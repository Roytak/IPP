"""
IPP - Project 2
Author: Roman Janota
Date: 16-04-2023
"""

import argparse
import xml.etree.ElementTree as ET
import frame
from status import *
from instruction import *
import os

# finds the instruction in the instructions array based on order
def find_instruction(instructions, order):
    for instruction in instructions:
        if instruction.order == order:
            return instruction
    return None

# checks order duplicity in the XML, it is forbidden
def check_order_duplicity(root):
    orders = []

    for child in root:
        if child.tag != 'instruction':
            exit_program(Status.INVALID_XML_ERR, "Expected instruction element.")

        if 'order' not in child.attrib:
            exit_program(Status.INVALID_XML_ERR, "Missing order attribute.")
        if 'opcode' not in child.attrib:
            exit_program(Status.INVALID_XML_ERR, "Missing opcode attribute.")

        order = child.attrib['order']
        if not order.isnumeric():
            exit_program(Status.INVALID_XML_ERR, "Non integer order.")

        order = int(order)
        if order < 0:
            exit_program(Status.INVALID_XML_ERR, "Negative order attribute.")

        for i in range(len(orders)):
            if orders[i] == order:
                exit_program(Status.INVALID_XML_ERR, "Duplicate order found.")

        orders.append(order)

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

    # parse the XML
    try:
        tree = ET.parse(source_f)
    except:
        exit_program(Status.MALFORMED_ERR, "Unable to parse XML.")

    # get the root element
    root = tree.getroot()
    if root.tag != 'program':
        exit_program(Status.INVALID_XML_ERR, "Expected program as root element.")

    # check the order duplicity
    check_order_duplicity(root)

    # validate each instruction element and append it to the array
    instructions = []
    for child in root:
        instruction = Instruction(child, input_f)
        instruction.validate(child)
        instructions.append(instruction)

    # create all the labels
    for instruction in instructions:
        instruction.create_labels()
        Instruction.labels = instruction.labels

    # find the minimum and maximum order of the instructions
    max_order = 0
    min_order = sys.maxsize
    for instruction in instructions:
        if instruction.order > max_order:
            max_order = instruction.order
        if instruction.order < min_order:
            min_order = instruction.order

    order = min_order
    while order <= max_order:
        # find the instruction with the given order
        instruction = find_instruction(instructions, order)
        if instruction is None:
            # order can have holes, meaning there can be order 1 and then order 3
            order = order + 1
            if order > max_order:
                break
            continue

        # execute the given instruction
        order = instruction.execute()

        # set the new values of static class variables for every instruction
        Instruction.GF = instruction.GF
        Instruction.TF = instruction.TF
        Instruction.LF = instruction.LF
        Instruction.stack = instruction.stack
        Instruction.inputs = instruction.inputs
        Instruction.labels = instruction.labels
        Instruction.call_stack = instruction.call_stack

        if order > max_order:
            break

    exit_program(Status.OK, None)

if __name__ == "__main__":
    main()
