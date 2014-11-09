#!/usr/bin/python3
# coding=utf-8
"""

"""
from collections import namedtuple
import os

__author__ = "Michael Krisper"
__email__ = "michael.krisper@gmail.com"
__date__ = "2014-11-09"


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
    Flags = namedtuple("Flags", "unsynchronisation extended_header experimental_header footer_present")

    def __init__(self, header):
        self.file_identifier = header[:3]
        self.version = ID3v2Header.Version(header[3], header[4])
        flags = int.from_bytes(header[5], byteorder="big")
        self.flags = ID3v2Header.Flags(bool(flags & 1 << 7), bool(flags & 1 << 6), bool(flags & 1 << 5),
                                       bool(flags & 1 << 4))
        self.size = int.from_bytes(header[6:], byteorder="big")


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
        self.header = None
        self.tag = None

        self.extended_header = None
        self.frames = None
        self.padding = None
        self.footer = None

        self.extended_header_size = 0
        self.number_flag_bytes = 0
        self.extended_flags = 0
        self.crc_data = 0
        self.restrictions = 0
        if filename:
            self.from_file(filename)


    def from_file(self, filename):
        f = open(filename, "rb")
        self.header = f.read(10)
        self.tag = f.read(self.header_size)

        if self.flags_extended_header:
            self.extended_header_size = int.from_bytes(f.read(4), byteorder="big")
            self.extended_header = f.read(self.extended_header_size)

            self.number_flag_bytes = f.read()
            self.extended_flags = int.from_bytes(f.read(), byteorder="big")
            if self.ex_flags_tag_is_update:
                f.seek(1, 1)

            if self.ex_flags_crc_data_present:
                f.seek(1, 1)
                self.crc_data = int.from_bytes(f.read(5), byteorder="big")

            if self.ex_flags_tag_restrictions:
                f.seek(1, 1)
                self.restrictions = int.from_bytes(f.read(), byteorder="big")

        frame_id = f.read(4)
        frames = {}
        while frame_id != b"\x00\x00\x00\x00" and frame_id != b"'+\x99U" and frame_id[0] != 0xFF:
            size = int.from_bytes(f.read(4), byteorder="big")
            flags = f.read(2)
            content = f.read(size)
            if content[0] == 3:
                content = content[1:-1].decode()
            elif content[0] == 0:
                content = content[1:-1].decode("ISO-8859-1")
            elif content[0] == 1:
                content = content[1:-2].decode("utf-16le")
            elif content[0] == 2:
                content = content[1:-2].decode("utf-16")
            frames[frame_id.decode()] = content
            frame_id = f.read(4)
        try:
            print("{TPE1} - {TIT2}".format(**frames))
        except KeyError as e:
            print(e)
            print(frames)


    @property
    def ex_flags_tag_is_update(self):
        return self.extended_flags & 1 << 7

    @property
    def ex_flags_crc_data_present(self):
        return self.extended_flags & 1 << 6

    @property
    def ex_flags_tag_restrictions(self):
        return self.extended_flags & 1 << 5


def main():
    for dirpath, dirnames, filenames in os.walk("/Users/michi/Music"):
        for filename in filenames:
            if os.path.splitext(filename)[1] == ".mp3":
                fullpath = os.path.join(dirpath, filename)
                try:
                    id3 = ID3Tag(fullpath)
                except UnicodeDecodeError as e:
                    print(e)
                except OSError as e:
                    print(e)
                except IndexError as e:
                    print(e)


if __name__ == "__main__":
    main()