import binascii
import string
from enum import Enum


class Logging_Level(Enum):
    ALL = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    CRITICAL = 5
    OFF = 6

LOG_LEVEL = Logging_Level.INFO
log_unpack = 1
log_repack = 1


def log(log_string, level=Logging_Level.INFO, packing_info=0, _end='\n'):
    """ prints a string to the console respecting logging level
    """
    if(level.value>=LOG_LEVEL.value):
        if((packing_info == 0) or (packing_info == 1 and log_unpack) or (packing_info == 2 and log_repack)):
            print(log_string, end = _end)
            #print("LOG: " + str(log_string), end = _end)

def set_LOG_LEVEL(level):
    if(type(level) is int):
        if(level>Logging_Level.OFF.value):
            print(f"[WARNING] LOG_LEVEL {level} out of range - Level set to OFF")
            LOG_LEVEL = Logging_Level.OFF
        elif(level<Logging_Level.ALL.value):
            print(f"[WARNING] LOG_LEVEL {level} out of range - Level set to ALL")
            LOG_LEVEL = Logging_Level.ALL
        else:
            LOG_LEVEL = Logging_Level(level)
    else:# is type Logging_level
        LOG_LEVEL = level

def convert_to_ascii_string(data):
    """ reads bytes from data and converts to string. 
    #   Stops at the first non printable byte
    """
    ascii_string = ""
    for char in data:
        char = chr(char)
        if char in string.printable and not char in "\r\n\t":
            ascii_string += char
        else:
            return ascii_string
    return ascii_string





""" These are based on Deces format.py """
def open_file(path):
    """ open the file specified in path """
    input_path = path
    try:
        with open(input_path, "rb") as input_file:
            data = input_file.read()
    except OSError as exc:
        print(f"Couldn't load {input_path}: {exc}")
        return
    return data

def save_file(data,path):
    """ save into the file specified in path """
    input_path = path
    try:
        with open(input_path, "xb") as input_file:
            input_file.write(data)
    except OSError as exc:
        print(f"Couldn't load {input_path}: {exc}")
        return
    return data


#used for formatting data
def get_data_dump(data):
    """ Return a pretty binary data representation in a Hexdump fashion. """
    dump = ""
    index = 0
    while index < len(data):
        data_slice = data[ index : index+16 ]
        offset_str = _get_offset_string(index)
        data_str = _get_hexdump_string(data_slice)
        ascii_str = _get_asciidump_string(data_slice)
        dump += "{} {:<47} {}\n".format(offset_str, data_str, ascii_str)
        index += 16
    return dump

def _get_offset_string(index):
    offset = hex(index)[2:]
    offset = offset.zfill(8)
    return offset

def _get_hexdump_string(data):
    hexdump = binascii.hexlify(data).decode("ascii")
    spaced_hexdump = ""
    index = 0
    while index < len(hexdump):
        spaced_hexdump += hexdump[ index : index+2 ] + " "
        index += 2
    return spaced_hexdump.strip()

def _get_asciidump_string(data):
    asciidump = ""
    for char in data:
        char = chr(char)
        if char in string.printable and not char in "\r\n\t":
            asciidump += char
        else:
            asciidump += "."
    return asciidump