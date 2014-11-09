#!/usr/bin/python3
# coding=utf-8
"""
Script for reading ID3v2 Tags in MP3-Files.
"""
from collections import namedtuple
import io
import os

__author__ = "Michael Krisper"
__email__ = "michael.krisper@gmail.com"
__date__ = "2014-11-09"


def unsync(iterable):
    return sum(item << (7 * (len(iterable) - i)) for i, item in enumerate(iterable, start=1))


class ID3v2Flags:
    def __init__(self, flags):
        self._data = flags
        self.unsynchronisation = bool(self._data & 1 << 7)
        self.extended_header = bool(self._data & 1 << 6)
        self.experimental_header = bool(self._data & 1 << 5)
        self.footer_present = bool(self._data & 1 << 4)

    def __str__(self):
        return "{0.unsynchronisation}, {0.extended_header}, {0.experimental_header}, {0.footer_present}".format(self)


class ID3v2Header:
    """
    @see http://id3.org/id3v2.4.0-structure

    ID3v2 header

     ID3v2/file identifier      "ID3"
     ID3v2 version              $04 00
     ID3v2 flags                %abcd0000
     ID3v2 size             4 * %0xxxxxxx

    +-----------------+-------------------------+
    | file_identifier | ID3                     |
    +-----------------+-------------------------+
    | version         | 0xAA 0xBB               |
    |                 |  AA: major              |
    |                 |  BB: minor              |
    +-----------------+-------------------------+
    | flags           | 0bABCD0000              |
    |                 |  A: unsynchronisation   |
    |                 |  B: extended_header     |
    |                 |  C: experimental_header |
    |                 |  D: footer_present      |
    +-----------------+-------------------------+
    | size            | 0xAA 0xBB 0xCC 0xDD     |
    +-----------------+-------------------------+

    The first three bytes of the tag are always "ID3", to indicate that
    this is an ID3v2 tag, directly followed by the two version bytes. The
    first byte of ID3v2 version is its major version, while the second
    byte is its revision number. In this case this is ID3v2.4.0. All
    revisions are backwards compatible while major versions are not. If
    software with ID3v2.4.0 and below support should encounter version
    five or higher it should simply ignore the whole tag. Version or
    revision will never be $FF.
    The version is followed by the ID3v2 flags field, of which currently
    four flags are used.

    a - Unsynchronisation
     Bit 7 in the 'ID3v2 flags' indicates whether or not
     unsynchronisation is applied on all frames (see section 6.1 for
     details); a set bit indicates usage.

    b - Extended header
     The second bit (bit 6) indicates whether or not the header is
     followed by an extended header. The extended header is described in
     section 3.2. A set bit indicates the presence of an extended
     header.

    c - Experimental indicator
     The third bit (bit 5) is used as an 'experimental indicator'. This
     flag SHALL always be set when the tag is in an experimental stage.

    d - Footer present
     Bit 4 indicates that a footer (section 3.4) is present at the very
     end of the tag. A set bit indicates the presence of a footer.

    The ID3v2 tag size is the sum of the byte length of the extended
    header, the padding and the frames after unsynchronisation. If a
    footer is present this equals to ('total size' - 20) bytes, otherwise
    ('total size' - 10) bytes.
    """

    Version = namedtuple("Version", "major minor")

    def __init__(self, header):
        self._data = header

        self.file_identifier = self._data[:3]
        self.version = ID3v2Header.Version(self._data[3], self._data[4])
        flags = self._data[5]
        self.flags = ID3v2Flags(self._data[5])
        self.size = unsync(self._data[6:10])

    def __str__(self):
        return "{0.file_identifier}, {0.version}, {0.flags}, {0.size}".format(self)

    def __repr__(self):
        return str(self._data)


class ID3v2ExtendedFlags:
    def __init__(self, flags):
        self._data = flags

        self.tag_is_update = bool(self._data & 1 << 7)
        self.crc_data_present = bool(self._data & 1 << 6)
        self.tag_restriction = bool(self._data & 1 << 5)


class ID3v2ExtendedHeader:
    def __init__(self, extended_header, size):
        self._data = extended_header
        self.size = size

        f = io.BytesIO(self._data)

        self.number_flag_bytes = f.read(1)
        self.extended_flags = ID3v2ExtendedFlags(f.read(1))
        if self.extended_flags.tag_is_update:
            f.seek(1, 1)

        if self.extended_flags.crc_data_present:
            f.seek(1, 1)
            self.crc_data = unsync(f.read(5))

        if self.extended_flags.tag_restriction:
            f.seek(1, 1)
            self.restrictions = f.read(1)

    def __str__(self):
        return "{0.tag_is_update}, {0.crc_data_present}, {0.tag_restriction}".format(self)


class ID3Tag:
    """
    http://id3.org/id3v2.4.0-structure
    +--------+-----------------------------+
    | header |      Header (10 bytes)      |
    +--------+-----------------------------+
    |        |       Extended Header       |
    |        | (variable length, OPTIONAL) |
    |        +-----------------------------+
    |        |   Frames (variable length)  |
    |  tag   +-----------------------------+
    |        |           Padding           |
    |        | (variable length, OPTIONAL) |
    |        +-----------------------------+
    |        | Footer (10 bytes, OPTIONAL) |
    +--------+-----------------------------+
    """

    def __init__(self, filename=None):
        self.filename = filename
        self.header = None

        self.extended_header = None
        self.frames = {}
        self.padding = None
        self.footer = None

        self.extended_header_size = 0
        self.number_flag_bytes = 0
        self.extended_flags = 0
        self.crc_data = 0
        self.restrictions = 0

        with open(self.filename, "rb") as f_in:
            self.header = ID3v2Header(f_in.read(10))
            f = io.BytesIO(f_in.read(self.header.size))

        if self.header.flags.extended_header:
            size = unsync(f.read(4))
            self.extended_header = ID3v2ExtendedHeader(f.read(self.extended_header_size), size)

        frame_id = f.read(4)
        while frame_id and frame_id != b"\x00\x00\x00\x00":
            size = unsync(f.read(4))
            flags = f.read(2)
            content = f.read(size)
            if frame_id in [b"TIT2", b"TPE1"]:
                encoding, content = content[0], content[1:]
                try:
                    if encoding == 0:
                        content = content.decode("ISO-8859-1")
                    elif encoding == 1:
                        content = content.decode("utf-16le")
                    elif encoding == 2:
                        content = content.decode("utf-16")
                    elif encoding == 3:
                        content = content.decode("utf-8")
                except UnicodeDecodeError as e:
                    print("{}: {}".format(frame_id, e))
                self.frames[frame_id.decode("ISO-8859-1")] = content

            frame_id = f.read(4)


    def __str__(self):
        if "TPE1" in self.frames and "TIT2" in self.frames:
            return "{0[TPE1]} - {0[TIT2]}".format(self.frames)
        else:
            return "{0.filename}".format(self)

def main():
    for dirpath, dirnames, filenames in os.walk("/Users/michi/Music"):
        for filename in filenames:
            if os.path.splitext(filename)[1] == ".mp3":
                fullpath = os.path.join(dirpath, filename)
                id3 = ID3Tag(fullpath)
                print(id3)


if __name__ == "__main__":
    main()