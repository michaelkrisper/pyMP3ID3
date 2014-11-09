#!/usr/bin/python3
# coding=utf-8
"""

"""
import os

__author__ = "Michael Krisper"
__email__ = "michael.krisper@gmail.com"


def read_id3(filename):
    with open(filename, "rb") as f:

        header = f.read(10)
        file_identifier = header[:3]
        version = header[3:5]
        flags = int.from_bytes(header[5:6], byteorder="big")
        flags_unsynchronisation = flags & 1 << 7
        flags_extended_header = flags & 1 << 6
        flags_experimental_header = flags & 1 << 5
        flags_footer_present = flags & 1 << 4
        header_size = int.from_bytes(header[6:], byteorder="big")

        extended_header = None
        if flags_extended_header:
            extended_header_size = int.from_bytes(f.read(4), byteorder="big")
            number_flag_bytes = f.read(1)
            extended_flags = int.from_bytes(f.read(1), byteorder="big")
            ex_flags_tag_is_update = extended_flags & 1 << 7
            if ex_flags_tag_is_update:
                _ = f.read(1)

            ex_flags_crc_data_present = extended_flags & 1 << 6
            if ex_flags_crc_data_present:
                _ = f.read(1)
                crc_data = int.from_bytes(f.read(5), byteorder="big")

            ex_flags_tag_restrictions = extended_flags & 1 << 5
            _ = f.read(1)
            restrictions = int.from_bytes(f.read(1), byteorder="big")

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
        #return frames
        try:
            print("{TPE1} - {TIT2}".format(**frames))
        except KeyError as e:
            print(e)
            print(frames)


def main():
    for dirpath, dirnames, filenames in os.walk("/Users/michi/Music"):
        for filename in filenames:
            if os.path.splitext(filename)[1] == ".mp3":
                fullpath = os.path.join(dirpath, filename)
                try:
                    read_id3(fullpath)
                except UnicodeDecodeError as e:
                    print(e)
                except OSError as e:
                    print(e)
                except IndexError as e:
                    print(e)

if __name__ == "__main__":
    main()