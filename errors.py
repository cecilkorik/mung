from pyenum import pyenum

enum = pyenum()
enum.E_NONE = 0
enum.E_PERM = 1 
enum.E_PROPNF = 2
enum.E_FUNCNF = 3
enum.E_FILENF = 4
enum.E_VARNF = 5
enum.E_INVARG = 6
enum.E_TICKS = 7
enum.E_SECONDS = 8
enum.E_MEMORY = 9
enum.E_IOERR = 10
enum.E_TYPE = 11
enum.E_ARGS = 12
enum.E_FLOAT = 13
enum.E_DIV = 14
enum.E_SYNTAX = 15
enum.E_UNICODE = 16
enum.E_MAXREC = 17
enum.E_PARSE = 18
enum.E_RANGE = 19
enum.E_INVIND = 20
enum.E_RECMOVE = 21
enum.E_NACC = 22
enum.E_INVOBJ = 23
enum.E_CONN = 24

enum.E_USER = 200
enum.E_USER1 = 201
enum.E_USER2 = 202
enum.E_USER3 = 203
enum.E_USER4 = 204
enum.E_USER5 = 205
enum.E_USER6 = 206
enum.E_USER7 = 207
enum.E_USER8 = 208
enum.E_USER9 = 209
enum.E_USER10 = 210

msgs = {
	enum.E_NONE: "No error",
	enum.E_PERM: "Permission denied",
	enum.E_PROPNF: "Property not found",
	enum.E_FUNCNF: "Function not found",
	enum.E_FILENF: "File not found",
	enum.E_VARNF: "Variable not found",
	enum.E_INVARG: "Invalid argument",
	enum.E_TICKS: "Out of ticks",
	enum.E_SECONDS: "Out of seconds",
	enum.E_MEMORY: "Out of memory",
	enum.E_IOERR: "I/O error",
	enum.E_TYPE: "Type mismatch",
	enum.E_ARGS: "Incorrect number of arguments",
	enum.E_FLOAT: "Floating point error",
	enum.E_DIV: "Division by zero",
	enum.E_SYNTAX: "Syntax error",
	enum.E_UNICODE: "Invalid unicode character",
	enum.E_MAXREC: "Maximum recursion depth reached",
	enum.E_PARSE: "Unable to parse command",
	enum.E_RANGE: "Index out of range",
	enum.E_INVIND: "Invalid indirection",
	enum.E_RECMOVE: "Recursive move",
	enum.E_NACC: "Move refused by destination",
	enum.E_INVOBJ: "Invalid object",
	enum.E_CONN: "Connection error",

	enum.E_USER: "User-defined error",
	enum.E_USER1: "User-defined error 1",
	enum.E_USER2: "User-defined error 2",
	enum.E_USER3: "User-defined error 3",
	enum.E_USER4: "User-defined error 4",
	enum.E_USER5: "User-defined error 5",
	enum.E_USER6: "User-defined error 6",
	enum.E_USER7: "User-defined error 7",
	enum.E_USER8: "User-defined error 8",
	enum.E_USER9: "User-defined error 9",
	enum.E_USER10: "User-defined error 10",
}

class VMRuntimeError(Exception):
	def __init__(self, code, msg=None):
		if msg == None and code in msgs:
			msg = msgs[code]
		elif msg == None:
			msg = "Unknown error code"
		Exception.__init__(self, msg)
		self.errorcode = code


		