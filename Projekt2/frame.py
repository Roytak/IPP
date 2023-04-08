from dataclasses import dataclass
from status import *

@dataclass
class Var:
	value: str = ""
	var_type: str = ""


class Frame:
	def __init__(self):
		self.vars = {}

	def get_type(self, symbol):
		if symbol.find('int@') != -1:
			return 'int'
		elif symbol.find('string@') != -1:
			return 'string'
		elif symbol.find('bool') != -1:
			return 'bool'
		elif symbol.find('nil') != -1:
			return 'nil'
		else:
			return None

	def insert_var(self, name, value, var_type):
		for key in self.vars.keys():
			if key == name:
				exit_program(Status.SEMTANTIC_ERR, "Variable already exists")
		self.vars[name] = Var(value, var_type)

	def set_value(self, dest, src, src_type):
		if src_type is None:
			src_type = self.get_type(src)

		if str(src).find('F@') != -1:
			self.vars[dest] = Var(src[src.find('@')+1:], src_type)
		else:
			self.vars[dest] = Var(src, src_type)

	def get_value(self, name):
		return self.vars[name].value

	def get_type(self, name):
		return self.vars[name].var_type
