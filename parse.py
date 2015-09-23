from pyparsing import *
from language import *


class Parser(object):
	def __init__(self):
		self.parser = None
		self.init_parser()
	
	def nest(self, tokens):
		return [list(tokens)]
		
	def init_parser(self):
		""" phase 1:
		most important part is to build the meta-parser for "expr". expr represents any atomic action that returns a value, and the bulk of
		the code in any program will consist primarily of exprs and flow control. expr is heavily recursive, because most types of expr can
		take another expr as an input value.
		"""
		point = Literal( "." )
		plus  = Literal( "+" )
		minus = Literal( "-" )
		mult  = Literal( "*" )
		div   = Literal( "/" )
		lpar  = Literal( "(" ).suppress()
		rpar  = Literal( ")" ).suppress()
		llbr  = Literal( "[" ).suppress()
		rlbr  = Literal( "]" ).suppress()
		addop  = plus | minus
		multop = mult | div
		expop = Literal( "^" )
		quote = Literal( '"' )
		excl   = Literal( "!" )
		call  = Literal( ":" )
		endl  = Literal( ";" )
		lisep = Literal( "," ).suppress()
		objn  = Literal( "#" )
		ref   = Literal( "$" )
		assign = Literal( "=" )
		flatten = Literal( "@" )
		neg = excl.copy()
		

		expr = Forward()
		ident = Word(alphas+"_", alphas+nums+"_")
		ident.setParseAction(VMIdent.parse)
		variable = Word(alphas+"_", alphas+nums+"_")
		variable.setParseAction(VMVariable.parse)
		
		
		integer = Word( "+-"+nums, nums )
		fnumber = Combine( integer + 
						   Optional( point + Optional( Word( nums ) ) ) +
						   Optional( CaselessLiteral('e') + Word( "+-"+nums, nums ) ) )
		objref = objn + Word( "+-"+nums, nums )
		objref.setParseAction(VMObjRef.parse)
		coreref = (ref + ident)
		coreref.setParseAction(VMCoreRef.parse)
		bexpr = (lpar + expr + rpar).setParseAction(self.nest)
		objrefexpr = bexpr | coreref | variable | objref
		identexpr = bexpr | ident
		propref = (objrefexpr + point + ident).setParseAction(VMPropRef.parse) | coreref
		fileref = (objrefexpr + excl + ident).setParseAction(VMFileRef.parse)

		argspec = Optional(delimitedList(expr))
		argspec.setParseAction(StackToList.parse)
		funccall = objrefexpr + call + identexpr + lpar + argspec + rpar
		
		fnumber.setParseAction(VMFloat.parse)
		integer.setParseAction(VMInteger.parse)
		funccall.setParseAction(CallFunc.parse)
		
		stringlit = QuotedString(quoteChar='"', escChar='\\').setParseAction(VMString.parse)
		
		atom = Forward()
		bifunction = (ident + lpar + argspec + rpar).setParseAction(CallBuiltin.parse)
		
		flatexpr = Optional(flatten) + expr
		flatexpr.setParseAction(Flatten.parse)
		listlit = llbr + Optional(flatexpr) + ZeroOrMore(lisep + flatexpr) + rlbr
		literal = integer | fnumber | stringlit | listlit | objref
		
		atom << (Optional(minus) + ZeroOrMore(neg) + (propref | literal | bifunction | bexpr | variable | funccall | fileref)).setParseAction(UnaryOp.parse)
		
		
		# by defining exponentiation as "atom [ ^ factor ]..." instead of "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-righ
		# that is, 2^3^2 = 2^(3^2), not (2^3)^2.
		factor = Forward()
		factor << atom + ZeroOrMore( (expop + factor).setParseAction(ArithExp.parse) )
		
		term = factor + ZeroOrMore( (multop + factor).setParseAction(ArithMul.parse) )
		#term.setParseAction(self.nest)
		mathexpr = term + ZeroOrMore( (addop + term).setParseAction(ArithAdd.parse) )
		#mathexpr.setParseAction(self.nest)
		
		opeq = Literal('==')
		opneq = Literal('!=')
		opgteq = Literal('<=')
		oplteq = Literal('>=')
		oplt = Literal('<')
		opgt = Literal('>')
		opin = Keyword('in')
		
		opcmp = opeq | opneq | opgteq | oplteq | oplt | opgt | opin
		eqexpr = mathexpr + Optional( (opcmp + mathexpr).setParseAction(BoolCompare.parse) )
		
		opand = Literal('&&') | Keyword('and')
		opor = Literal('||') | Keyword('or')
		opxor = Literal('~~') | Keyword('xor')
		
		opbool = opand | opor | opxor
		boolexpr = eqexpr + ZeroOrMore( (opbool + eqexpr).setParseAction(BoolLogic.parse) )
		
		
		assignable = variable | propref | fileref
		assignexpr = Optional(assignable + assign) + boolexpr
		expr << assignexpr.setParseAction(Assignment.parse)
		
		
		""" phase 2:
		now that expr is built, we can move on to handling flow control statements, and after that the structure of the program
		is mostly defined
		"""
		
		ifstart = (Keyword("if") + bexpr)
		ifelseif = (Keyword("elseif") + bexpr)
		ifelse = Keyword("else")
		ifend = Keyword("endif")
		trystart = Keyword("try")
		tryexcept = (Keyword("except") + variable)
		tryelse = Keyword("else")
		tryfinally = Keyword("finally")
		tryend = Keyword("endtry")
		whilestart = (Keyword("while") + bexpr)
		whileend = Keyword("endwhile")
		forstart = (Keyword("for") + variable + Keyword("in") + bexpr)
		forend = Keyword("endfor")

		kwdbreak = Keyword("break").setParseAction(LoopBreak)
		kwdcontinue = Keyword("continue").setParseAction(LoopContinue)
		kwdreturn = Keyword("return")

		rtnexpr = (kwdreturn + expr).setParseAction(KeywordReturn.parse)
		line = expr | rtnexpr
		lline = expr | rtnexpr | kwdcontinue | kwdbreak
		exprblock = ZeroOrMore(line + endl)
		lexprblock = ZeroOrMore(lline + endl)

		block = Forward()
		lblock = Forward()
		ifblock = ifstart + block + ZeroOrMore(ifelseif + block) + Optional(ifelse + block) + ifend
		tryblock = trystart + block + Optional(tryexcept + block + Optional(tryelse + block)) + Optional(tryfinally + block) + tryend
		iflblock = ifstart + lblock + ZeroOrMore(ifelseif + lblock) + Optional(ifelse + lblock) + ifend
		trylblock = trystart + lblock + Optional(tryexcept + lblock + Optional(tryelse + lblock)) + Optional(tryfinally + block) + tryend
		whileblock = whilestart + lblock + whileend
		forblock = forstart + lblock + forend
		
		ifblock.setParseAction(IfBlock.parse)
		tryblock.setParseAction(TryBlock.parse)
		iflblock.setParseAction(IfBlock.parse)
		trylblock.setParseAction(TryBlock.parse)
		whileblock.setParseAction(WhileBlock.parse)
		forblock.setParseAction(ForeachBlock.parse)
		
		# blocks are used for code blocks that are outside a loop. Inside a loop, all code blocks are lblocks
		# which allow loop-control keywords like break and continue (except try-finally, it wouldn't make sense)
		
		block << (exprblock + Optional(ifblock | tryblock | whileblock | forblock) + exprblock)
		lblock << (lexprblock + Optional(iflblock | trylblock | whileblock | forblock) + lexprblock)
		
		block.setParseAction(self.nest)
		lblock.setParseAction(self.nest)

		endl.setParseAction(DiscardStack.parse)
		self.parser = block
		#print argspec.parseString("hello(hi.xyz)", parseAll=True)
		#print block.parseString(u"hi.xyz + #555.test;", parseAll=True)
		#print block.parseString("""serverlog();""")

	def parse(self, data):
		rv = self.parser.parseString(data, parseAll=True)
		
		return optimizer.optimize(rv)

	def parse_command(self, line):
		ls = line.split(' ')
		cmd = ls[0]
		argstr = ' '.join(ls[1:])
		vars = {
			'cmdstr': line,
			'cmd': cmd,
			'argstr': argstr,
			'args': [x.strip() for x in ls[1:] if x.strip() != '']
		}
		
		return [cmd, vars]

	def test(self):
		#print self.parse(u"if (1) #740.xyz + -hello.world; endif")
		
		data = unicode(open("test.moo", "r").read(), 'utf-8')
		rv = self.parse(data)
		print rv
		return rv
	
	
static_parser = Parser()

if __name__ == "__main__":
	p = Parser()
	p.test()
