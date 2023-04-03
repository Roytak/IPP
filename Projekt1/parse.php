<?php
/*
 * IPP Project 1 - Parser for IPPcode23
 * Author: Roman Janota
 * Date: 22-02-2023
 */

$xml_header = <<<XML
<?xml version="1.0" encoding="UTF-8"?>
<program language="IPPcode23">
</program>
XML;

function
display_help() : void
{
	echo "Usage: php[8.1] parse.php [OPTIONS]\n";
	echo "Parse IPPcode23 instructions (from stdin) and output them as XML.\n";
	echo "Example: php parse.php < input.txt\n\n";
	echo "Available options:\n";
	echo "\t--help [-h]\t\tdisplay a help message.\n";
}

function
validate_header(string $line) : int
{
	$line = trim(strtok($line, '#'));
	$line = strtolower(str_replace(array("\r", "\n"), '', $line));
	if (!strncmp($line, '.ippcode23', 10) && strlen($line) == 10) {
		return 0;
	}

	return 21;
}

function
val_var_symb(string $args) : int
{
	$args = explode(" ", $args);

	if (count($args) != 2) {
		return 23;
	}

	$args[0] = strtoupper($args[0]);
	if (!str_starts_with($args[0], "GF@") && !str_starts_with($args[0], "TF@") && !str_starts_with($args[0], "LF@")) {
		return 23;
	}

	if (!str_contains($args[1], "@")) {
		return 23;
	}

	return 0;
}

/* simply validate that the instruction contains just the opcode */
function
val_no_args(array $args) : int
{
	if (count($args) == 1) {
		return 0;
	}

	return 23;
}

/* check if there is just one argument and if it is in the IPPcode23 variable format */
function
val_var(string $args) : int
{
	if (substr_count($args, ' ') > 0) {
		return 23;
	}

	$args = strtoupper($args);
	if (str_starts_with($args, "GF@") || str_starts_with($args, "TF@") || str_starts_with($args, "LF@")) {
		return 0;
	}

	return 23;
}

/* check if there is just one argument and if it is a symbol (it has to contain '@') */
function
val_symb(string $args) : int
{
	if (substr_count($args, ' ') > 0) {
		return 23;
	}

	if (!str_contains($args, '@')) {
		return 23;
	}

	return 0;
}

/* check if there are three arguments and if the first one is a variable (has a frame in the name)
 * and if the other two are symbols */
function
val_var_symb_symb(string $args) : int
{
	$args = explode(" ", $args);

	if (count($args) != 3) {
		return 23;
	}

	if (!str_contains($args[1], '@') || !str_contains($args[2], '@')) {
		return 23;
	}

	if (str_starts_with($args[0], "GF@") || str_starts_with($args[0], "TF@") || str_starts_with($args[0], "LF@")) {
		return 0;
	}

	return 23;
}

/* check if there are two arguments and the first one is a variable
 * and the second one is a type (either int, string or bool) */
function
val_var_type(string $args) : int
{
	$args = explode(" ", $args);

	if (count($args) != 2) {
		return 23;
	}

	$args[0] = strtoupper($args[0]);
	if (str_starts_with($args[0], "GF@") || str_starts_with($args[0], "TF@") || str_starts_with($args[0], "LF@")) {
		if (!strcmp($args[1], "int") || !strcmp($args[1], "string") || !strcmp($args[1], "bool")) {
			return 0;
		}
	}

	return 23;
}

/* check if there are three arguments and if the first one is a label (contains no '@')
 * and if the other two are symbols */
function
val_label_symb_symb(string $args) : int
{
	$args = explode(" ", $args);

	if (count($args) != 3) {
		return 23;
	}

	if (str_contains($args[0], "@")) {
		return 23;
	}

	if (!str_contains($args[1], "@") || !str_contains($args[2], "@")) {
		return 23;
	}

	return 0;
}

/* check if there is just one argument and if the argument is a label */
function
val_label(string $args) : int
{
	if (substr_count($args, ' ') > 0) {
		return 23;
	}

	if (str_contains($args, "@")) {
		return 23;
	}

	return 0;
}

