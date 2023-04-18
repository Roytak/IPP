"""
IPP - Project 2
Author: Roman Janota
Date: 16-04-2023
"""

import sys
from enum import Enum


# enum for exit codes
class Status(Enum):
    OK = 0
    MISSING_PARAM_ERR = 10
    INPUT_FILE_ERR = 11
    OUTPUT_FILE_ERR = 12
    MALFORMED_ERR = 31
    INVALID_XML_ERR = 32
    SEMTANTIC_ERR = 52
    MISMATCHED_TYPES_ERR = 53
    VAR_NOT_EXIST_ERR = 54
    FRAME_NOT_EXIST_ERR = 55
    MISSING_VALUE_ERR = 56
    VALUE_ERR = 57
    STRING_ERR = 58
    INTERNAL_ERR = 99


# prints the message and terminates the program with the status value
def exit_program(status, msg):
    if msg is not None:
        print(msg, file=sys.stderr)
    exit(status.value)
