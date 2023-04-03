from enum import Enum
import sys
from pathlib import Path

class err_code(Enum):
	ERR_OK = 0
	ERR_ARGS = 10
	ERR_FILE_IN = 11
	ERR_FILE_OUT = 12
	ERR_INT = 99

def parse_args(args):
	if (len(sys.argv) == 3):
		if ("--source=" in sys.argv[1] and "--input=" in sys.argv[2]):
			args.append(sys.argv[1])
			args.append(sys.argv[2])
		elif ("--source=" in sys.argv[2] and "--input=" in sys.argv[1]):
			args.append(sys.argv[2])
			args.append(sys.argv[1])
		else:
			return 22
	elif (len(sys.argv) == 2):
		if ("--source=" in sys.argv[1]):
			args.append(sys.argv[1])
			args.append("")
			args.append("")
		elif ("--input=" in sys.argv[1]):
			args.append("")
			args.append(sys.argv[1])
			args.append("")
			args.append("")
		else:
			return 22
	else:
		return 22

	return 0

def main():
	args = []
	ret = parse_args(args)
	if (ret):
		print('Invalid arguments')
		exit(err_code.ERR_ARGS.value)

	if (len(args) == 2):
		f_xml = args[0].partition('=')[2]
		f_input = args[1].partition('=')[2]
	elif (len(args) == 3):
		f_xml = Path(args[0].partition('=')[2])
		f_input = sys.stdin
	else:
		f_xml = sys.stdin
		f_input = args[1].partition('=')[2]

	#if (not f_xml.is_file() or f_xml != sys.stdin) and (f_input != sys.stdin or f_input.is_file()):
	#	print('File does not exist.')
	#	exit(err_code.ERR_FILE_IN.value)
	f_in = open(f_xml, "r")

	exit(err_code.ERR_OK.value)

if __name__ == "__main__":
	main()