# Documentation of Project Implementation for IPP 2022/2023

Name and surname: Roman Janota
Login: xjanot04

## Program structure

The program begins by calling a function called *main*. The first thing that this function does is parsing command-line arguments. The only allowed argument is `--help` or `-h` for short, which prints the help message and terminates the program. This argument is optional. Next up is validating the *IPPcode23* header, which looks like this: `.IPPcode23`. Every source code written in *IPPcode23* language is required to have this header.

Once everything is set up and the header is validated the main loop of the program begins. This loop does two things - first a line read from the standard input is validated and then it is converted to an *XML* representation and printed to the standard output. Any line beginning with the symbol '#' (the symbol '#' stands for a comment in *IPPcode23*) or being comprised of just white space characters is skipped.

### Instruction validation

An instruction has an opcode and some number of operands (zero or more). An operand can be a variable (eg. `GF@var@`), a constant (eg. `int@4`), a label (eg. `label`) or a symbol, which can be a variable or a constant. In my solution I put instructions with the same number and types of operands together and created a function for each of these sets of instructions. These functions' job is to validate the operands. The set to which an instruction belongs is determined by a fallthrough switch based on it's opcode.

The next step in a validation of an instruction is some further checking of it's operands. I called this step *validate_other*. This part analyzes for example string's escape sequences, that boolean values are either *true* or *false*, that the names of variables are allowed and so on. To do this I mostly used the PHP8 built-in function ` str_contains(string $haystack, string $needle): bool`, but regular expressions can be found here and there too.

### Generating output

The final part of the main loop is converting an instruction from *IPPcode23* to it's *XML* representation. The script defines an *XML* header, which looks like this:
```
<?xml version="1.0" encoding="UTF-8"?>
    <program language="IPPcode23">
    </program>
```
and to which every instruction is later appended. For every instruction read an element called *instruction* is added as a child to the *program* element. The *instruction* element has an attribute *order*, which is the number of the instruction, and an attribute *opcode*, which is the opcode of the instruction. Afterwards the script iterates over all it's operands. In each iteration the value of the given operand is read and the characters '&', '<' and '>' are replaced by their *XML* escape sequences (*&amp*, *&lt* and *&gt* in this order) if they're present. Next a child is added to the *instruction* element called *arg%*, where '%' is the number of the argument, with it's value that was read before and with an attribute called *type*, which is the type of the argument.

#### Dependencies
The script uses the following PHP libraries:
- *SimpleXML* - a toolset for working with XML
- *DOMDocument* - formatting of the XML output
