# PCK-PY by NDRAEY [2023]

import struct
import os
import sys
from dataclasses import dataclass

@dataclass
class FileInfo:
    ident: int
    name: str
    lang: str
    offset: int
    size: int

if not sys.argv[1:]:
    print("Not enough arguments!")
    exit(1)

filename = sys.argv[1]

file = open(filename, "rb")

ident = struct.unpack("<4s", file.read(4))[0]

file.seek(8)

endianness = struct.unpack("<1b", file.read(1))[0]
endianness = ">" if not endianness else "<"

print(ident)
print(endianness)

file.seek(4)

def read_uint() -> int:
    global endianness
    global file
    
    data = struct.unpack(
            endianness + "I",
            file.read(4)
           )

    return data[0]

def read_ull() -> int:
    global endianness
    global file
    
    data = struct.unpack(
            endianness + "Q",
            file.read(8)
           )

    return data[0]

header_size = read_uint()
flags = read_uint()

section1_size = read_uint()
section2_size = read_uint()
section3_size = read_uint()
section4_size = 0

print("HEADER SIZE", header_size)
print("FLAGS", flags)

print("1:", section1_size)
print("2:", section2_size)
print("3:", section3_size)

checksum = section1_size + section2_size + section3_size + 16

version = 1 if checksum == header_size else 2

print("Detected version:", version)

if version == 2:
    section4_size = read_uint()
    
    print("4:", section4_size)

section1_offset = file.tell()
section2_offset = section1_offset + section1_size

def parse_languages() -> list[(int, str)]:
    global file

    count = read_uint()

    print("Languages:", count)

    languages = []

    for i in range(count):
        name_offset = read_uint()
        ident = read_uint()

        old_pos = file.tell()

        file.seek(name_offset + section1_offset)

        name = b""

        while True:
            byte = file.read(1)

            if byte == b'\x00':
                break

            name += byte

        name = name.decode("utf-8")

        languages.append((ident, name))

        print(f"|- Language: [{ident}] {name}")

        file.seek(old_pos)

    return languages

def parse_files(languages: list[(int, str)], extension: str) -> list[FileInfo]:
    global file

    count = read_uint()

    print("File count:", count)

    files = []

    for i in range(count):
        ident = read_uint()
        mult = read_uint()

        size = read_ull() if version == 1 else read_uint()

        offset = read_uint()
        lang_index = read_uint()

        if mult:
            offset *= mult

        name = f"{languages[lang_index][0]}_{ident}.{extension}"

        print(f"File: [{ident:6}] {name:20} {lang_index:2} {hex(offset):8} {size} bytes")            

        files.append(
            FileInfo(
                ident,
                name,
                languages[lang_index][0],
                offset,
                size
            )
        )

    return files

languages = parse_languages()

file.seek(section2_offset)

print("Parsing section 2...")

print("Parsing banks...")
banks = parse_files(languages, "bnk")

print("Parsing sounds...")
wems = parse_files(languages, "wem")

# Extract
def extract(files: list[FileInfo], directory: str):
    global file

    length = len(files)

    if not os.path.isdir(directory):
        os.mkdir(directory)

    for i in range(length):
        percentage = (i / length) * 100

        myfile = files[i]
        
        print(f"\033[K\r{percentage:.3}% {myfile.name}", end='')

        file.seek(myfile.offset)

        data = file.read(myfile.size)

        with open(directory + "/" + myfile.name, "wb") as output:
            output.write(data)
            output.close()
        
    print(f"\r100%\033[K")
    print()

print("Extracting banks...")
extract(banks, "banks")

print("Extracting sounds...")
extract(wems, "sounds")
