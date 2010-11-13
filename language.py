
from ply import lex

tokens = (
		"OPERATION",
		"LITERAL",
		"VARIABLE"
)

t_OPERATION = (
		r"CALLBUILTIN|CALLFUNC|SETVAR|RETURN"
)

t_LITERAL = (
		r'"i"'
)

lex.lex()
print lex

