"""
IPP - Project 2
Author: Roman Janota
Date: 16-04-2023
"""

from status import *
from frame import *
from collections import deque
import re
import ast

"""
Instruction objects represent XML instruction elements.
They depend on sharing their static class variables with each other.
The class contains various methods for validation and execution of the instructions.
"""


class Instruction:
    GF = Frame()  # Global frame
    TF = None  # Temporary frame
    LF = deque()  # Local frame stack
    stack = deque()  # IPPcode23 instruction's stack
    inputs = deque()  # Inputs queue
    labels = {}  # Labels dictionary
    call_stack = deque()  # Function call stack

    def __init__(self, tree, file):
        self.order = int(tree.attrib["order"])  # instruction element's order
        self.opcode = tree.attrib["opcode"].upper()  # instruction element's opcode
        self.op1 = ""  # instruction element's arg1 value
        self.op1_type = ""  # instruction element's arg1 type
        self.op2 = ""  # instruction element's arg2 value
        self.op2_type = ""  # instruction element's arg2 type
        self.op3 = ""  # instruction element's arg3 value
        self.op3_type = ""  # instruction element's arg3 type
        self.in_file = file  # file with inputs for IPPcode23 instructions
        self._fill_input(file)  # fill the inputs queue if possible

    # fills the labels dictionary
    def create_labels(self):
        if self.opcode == "LABEL":
            for label in self.labels.keys():
                if self.op1 == label:
                    exit_program(
                        Status.SEMTANTIC_ERR,
                        "Attempted to create two labels with same name.",
                    )

            self.labels[self.op1] = int(self.order) + 1

    # fills the inputs queue if possible
    def _fill_input(self, file):
        if file != sys.stdin:
            with open(file) as f:
                lines = f.readlines()
            for line in lines:
                self.inputs.append(line.strip())
            f.close()

    # gets the frame of a variable
    def _get_frame(self, var):
        if var.find("GF@") != -1:
            return self.GF
        elif var.find("TF@") != -1:
            if self.TF is None:
                exit_program(
                    Status.FRAME_NOT_EXIST_ERR,
                    "Attempted to access a temporary frame without creating it first.",
                )
            return self.TF
        elif var.find("LF@") != -1:
            if len(self.LF) == 0:
                exit_program(
                    Status.FRAME_NOT_EXIST_ERR,
                    "Attempted to access a local frame without creating it first.",
                )
            return self.LF[0]
        else:
            exit_program(
                Status.INVALID_XML_ERR, "Expected frame name in variable name."
            )

    # checks if a symbol is a variable
    def _is_var(self, name):
        if name is None:
            return False

        name = str(name)
        if name.find("F@") != -1:
            return True
        return False

    # arithmetic instructions arguments checks
    def _check_arithmetic_args(
        self, arg1_type, arg1_val, arg2_type, arg2_val, instruction
    ):
        if (arg1_type is None and arg1_val is None) or (
            arg2_type is None and arg2_val is None
        ):
            exit_program(Status.MISSING_VALUE_ERR, f"Var not set in {instruction}.")

        if arg1_type != "int" or arg2_type != "int":
            exit_program(
                Status.MISMATCHED_TYPES_ERR,
                f"Expected two integer operands in {instruction} instruction.",
            )

    # logical instructions arguments checks
    def _check_logical_args(
        self, arg1_type, arg1_val, arg2_type, arg2_val, instruction
    ):
        if (arg1_type is None and arg1_val is None) or (
            instruction != "NOT" and arg2_type is None and arg2_val is None
        ):
            exit_program(Status.MISSING_VALUE_ERR, f"Var not set in {instruction}.")

        if arg1_type != "bool" or (
            instruction != "NOT" and arg2_type is not None and arg2_type != "bool"
        ):
            exit_program(
                Status.MISMATCHED_TYPES_ERR,
                f"Expected two boolean operands in {instruction} instruction.",
            )

    # relation instructions arguments checks
    def _check_relation_args(
        self, arg1_type, arg1_val, arg2_type, arg2_val, instruction
    ):
        if (arg1_type is None and arg1_val is None) or (
            arg2_type is None and arg2_val is None
        ):
            exit_program(Status.MISSING_VALUE_ERR, f"Var not set in {instruction}.")

        if arg1_type != arg2_type:
            exit_program(
                Status.MISMATCHED_TYPES_ERR,
                f"Expected same types of operands in {instruction} instruction.",
            )

        if instruction != "EQ":
            if arg1_type == "nil" or arg2_type == "nil":
                exit_program(Status.MISMATCHED_TYPES_ERR, "Nil as operand in LT.")

    # flow control instructions arguments checks
    def _check_jump_args(self, arg1_type, arg1_val, arg2_type, arg2_val, instruction):
        if (arg1_type is None and arg1_val is None) or (
            arg2_type is None and arg2_val is None
        ):
            exit_program(Status.MISSING_VALUE_ERR, f"Var not set in {instruction}.")

        if arg1_type != arg2_type and arg1_type != "nil" and arg2_type != "nil":
            exit_program(Status.MISMATCHED_TYPES_ERR, f"Wrong types in {instruction}")

        if self.op1 not in self.labels:
            exit_program(Status.SEMTANTIC_ERR, f"Label {self.op1} not defined.")

    # gets symbols types and values
    def _get_frame_value_types(self, sym1, sym1_type, sym2, sym2_type):
        if self._is_var(sym1):
            frame1 = self._get_frame(sym1)
            value1 = frame1.get_value(sym1)
            type1 = frame1.get_type(sym1)
        else:
            value1 = sym1
            type1 = sym1_type

        if self._is_var(sym2):
            frame2 = self._get_frame(sym2)
            value2 = frame2.get_value(sym2)
            type2 = frame2.get_type(sym2)
        else:
            value2 = sym2
            type2 = sym2_type

        return value1, type1, value2, type2

    # The actual interpretation of IPPcode23 instruction set follows
    def _do_move(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, None, None
        )

        if value1 is None or type1 is None:
            exit_program(
                Status.MISSING_VALUE_ERR,
                f"Var {self.op2} has to be set before assingning.",
            )
        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, value1, type1)

    def _do_createframe(self):
        self.TF = Frame()

    def _do_pushframe(self):
        if self.TF is None:
            exit_program(
                Status.FRAME_NOT_EXIST_ERR, "Attempted to push an undefined frame."
            )

        frame = Frame()
        for var in self.TF.vars:
            # change TF variable names to LF
            old_name = var.find("@")
            new_name = "LF" + var[old_name:]
            frame.vars[new_name] = self.TF.vars[var]

        self.LF.appendleft(frame)
        self.TF = None

    def _do_popframe(self):
        if len(self.LF) == 0:
            exit_program(
                Status.FRAME_NOT_EXIST_ERR, "Unable to pop from empty LF stack."
            )

        new_frame = Frame()
        old_frame = self.LF.popleft()
        for var in old_frame.vars:
            # change LF variable names to TF
            old_name = var.find("@")
            new_name = "TF" + var[old_name:]
            new_frame.vars[new_name] = old_frame.vars[var]

        self.TF = new_frame

    def _do_defvar(self):
        frame = self._get_frame(self.op1)

        frame.insert_var(self.op1, None, None)

    def _do_call(self):
        self.call_stack.appendleft(int(self.order) + 1)

        return self._do_jump()

    def _do_return(self):
        if len(self.call_stack) == 0:
            exit_program(
                Status.MISSING_VALUE_ERR, "Tried to use RETURN without calling."
            )

        return int(self.call_stack.popleft())

    def _do_pushs(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op1, self.op1_type, None, None
        )

        if value1 is None or type1 is None:
            exit_program(
                Status.MISSING_VALUE_ERR, f"Variable {self.op1} not set in PUSHS."
            )

        self.stack.appendleft(Var(value1, type1))

    def _do_pops(self):
        if len(self.stack) == 0:
            exit_program(Status.MISSING_VALUE_ERR, "Unable to pop from empty stack.")

        symbol = self.stack.popleft()
        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, symbol.value, symbol.var_type)

    def _do_add(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        self._check_arithmetic_args(type1, value1, type2, value2, "ADD")

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, int(value1) + int(value2), "int")

    def _do_mul(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        self._check_arithmetic_args(type1, value1, type2, value2, "MUL")

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, int(value1) * int(value2), "int")

    def _do_sub(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        self._check_arithmetic_args(type1, value1, type2, value2, "SUB")

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, int(value1) - int(value2), "int")

    def _do_idiv(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        self._check_arithmetic_args(type1, value1, type2, value2, "IDIV")

        if int(value2) == 0:
            exit_program(Status.VALUE_ERR, "Division by 0 attempted.")

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, int(value1) // int(value2), "int")

    def _do_lt(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        self._check_relation_args(type1, value1, type2, value2, "LT")

        if type1 == "int":
            if int(value1) < int(value2):
                ret = "true"
            else:
                ret = "false"
        elif type1 == "string":
            if str(value1) < str(value2):
                ret = "true"
            else:
                ret = "false"
        elif type1 == "bool":
            if value1 == "false" and value1 != value2:
                ret = "true"
            else:
                ret = "false"

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, ret, "bool")

    def _do_gt(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        self._check_relation_args(type1, value1, type2, value2, "GT")

        if type1 == "int":
            if int(value1) > int(value2):
                ret = "true"
            else:
                ret = "false"
        elif type1 == "string":
            if str(value1) > str(value2):
                ret = "true"
            else:
                ret = "false"
        elif type1 == "bool":
            if value1 == "true" and value1 != value2:
                ret = "true"
            else:
                ret = "false"

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, ret, "bool")

    def _do_eq(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        self._check_relation_args(type1, value1, type2, value2, "EQ")

        if type1 == "int":
            if int(value1) == int(value2):
                ret = "true"
            else:
                ret = "false"
        elif type1 == "string":
            if str(value1) == str(value2):
                ret = "true"
            else:
                ret = "false"
        elif type1 == "bool":
            if value1 == value2:
                ret = "true"
            else:
                ret = "false"

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, ret, "bool")

    def _do_and(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        self._check_logical_args(type1, value1, type2, value2, "AND")

        if value1 == "true" and value2 == "true":
            ret = "true"
        else:
            ret = "false"

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, ret, "bool")

    def _do_or(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        self._check_logical_args(type1, value1, type2, value2, "OR")

        if value1 == "true" or value2 == "true":
            ret = "true"
        else:
            ret = "false"

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, ret, "bool")

    def _do_not(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, None, None
        )

        self._check_logical_args(type1, value1, None, None, "NOT")

        if value1 == "true":
            ret = "false"
        else:
            ret = "true"

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, ret, "bool")

    def _do_int2char(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, None, None
        )

        if value1 is None and type1 is None:
            exit_program(
                Status.MISSING_VALUE_ERR, f"Variable {self.op2} not set in INT2CHAR."
            )

        if type1 != "int":
            exit_program(Status.MISMATCHED_TYPES_ERR, "Expected valid type in INT2CHAR")

        try:
            ret = chr(int(value1))
        except:
            exit_program(Status.STRING_ERR, "Expected valid value in INT2CHAR")

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, ret, "string")

    def _do_stri2int(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        if (value1 is None and type1 is None) or (value2 is None and type2 is None):
            exit_program(
                Status.MISSING_VALUE_ERR, f"Variable {self.op2} not set in STRI2INT."
            )

        if type1 != "string" or type2 != "int":
            exit_program(Status.MISMATCHED_TYPES_ERR, "Expected valid type in STRI2INT")

        if int(value2) < 0 or int(value2) > len(value1):
            exit_program(Status.STRING_ERR, "Invalid length in STRI2INT")

        try:
            ret = ord(str(value1[int(value2)]))
        except:
            exit_program(Status.STRING_ERR, "Expected valid value in STRI2INT")

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, ret, "int")

    def _do_read(self):
        if self.in_file != sys.stdin:
            # read from queue if command line arg was specified
            if len(self.inputs) == 0:
                read = "nil"
            else:
                read = self.inputs.popleft()
        else:
            read = input()

        if self.op2 == "int":
            try:
                value = int(read)
            except:
                read = "nil"
            type1 = "int"
        elif self.op2 == "bool":
            if read.lower() == "true":
                value = "true"
            else:
                value = "false"
            type1 = "bool"
        else:
            value = str(read)
            type1 = "string"

        if read == "nil":
            value = "nil"
            type1 = "nil"

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, value, type1)

    def _do_write(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op1, self.op1_type, None, None
        )

        if value1 is None:
            exit_program(
                Status.MISSING_VALUE_ERR,
                f"Can not write an uninitialized symbol {self.op1}",
            )

        if str(type1).find("nil") != -1:
            value1 = ""

        print(value1, end="")

    def _do_concat(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        if (type1 is None and value1 is None) or (type2 is None and value2 is None):
            exit_program(Status.MISSING_VALUE_ERR, "Var not set in CONCAT.")

        if type1 != "string" or type2 != "string":
            exit_program(
                Status.MISMATCHED_TYPES_ERR, "Only string types allowed in CONCAT."
            )

        if value1 is None and value2 is None:
            ret = ""
        elif value2 is None:
            ret = value1
        elif value1 is None:
            ret = value2
        else:
            ret = value1 + value2

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, ret, "string")

    def _do_strlen(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, None, None
        )

        if value1 is None and type1 is None:
            exit_program(Status.MISSING_VALUE_ERR, "Missing value in STRLEN.")

        if type1 != "string":
            exit_program(
                Status.MISMATCHED_TYPES_ERR, "Only string types allowed in STRLEN."
            )

        if value1 is None:
            length = 0
        else:
            length = len(value1)

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, length, "int")

    def _do_getchar(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        if (type1 is None and value1 is None) or (type2 is None and value2 is None):
            exit_program(Status.MISSING_VALUE_ERR, "Var not set in GETCHAR.")

        if type1 != "string" or type2 != "int":
            exit_program(
                Status.MISMATCHED_TYPES_ERR, "Only string types allowed in GETCHAR."
            )

        if int(value2) >= len(value1) or int(value2) < 0:
            exit_program(Status.STRING_ERR, "Bad value in GETCHAR.")

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, value1[int(value2)], "string")

    def _do_setchar(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        if (type1 is None and value1 is None) or (type2 is None and value2 is None):
            exit_program(Status.MISSING_VALUE_ERR, "Var not set in GETCHAR.")

        frame = self._get_frame(self.op1)
        value = frame.get_value(self.op1)
        Type = frame.get_type(self.op1)

        if type1 != "int" or type2 != "string" or Type != "string":
            exit_program(
                Status.MISMATCHED_TYPES_ERR, "Only string types allowed in SETCHAR."
            )

        if int(value1) < 0 or int(value1) >= len(value):
            exit_program(Status.STRING_ERR, "Bad value in SETCHAR.")

        if len(value2) > 1:
            new_value = value[: int(value1)] + value2[0] + value[int(value1) + 1 :]
        else:
            new_value = value[: int(value1)] + value2 + value[int(value1) + 1 :]

        frame.set_value(self.op1, new_value, "string")

    def _do_type(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, None, None
        )

        if type1 is None:
            type1 = ""

        frame = self._get_frame(self.op1)
        frame.set_value(self.op1, type1, "string")

    def _do_jump(self):
        for label in self.labels:
            if label == self.op1:
                return self.labels[label]

        exit_program(Status.SEMTANTIC_ERR, "Attempted to jump to a non existant label.")

    def _do_jumpifeq(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        self._check_jump_args(type1, value1, type2, value2, "JUMPIFEQ")

        ret = False
        if type1 == "int" and type2 == "int":
            if int(value1) == int(value2):
                ret = True
        elif type1 == "string" or type1 == "bool" or value1 == "nil":
            if value1 == value2:
                ret = True

        if ret is True:
            return self._do_jump()
        else:
            return self.order + 1

    def _do_jumpifneq(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, self.op3, self.op3_type
        )

        self._check_jump_args(type1, value1, type2, value2, "JUMPIFNEQ")

        ret = False
        if type1 == "int" and type2 == "int":
            if int(value1) == int(value2):
                ret = True
        elif type1 == "string" or type1 == "bool" or value1 == "nil":
            if value1 == value2:
                ret = True

        if ret is False:
            return self._do_jump()
        else:
            return self.order + 1

    def _do_exit(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op1, self.op1_type, None, None
        )

        if type1 is None and value1 is None:
            exit_program(Status.MISSING_VALUE_ERR, "Variable not set in EXIT.")

        if type1 != "int":
            exit_program(Status.MISMATCHED_TYPES_ERR, "Expected integer value in EXIT.")

        if int(value1) < 0 or int(value1) > 49:
            exit_program(Status.VALUE_ERR, "Invalid EXIT value.")

        sys.exit(int(value1))

    def _do_dprint(self):
        value1, type1, value2, type2 = self._get_frame_value_types(
            self.op2, self.op2_type, None, None
        )

        print(value1, file=sys.stderr)

    # calls the corresponding function based on the opcode and returns the next order
    def execute(self):
        order = 0

        if self.opcode == "MOVE":
            self._do_move()
        elif self.opcode == "CREATEFRAME":
            self._do_createframe()
        elif self.opcode == "PUSHFRAME":
            self._do_pushframe()
        elif self.opcode == "POPFRAME":
            self._do_popframe()
        elif self.opcode == "DEFVAR":
            self._do_defvar()
        elif self.opcode == "CALL":
            order = self._do_call()
        elif self.opcode == "RETURN":
            order = self._do_return()
        elif self.opcode == "PUSHS":
            self._do_pushs()
        elif self.opcode == "POPS":
            self._do_pops()
        elif self.opcode == "ADD":
            self._do_add()
        elif self.opcode == "MUL":
            self._do_mul()
        elif self.opcode == "SUB":
            self._do_sub()
        elif self.opcode == "IDIV":
            self._do_idiv()
        elif self.opcode == "LT":
            self._do_lt()
        elif self.opcode == "GT":
            self._do_gt()
        elif self.opcode == "EQ":
            self._do_eq()
        elif self.opcode == "AND":
            self._do_and()
        elif self.opcode == "OR":
            self._do_or()
        elif self.opcode == "NOT":
            self._do_not()
        elif self.opcode == "INT2CHAR":
            self._do_int2char()
        elif self.opcode == "STRI2INT":
            self._do_stri2int()
        elif self.opcode == "READ":
            self._do_read()
        elif self.opcode == "WRITE":
            self._do_write()
        elif self.opcode == "CONCAT":
            self._do_concat()
        elif self.opcode == "STRLEN":
            self._do_strlen()
        elif self.opcode == "GETCHAR":
            self._do_getchar()
        elif self.opcode == "SETCHAR":
            self._do_setchar()
        elif self.opcode == "TYPE":
            self._do_type()
        elif self.opcode == "LABEL":
            pass
        elif self.opcode == "JUMP":
            order = self._do_jump()
        elif self.opcode == "JUMPIFEQ":
            order = self._do_jumpifeq()
        elif self.opcode == "JUMPIFNEQ":
            order = self._do_jumpifneq()
        elif self.opcode == "EXIT":
            self._do_exit()
        elif self.opcode == "DPRINT":
            self._do_dprint()

        if order == 0:
            return self.order + 1
        else:
            return order

    # validates the instruction, it's argument count and types if possible
    def validate(self, tree):
        if self.opcode == "MOVE":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "CREATEFRAME":
            pass
        elif self.opcode == "PUSHFRAME":
            pass
        elif self.opcode == "POPFRAME":
            pass
        elif self.opcode == "DEFVAR":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "CALL":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "label":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "RETURN":
            pass
        elif self.opcode == "PUSHS":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] != "label":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "POPS":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "ADD":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "SUB":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "MUL":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "IDIV":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "LT":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "GT":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "EQ":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "AND":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "OR":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "NOT":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "INT2CHAR":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "STRI2INT":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "READ":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] == "type":
                    if (
                        element.text != "int"
                        and element.text != "string"
                        and element.text != "bool"
                    ):
                        exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "WRITE":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] != "label":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "CONCAT":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "STRLEN":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "GETCHAR":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "SETCHAR":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "TYPE":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "var":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "LABEL":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "label":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "JUMP":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "label":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "JUMPIFEQ":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "label":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "JUMPIFNEQ":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] == "label":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                elif element.tag == "arg2" and element.attrib["type"] != "label":
                    self.op2 = element.text
                    self.op2_type = element.attrib["type"]
                elif element.tag == "arg3" and element.attrib["type"] != "label":
                    self.op3 = element.text
                    self.op3_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "EXIT":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] != "label":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "DPRINT":
            for element in tree:
                if element.tag == "arg1" and element.attrib["type"] != "label":
                    self.op1 = element.text
                    self.op1_type = element.attrib["type"]
                else:
                    exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
        elif self.opcode == "BREAK":
            pass
        else:
            exit_program(Status.INVALID_XML_ERR, "Unexpected opcode.")
