"""
IPP - Project 2
Author: Roman Janota
Date: 16-04-2023
"""

from dataclasses import dataclass
from status import *


# a wrapper around variable value and type pair
@dataclass
class Var:
    value: str = ""
    var_type: str = ""


class Frame:
    def __init__(self):
        self.vars = {}

    # inserts the variable into the frames variable storage
    def insert_var(self, name, value, var_type):
        for key in self.vars.keys():
            if key == name:
                exit_program(Status.SEMTANTIC_ERR, "Variable already exists")
        self.vars[name] = Var(value, var_type)

    # sets the variable's new value and type
    def set_value(self, dest, src, src_type):
        if dest not in self.vars:
            exit_program(Status.VAR_NOT_EXIST_ERR, f"Variable {dest} not defined.")

        if src_type is None:
            src_type = self.get_type(src)

        if str(src).find("F@") != -1:
            self.vars[dest] = Var(src[src.find("@") + 1 :], src_type)
        else:
            self.vars[dest] = Var(src, src_type)

    # gets variable's value
    def get_value(self, name):
        if name not in self.vars:
            exit_program(Status.VAR_NOT_EXIST_ERR, f"Variable {name} not defined.")
        return self.vars[name].value

    # gets variable's type
    def get_type(self, name):
        if name not in self.vars:
            exit_program(Status.VAR_NOT_EXIST_ERR, f"Variable {name} not defined.")
        return self.vars[name].var_type
