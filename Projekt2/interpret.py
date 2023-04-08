import argparse
import xml.etree.ElementTree as ET
import frame
from status import *
from instruction import *
import os

def find_instruction(instructions, order):
	for instruction in instructions:
		if instruction.order == order:
			return instruction
	return None

def main():
	# parse arguments
	parser = argparse.ArgumentParser(description='Interpreter for IPPcode23.')
	parser.add_argument('--source', help='IPPcode23 source code file.')
	parser.add_argument('--input', help='File with inputs for the source file.')
	args = vars(parser.parse_args())

	if args['input'] is None and args['source'] is None:
		exit_program(MISSING_PARAM_ERR, "Missing both parameters.")
	elif args['input'] is None:
		input_f = sys.stdin
		source_f = args['source']
	elif args['source'] is None:
		input_f = args['input']
		source_f = sys.stdin
	else:
		input_f = args['input']
		source_f = args['source']

	if input_f != sys.stdin and not os.path.isfile(input_f):
		exit_program(Status.INPUT_FILE_ERR, "Unable to open input file.")

	if source_f != sys.stdin and not os.path.isfile(source_f):
		exit_program(Status.INPUT_FILE_ERR, "Unable to open source file.")

	tree = ET.parse(source_f)
	root = tree.getroot()
	instructions = []
	i = 0
	for child in root:
		instruction = Instruction(child, input_f)
		instruction.validate(child)
		instructions.append(instruction)
		i = i + 1

	for instruction in instructions:
		instruction.create_labels()
		Instruction.labels = instruction.labels

	max_order = 0
	for instruction in instructions:
		if instruction.order > max_order:
			max_order = instruction.order

	order = 1
	while order <= max_order:
		instruction = find_instruction(instructions, order)
		order = instruction.execute()
		Instruction.GF = instruction.GF
		Instruction.TF = instruction.TF
		Instruction.LF = instruction.LF
		Instruction.stack = instruction.stack
		Instruction.inputs = instruction.inputs
		Instruction.labels = instruction.labels
		if order > max_order:
			break

	exit_program(Status.OK, None)

if __name__ == "__main__":
	main()