function
validate_opcode(string $instr) : int
{
	$ret = 0;
	$val_func;

	/* split by spaces */
	$instr = explode(" ", $instr, 2);

	$opcode = $instr[0];

	/* convert to lower case so we can compare */
	$opcode = strtolower($opcode);

	/* fallthrough switch, instructions are divided based on their operands */
	switch ($opcode) {
	case 'createframe':
	case 'pushframe':
	case 'return':
	case 'break':
	case 'popframe':
		$val_func = 'val_no_args';
		break;

	case 'defvar':
	case 'pops':
		$val_func = 'val_var';
		break;

	case 'call':
	case 'label':
	case 'jump':
		$val_func = 'val_label';
		break;

	case 'exit':
	case 'dprint':
	case 'write':
	case 'pushs':
		$val_func = 'val_symb';
		break;

	case 'add':
	case 'sub':
	case 'mul':
	case 'idiv':
	case 'lt':
	case 'gt':
	case 'eq':
	case 'and':
	case 'or':
	case 'str2int':
	case 'concat':
	case 'getchar':
	case 'setchar':
		$val_func = 'val_var_symb_symb';
		break;

	case 'move':
	case 'not':
	case 'int2char':
	case 'strlen':
	case 'type':
		$val_func = 'val_var_symb';
		break;

	case 'read':
		$val_func = 'val_var_type';
		break;

	case 'jumpifeq':
	case 'jumpifneq':
		$val_func = 'val_label_symb_symb';
		break;

	default:
		fwrite(STDERR, "Unknown opcode " . $opcode . "\n");
		return 22;
	}

	if ($val_func == 'val_no_args') {
		$ret = $val_func($instr);
	} else {
		if (isset($instr[1])) {
			$ret = $val_func($instr[1]);
		} else {
			$ret = 23;
		}
	}

	return $ret;
}

function
validate_string(string $str) : int
{
	if (ctype_space($str) || str_contains($str, '#')) {
		return 23;
	}

	/* check if there are any backslashes */
	$bs_count = substr_count($str, "\\");
	if ($bs_count > 0) {
		if ($bs_count != preg_match_all("/\\\\\d{3}/", $str)) {
			return 23;
		}
	}

	return 0;
}

function
validate_other(string $instr, string $arg) : int
{

	if (str_contains($arg, "string@")) {
		/* string validation */
		$ret = validate_string(substr($arg, strpos($arg, "string@") + 1));
		if ($ret) {
			fwrite(STDERR, "Invalid string " . $arg . "\n");
			return $ret;
		}
	}

	if (str_contains($instr, "pushs") && !str_contains($arg, "@")) {
		/* label in pushs */
		fwrite(STDERR, "Unexpected label " . $arg . "\n");
		return 23;
	}

	if (str_contains($arg, "bool@") && !(str_contains($arg, "bool@true") || str_contains($arg, "bool@false"))) {
		/* bool has to have value true or false */
		fwrite(STDERR, "Invalid boolean value " . $arg . "\n");
		return 23;
	}

	if (str_contains($arg, "F@")) {
		/* check variable name */
		$var_name = strtok(substr($arg, strpos($arg, "@") + 1), " ");
		if (str_contains($var_name, "@") || preg_match('/^\d/', $var_name) || str_contains($var_name, "/") || str_contains($var_name, "\\")) {
			fwrite(STDERR, "Invalid variable name " . $arg . "\n");
			return 23;
		}
	}

	if (!str_contains($arg, '@')) {
		/* check label name */
		if (str_contains($arg, "@") || preg_match('/^\d/', $arg) || str_contains($arg, "/") || str_contains($arg, "\\")) {
			fwrite(STDERR, "Invalid label " . $arg . "\n");
			return 23;
		}
	}

	if (str_contains($arg, "f@")) {
		/* no lower case frame */
		fwrite(STDERR, "Invalid frame " . $arg . "\n");
		return 23;
	}

	if (str_contains($arg, "nil@") && strcmp($arg, "nil@nil")) {
		fwrite(STDERR, "Invalid use of nil " . $arg . "\n");
		return 23;
	}

	if (str_contains($arg, "int@")) {
		/* no empty int */
		if (strlen($arg) == 4) {
			fwrite(STDERR, "Empty integer " . $arg . "\n");
			return 23;
		}
	}

	return 0;
}

function
validate_instruction(string $instr) : int
{
	$ret = 0;

	if (ctype_space($instr)) {
		/* empty line */
		$ret = -1;
	} elseif (str_starts_with($instr, '#')) {
		/* comment */
		$ret = -1;
	}

	if ($ret) {
		goto end;
	}

	/* check opcode */
	$ret = validate_opcode($instr);
	if ($ret) {
		goto end;
	}

	$arg_c = substr_count($instr, ' ');
	$line_arr = explode(" ", $instr);

	for ($i = 1; $i <= $arg_c; $i++) {
		$ret = validate_other($instr, $line_arr[$i]);
		if ($ret) {
			goto end;
		}
	}

end:
	return $ret;
}

