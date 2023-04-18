# Documentation of Project Implementation for IPP 2022/2023

Name and surname: Roman Janota

Login: xjanot04

## Introduction

This documentation describes an interpreter for the *IPPcode23* language. The program was written in Python3.10. The project has three command-line arguments:

- --help (-h): prints a help message and terminates the program,
- --source <source>: path to a file with *IPPcode23* instructions in *XML* format,
- --input <input>: path to a file with inputs for some *IPPcode23* instructions.
 

The interpreter takes *IPPcode23* instructions in the *XML* format as input and transforms their meaning into output.

## Project design

The project is composed of the following modules: interpret.py, frame.py, status.py, and instruction.py. The last three modules each define a class and its methods, where the name of the class is the same as the name of the file. The philosophy behind my project can be described in the following steps:

1) parse the command-line arguments,
2) parse the source file and store the *XML* representation,
3) for each instruction element in the *XML*:
3a. create an instruction object,
3b. validate the instruction,
3c. append this object to an array of instructions,
4) iterate over the array of instructions and create every label (if any),
5) iterate over the array of instructions and find the minimum and maximum value of the order attribute,
6) initialize the order to the minimum order
7) if the order is less than or equal to the maximum order, continue; otherwise, terminate the program,
8) find an instruction with the given order in the array of instructions,
9) execute the instruction,
10) go to step 7.

## Instruction class

The instruction class contains the whole functionality of the interpreter. It relies on sharing static class variables between objects of this class. This means that if an instruction object makes any changes to any instruction class static variable, then this variable's new value has to be set for all the instruction class objects. The static class variables are:

- GF:Frame - the global frame,
- TF:Frame - the temporary frame,
- LF:Stack - the local frame stack,
- stack:Stack - the stack,
- inputs:Queue - the queue for inputs,
- labels:Dict - the dictionary of labels, where the key is the name of the label and value is the instruction order,
- call_stack:Stack - the stack for function calls.
 

### Instruction object initialization

A list of instance attributes follows:

- order,
- opcode,
- op1,
- op1_type,
- op2,
- op2_type,
- op3,
- op3_type,
- in_file.


An instruction object requires two parameters for initialization. The first of them is called *tree*. The tree represents an instruction *XML* element, which has the attributes order and opcode. Their values are then assigned to the instance attributes order and opcode. The next parameter is file, which is the input command-line argument. It is assigned to in_file. If it is a file and not standard input, the static class variable *inputs* gets filled with lines from the input. That is because inputs are in a queue, and the first input line will be needed first.

### Instruction validation

The instruction class defines a method called validate. This method statically checks each instruction's number of operands and their types, if it is possible. The main purpose is to assign the values and types of the operands to the instance attributes op1, op1_type, and so on. All of the instance attributes are now initialized.

### Execution of an instruction

A key method of the instruction class is called execute. It is a wrapper around each instruction's functionality. The Instruction class defines a method called do_<opcode> (e.g., do_read) for each *IPPcode23* instruction. The execute method then calls the given do_<opcode> method based on the opcode instance attribute.

## Frame class

The sole instance attribute of an object of the frame class is a dictionary, where key is the name of the variable and value is its value. The class defines methods that insert a variable into the frame, set the value of a variable, and get the value and type of the variable. Its intended purpose is to encapsulate the data with which the instruction objects work.
