from status import *
from frame import *
from collections import deque

class Instruction:
	GF = Frame()
	TF = None
	LF = deque()
	stack = deque()
	inputs = deque()
	labels = {}

	def __init__(self, tree, file):
		self.order = int(tree.attrib['order'])
		self.opcode = tree.attrib['opcode']
		self.op1 = ""
		self.op1_type = ""
		self.op2 = ""
		self.op2_type = ""
		self.op3 = ""
		self.op3_type = ""
		self.in_file = file
		self.fill_input(file)

	def create_labels(self):
		if self.opcode == "LABEL":
			for label in self.labels.keys():
				if self.op1 == label:
					exit_program(Status.SEMTANTIC_ERR, "Attempted to create two labels with same name.")

			self.labels[self.op1] = int(self.order) + 1

	def fill_input(self, file):
		if file != sys.stdin:
			with open(file) as f:
				lines = f.readlines()
			for line in lines:
				self.inputs.append(line.strip())
			f.close()

	def get_frame(self, var):
		if var.find('GF@') != -1:
			return self.GF
		elif var.find('TF@') != -1:
			return self.TF
		elif var.find('LF@') != -1:
			return self.LF
		else:
			exit_program(Status.INVALID_XML_ERR, "Expected frame name in variable name.")

	def is_var(self, name):
		name = str(name)
		if name.find('F@') != -1:
			return True
		return False

	def do_move(self):
		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, self.op2, self.op2_type)

	def do_createframe(self):
		self.TF = Frame()

	def do_pushframe(self):
		if self.TF is None:
			exit_program(Status.FRAME_NOT_EXIST_ERR, "Attempted to push an undefined frame.")

		self.LF.appendleft(self.TF)
		self.TF = None

	def do_popframe(self):
		if len(self.LF) == 0:
			exit_program(Status.FRAME_NOT_EXIST_ERR, "Unable to pop from empty LF stack.")

		self.TF = self.LF.popleft()

	def do_defvar(self):
		frame = self.get_frame(self.op1)
		frame.insert_var(self.op1, None, None)

	def do_pushs(self):
		if self.is_var(self.op1):
			frame = get_frame(self.op1)
			self.stack.appendleft(frame[self.op1])
		else:
			self.stack.appendleft(Var(self.op1, self.op1_type))

	def do_pops(self):
		if len(self.stack) == 0:
			exit_program(Status.MISSING_VALUE_ERR, "Unable to pop from empty stack.")

		symbol = self.stack.popleft()
		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, symbol.value, symbol.var_type)

	def do_add(self):
		if self.is_var(self.op2):
			frame1 = self.get_frame(self.op2)
			value1 = frame1.get_value(self.op2)
			type1 = frame1.get_type(self.op2)
		else:
			value1 = self.op2
			type1 = self.op2_type

		if self.is_var(self.op3):
			frame2 = self.get_frame(self.op3)
			value2 = frame2.get_value(self.op3)
			type2 = frame2.get_type(self.op3)
		else:
			value2 = self.op3
			type2 = self.op3_type

		if type1 != 'int' or type2 != 'int':
			exit_program(Status.MISMATCHED_TYPES_ERR, "Expected two integer operands in ADD instruction.")

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, int(value1) + int(value2), 'int')

	def do_mul(self):
		if self.is_var(self.op2):
			frame1 = self.get_frame(self.op2)
			value1 = frame1.get_value(self.op2)
			type1 = frame1.get_type(self.op2)
		else:
			value1 = self.op2
			type1 = self.op2_type

		if self.is_var(self.op3):
			frame2 = self.get_frame(self.op3)
			value2 = frame2.get_value(self.op3)
			type2 = frame2.get_type(self.op3)
		else:
			value2 = self.op3
			type2 = self.op3_type

		if type1 != 'int' or type2 != 'int':
			exit_program(Status.MISMATCHED_TYPES_ERR, "Expected two integer operands in ADD instruction.")

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, int(value1) * int(value2), 'int')

	def do_sub(self):
		if self.is_var(self.op2):
			frame1 = self.get_frame(self.op2)
			value1 = frame1.get_value(self.op2)
			type1 = frame1.get_type(self.op2)
		else:
			value1 = self.op2
			type1 = self.op2_type

		if self.is_var(self.op3):
			frame2 = self.get_frame(self.op3)
			value2 = frame2.get_value(self.op3)
			type2 = frame2.get_type(self.op3)
		else:
			value2 = self.op3
			type2 = self.op3_type

		if type1 != 'int' or type2 != 'int':
			exit_program(Status.MISMATCHED_TYPES_ERR, "Expected two integer operands in ADD instruction.")

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, int(value2) - int(value1), 'int')

	def do_idiv(self):
		if self.is_var(self.op2):
			frame1 = self.get_frame(self.op2)
			value1 = frame1.get_value(self.op2)
			type1 = frame1.get_type(self.op2)
		else:
			value1 = self.op2
			type1 = self.op2_type

		if self.is_var(self.op3):
			frame2 = self.get_frame(self.op3)
			value2 = frame2.get_value(self.op3)
			type2 = frame2.get_type(self.op3)
		else:
			value2 = self.op3
			type2 = self.op3_type

		if type1 != 'int' or type2 != 'int':
			exit_program(Status.MISMATCHED_TYPES_ERR, "Expected two integer operands in ADD instruction.")

		if int(value2) == 0:
			exit_program(Status.VALUE_ERR, "Division by 0 attempted.")

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, int(value2) // int(value1), 'int')

	def do_lt(self):
		if self.op2_type != self.op3_type:
			exit_program(Status.MISMATCHED_TYPES_ERR, "Expected same types in arithmetic operation")

		if self.op2 == "nil" or self.op3 == "nil":
			exit_program(Status.MISMATCHED_TYPES_ERR, "Nil as operand in LT.")

		if self.op2_type == "int":
			if int(self.op2) < int(self.op3):
				ret = "true"
			else:
				ret = "false"
		elif self.op2_type == "string":
			if str(self.op2) < str(self.op3):
				ret = "true"
			else:
				ret = "false"
		elif self.op2_type == "bool":
			if self.op2 == "false" and self.op2 != self.op3:
				ret = "true"
			else:
				ret = "false"

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, ret, "bool")

	def do_gt(self):
		if self.op2_type != self.op3_type:
			exit_program(Status.MISMATCHED_TYPES_ERR, "Expected same types in arithmetic operation")

		if self.op2 == "nil" or self.op3 == "nil":
			exit_program(Status.MISMATCHED_TYPES_ERR, "Nil as operand in GT.")

		if self.op2_type == "int":
			if int(self.op2) > int(self.op3):
				ret = "true"
			else:
				ret = "false"
		elif self.op2_type == "string":
			if str(self.op2) > str(self.op3):
				ret = "true"
			else:
				ret = "false"
		elif self.op2_type == "bool":
			if self.op2 == "true" and self.op2 != self.op3:
				ret = "true"
			else:
				ret = "false"

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, ret, "bool")

	def do_eq(self):
		if self.op2_type != self.op3_type:
			exit_program(Status.MISMATCHED_TYPES_ERR, "Expected same types in arithmetic operation")

		if self.op2_type == "int":
			if int(self.op2) == int(self.op3):
				ret = "true"
			else:
				ret = "false"
		elif self.op2_type == "string":
			if str(self.op2) == str(self.op3):
				ret = "true"
			else:
				ret = "false"
		elif self.op2_type == "bool":
			if self.op2 == self.op3:
				ret = "true"
			else:
				ret = "false"

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, ret, "bool")

	def do_and(self):
		if self.op2_type != "bool" or self.op3_type != "bool":
			exit_program(Status.MISMATCHED_TYPES_ERR, "Expected boolean types in AND.")

		if self.op2 == "true" and self.op3 == "true":
			ret = "true"
		else:
			ret = "false"

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, ret, "bool")

	def do_or(self):
		if self.op2_type != "bool" or self.op3_type != "bool":
			exit_program(Status.MISMATCHED_TYPES_ERR, "Expected boolean types in OR.")

		if self.op2 == "true" or self.op3 == "true":
			ret = "true"
		else:
			ret = "false"

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, ret, "bool")

	def do_not(self):
		if self.op2_type != "bool":
			exit_program(Status.MISMATCHED_TYPES_ERR, "Expected boolean type in NOT.")

		if self.op2 == "true":
			ret = "false"
		else:
			ret = "true"

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, ret, "bool")

	def do_int2char(self):
		if self.is_var(self.op2):
			frame1 = get_frame(self.op2)
			value = frame1.get_value(self.op2)
			type1 = frame1.get_type(self.op2)
		else:
			value = self.op2
			type1 = self.op2_type

		if type1 != "int":
			exit_program(Status.STRING_ERR, "Expected valid type in INT2CHAR")

		try:
			ret = chr(int(value))
		except:
			exit_program(Status.STRING_ERR, "Expected valid value in INT2CHAR")

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, ret, "string")

	def do_stri2int(self):
		if self.is_var(self.op2):
			frame1 = get_frame(self.op2)
			value1 = frame1.get_value(self.op2)
			type1 = frame1.get_type(self.op2)
		else:
			value1 = self.op2
			type1 = self.op2_type

		if self.is_var(self.op3):
			frame2 = get_frame(self.op3)
			value2 = frame2.get_value(self.op3)
			type2 = frame2.get_type(self.op3)
		else:
			value2 = self.op3
			type2 = self.op3_type

		if type1 != "string" or type2 != "int":
			exit_program(Status.STRING_ERR, "Expected valid type in STRI2INT")

		if int(value2) < 0 or int(value2) > len(value1):
			exit_program(Status.STRING_ERR, "Invalid length in STRI2INT")

		try:
			ret = ord(str(value1[int(value2)]))
		except:
			exit_program(Status.STRING_ERR, "Expected valid value in STRI2INT")

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, ret, "int")

	def do_read(self):
		if self.in_file != sys.stdin:
			if len(self.inputs) == 0:
				read = "nil"
			else:
				read = self.inputs.popleft()
		else:
			read = input()

		if self.op2 == "int":
			value = int(read)
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

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, value, type1)

	def do_write(self):
		if str(self.op1).find('F@') != -1:
			frame = self.get_frame(self.op1)
			value = frame.get_value(self.op1)
		else:
			value = self.op1

		if str(value).find('nil') != -1:
			value = ""

		print(value, end = '')

	def do_concat(self):
		if self.is_var(self.op2):
			frame1 = self.get_frame(self.op2)
			value1 = frame1.get_value(self.op2)
			type1 = frame1.get_type(self.op2)
		else:
			value1 = self.op2
			type1 = self.op2_type

		if self.is_var(self.op3):
			frame2 = self.get_frame(self.op3)
			value2 = frame1.get_value(self.op3)
			type2 = frame1.get_type(self.op3)
		else:
			value2 = self.op3
			type2 = self.op3_type

		if type1 != "string" or type2 != "string":
			exit_program(Status.MISMATCHED_TYPES_ERR, "Only string types allowed in CONCAT.")

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, value1 + value2, "string")

	def do_strlen(self):
		if self.is_var(self.op2):
			frame1 = self.get_frame(self.op2)
			value1 = frame1.get_value(self.op2)
			type1 = frame1.get_type(self.op2)
		else:
			value1 = self.op2
			type1 = self.op2_type

		if type1 != "string":
			exit_program(Status.MISMATCHED_TYPES_ERR, "Only string types allowed in STRLEN.")

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, len(value1), "int")

	def do_getchar(self):
		if self.is_var(self.op2):
			frame1 = self.get_frame(self.op2)
			value1 = frame1.get_value(self.op2)
			type1 = frame1.get_type(self.op2)
		else:
			value1 = self.op2
			type1 = self.op2_type

		if self.is_var(self.op3):
			frame2 = self.get_frame(self.op3)
			value2 = frame1.get_value(self.op3)
			type2 = frame1.get_type(self.op3)
		else:
			value2 = self.op3
			type2 = self.op3_type

		if type1 != "string" or type2 != "int":
			exit_program(Status.MISMATCHED_TYPES_ERR, "Only string types allowed in GETCHAR.")

		if int(value2) >= len(value1) or int(value2) < 0:
			exit_program(Status.STRING_ERR, "Bad value in GETCHAR.")

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, value1[int(value2)], "string")

	def do_setchar(self):
		if self.is_var(self.op2):
			frame1 = self.get_frame(self.op2)
			value1 = frame1.get_value(self.op2)
			type1 = frame1.get_type(self.op2)
		else:
			value1 = self.op2
			type1 = self.op2_type

		if self.is_var(self.op3):
			frame2 = self.get_frame(self.op3)
			value2 = frame1.get_value(self.op3)
			type2 = frame1.get_type(self.op3)
		else:
			value2 = self.op3
			type2 = self.op3_type


		frame = self.get_frame(self.op1)
		value = frame.get_value(self.op1)
		Type = frame.get_type(self.op1)

		if type1 != "int" or type2 != "string" or Type != "string":
			exit_program(Status.MISMATCHED_TYPES_ERR, "Only string types allowed in SETCHAR.")

		if int(value1) < 0 or int(value1) >= len(value):
			exit_program(Status.STRING_ERR, "Bad value in SETCHAR.")

		if len(value2) > 1:
			new_value = value[:int(value1)] + value2[0] + value[int(value1) + 1:]
		else:
			new_value = value[:int(value1)] + value2 + value[int(value1) + 1:]

		frame.set_value(self.op1, new_value, "string")

	def do_type(self):
		if self.is_var(self.op2):
			frame1 = self.get_frame(self.op2)
			type1 = frame1.get_type(self.op2)
		else:
			type1 = self.op2_type

		if type1 is None:
			type1 = ""

		frame = self.get_frame(self.op1)
		frame.set_value(self.op1, type1, "string")

	def do_jump(self):
		for label in self.labels:
			if label == self.op1:
				return self.labels[label]

		exit_program(Status.SEMTANTIC_ERR, "Attempted to jump to a non existant label.")


	def execute(self):
		order = 0

		if self.opcode == "MOVE":
			self.do_move()
		elif self.opcode == "CREATEFRAME":
			self.do_createframe()
		elif self.opcode == "PUSHFRAME":
			self.do_pushframe()
		elif self.opcode == "POPFRAME":
			self.do_popframe()
		elif self.opcode == "DEFVAR":
			self.do_defvar()
		elif self.opcode == "PUSHS":
			self.do_pushs()
		elif self.opcode == "POPS":
			self.do_pops()
		elif self.opcode == "ADD":
			self.do_add()
		elif self.opcode == "MUL":
			self.do_mul()
		elif self.opcode == "SUB":
			self.do_sub()
		elif self.opcode == "IDIV":
			self.do_idiv()
		elif self.opcode == "LT":
			self.do_lt()
		elif self.opcode == "GT":
			self.do_gt()
		elif self.opcode == "EQ":
			self.do_eq()
		elif self.opcode == "AND":
			self.do_and()
		elif self.opcode == "OR":
			self.do_or()
		elif self.opcode == "NOT":
			self.do_not()
		elif self.opcode == "INT2CHAR":
			self.do_int2char()
		elif self.opcode == "STRI2INT":
			self.do_stri2int()
		elif self.opcode == "READ":
			self.do_read()
		elif self.opcode == "WRITE":
			self.do_write()
		elif self.opcode == "CONCAT":
			self.do_concat()
		elif self.opcode == "STRLEN":
			self.do_strlen()
		elif self.opcode == "GETCHAR":
			self.do_getchar()
		elif self.opcode == "SETCHAR":
			self.do_setchar()
		elif self.opcode == "TYPE":
			self.do_type()
		elif self.opcode == "LABEL":
			pass
		elif self.opcode == "JUMP":
			order = self.do_jump()

		if order == 0:
			return self.order + 1
		else:
			return order + 1

	def validate(self, tree):
		if self.opcode == "MOVE":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
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
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "CALL":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'label':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "RETURN":
			pass
		elif self.opcode == "PUSHS":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] != 'label':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "POPS":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "ADD":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "SUB":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "MUL":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "IDIV":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "LT":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "GT":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "EQ":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "AND":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "OR":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "NOT":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "INT2CHAR":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "STRI2INT":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "READ":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] == 'type':
					if element.text != "int" and element.text != "string" and element.text != "bool":
						exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "WRITE":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] != 'label':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "CONCAT":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "STRLEN":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "GETCHAR":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "SETCHAR":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "TYPE":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "LABEL":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'label':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "JUMP":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'label':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "JUMPIFEQ":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'label':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "JUMPIFNEQ":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] == 'var':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				elif element.tag == 'arg2' and element.attrib['type'] != 'label':
					self.op2 = element.text
					self.op2_type = element.attrib['type']
				elif element.tag == 'arg3' and element.attrib['type'] != 'label':
					self.op3 = element.text
					self.op3_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "EXIT":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] != 'label':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "DPRINT":
			for element in tree:
				if element.tag == 'arg1' and element.attrib['type'] != 'label':
					self.op1 = element.text
					self.op1_type = element.attrib['type']
				else:
					exit_program(Status.INVALID_XML_ERR, "Invalid XML.")
		elif self.opcode == "BREAK":
			pass
		else:
		 	exit_program(Status.INVALID_XML_ERR, "Unexpected opcode.")