function
get_type_from_arg($arg) : string
{
	if (strpos($arg, '@')) {
		/* check if anything is uppercase*/
		$type = strtok($arg, '@');
		if (preg_match('/[A-Z]/', $type) && !str_contains($type, "GF") && !str_contains($type, "TF") && !str_contains($type, "LF")) {
			exit(23);
		}
	}
	$arg = strtolower($arg);

	if (str_starts_with($arg, "bool@")) {
		return "bool";
	} elseif (str_starts_with($arg, "gf@") || str_starts_with($arg, "tf@") || str_starts_with($arg, "lf@")) {
		return "var";
	} elseif (str_starts_with($arg, "nil@")) {
		return "nil";
	} elseif (str_starts_with($arg, "int@")) {
		return "int";
	} elseif (str_starts_with($arg, "string@")) {
		return "string";
	} elseif (!strcmp($arg, "int") || !strcmp($arg, "string") || !strcmp($arg, "bool")) {
		return "type";
	} else {
		return "label";
	}
}

function
generate_xml($xml, $line, $instr_id) : int
{
	$arg_c = substr_count($line, ' ');
	$line_arr = explode(" ", $line);
	$i;
	$value = NULL;

	$instruction = $xml->addChild('instruction');
	$instruction->addAttribute('order', $instr_id);
	$instruction->addAttribute('opcode', strtoupper($line_arr[0]));

	for ($i = 1; $i <= $arg_c; $i++) {
		$type = get_type_from_arg($line_arr[$i]);
		if (!strcmp($type, "type")) {
			$value = substr($line_arr[$i], strpos($line_arr[$i], "@"));
		} elseif (!strcmp($type, "var")) {
			$value = ucfirst($line_arr[$i]);
			$value = str_replace("f@", "F@", $value);
		} elseif (!strcmp($type, "bool")) {
			$value = substr($line_arr[$i], strpos($line_arr[$i], "@") + 1);
		} elseif (!strcmp($type, "int")) {
			$value = substr($line_arr[$i], strpos($line_arr[$i], "@") + 1);
		} elseif (!strcmp($type, "string")) {
			$value = substr($line_arr[$i], strpos($line_arr[$i], "@") + 1);
		} elseif (!strcmp($type, "label")) {
			$value = $line_arr[$i];
		} else {
			$value = substr($line_arr[$i], strpos($line_arr[$i], "@") + 1);
		}
		/* replace special chars */
		$value = str_replace('&', '&amp;', $value);
		$value = str_replace('<', '&lt;', $value);
		$value = str_replace('>', '&gt;', $value);

		$arg = $instruction->addChild('arg' . $i, $value);
		$arg->addAttribute('type', $type);
	}

	return 0;
}

function
main() : int
{
	global $argc, $argv;
	$ret;
	$line;
	$line_c = 2;
	$instr_id = 1;
	global $xml_header;

	if ($argc > 1) {
		if ($argc == 2 && (!strcmp($argv[1], "--help") || !strcmp($argv[1], "-h"))) {
			display_help();
			exit(0);
		}

		exit(10);
	}

	ini_set('display_errors', 'stderr');
	$dom = new DOMDocument('1.0');
	$dom->preserveWhiteSpace = false;
	$dom->formatOutput = true;

	$xml = new SimpleXMLElement($xml_header);

	$line = fgets(STDIN);
	while (str_starts_with($line, '#') || ctype_space($line)) {
		/* skip comments */
		$line = fgets(STDIN);
	}

	$ret = validate_header($line);
	if ($ret) {
		fwrite(STDERR, "Invalid header " . $line . "\n");
		exit(21);
	}

	while($line = fgets(STDIN)){
		if (str_starts_with($line, '#') || ctype_space($line)) {
			/* skip comments and empty lines */
			continue;
		}
		/* strip comment */
		$line = strtok($line, '#');
		/* replace multiple spaces with single one and trim them from the start and end */
		$line = trim(preg_replace('!\s+!', ' ', $line));

		$ret = validate_instruction($line);
		if ($ret) {
			if ($ret == -1) {
				continue;
			}
			fwrite(STDERR, "Invalid instruction " . $line . " on line " . $line_c . "\n");
			exit($ret);
		}

		$ret = generate_xml($xml, $line, $instr_id);
		if ($ret) {
			fwrite(STDERR, "Unable to generate xml for " . $line . " on line " . $line_c . "\n");
			exit($ret);
		}

		$instr_id++;
		$line_c++;
	}

	$dom->loadXML($xml->asXML());
	echo $dom->saveXML();

	return 0;
}

main();

?>
