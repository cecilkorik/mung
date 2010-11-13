from pyparsing import *

def enum_parse():
	fd = open('test.enum', 'r')
	
	# syntax we don't want to see in the final parse tree
	_lcurl = Suppress('{')
	_rcurl = Suppress('}')
	_equal = Suppress('=')
	_comma = Suppress(',')
	_semi = Suppress(';')
	_enum = Suppress('enum')
	
	identifier = Word(alphas,alphanums+'_')
	integer = Word(nums)
	enumValue = Group(identifier('name') + Optional(_equal + integer('value')))
	enumList = Group(enumValue + ZeroOrMore(_comma + enumValue))
	enum = _enum + identifier('enum') + _lcurl + enumList('list') + _rcurl + Optional(_semi)
	
	enumlist = ZeroOrMore(enum)
	
	#print enumlist.parseString(fd.read(), parseAll=True)
	# find instances of enums ignoring other syntax
	for item in enumlist.parseString(fd.read(), parseAll=True):
	    id = 0
	    for entry in item:
	        if entry.value != '':
	            id = int(entry.value)
	        print '%s_%s = %d' % (item.enum.upper(),entry.name.upper(),id)
	        id += 1
	
	fd.close()

def parse_fourfn():	
    global bnf
    if not bnf:
        point = Literal( "." )
        e     = CaselessLiteral( "E" )
        fnumber = Combine( Word( "+-"+nums, nums ) + 
                           Optional( point + Optional( Word( nums ) ) ) +
                           Optional( e + Word( "+-"+nums, nums ) ) )
        ident = Word(alphas, alphas+nums+"_$")
     
        plus  = Literal( "+" )
        minus = Literal( "-" )
        mult  = Literal( "*" )
        div   = Literal( "/" )
        lpar  = Literal( "(" ).suppress()
        rpar  = Literal( ")" ).suppress()
        addop  = plus | minus
        multop = mult | div
        expop = Literal( "^" )
        pi    = CaselessLiteral( "PI" )
        
        expr = Forward()
        atom = (Optional("-") + ( pi | e | fnumber | ident + lpar + expr + rpar ).setParseAction( pushFirst ) | ( lpar + expr.suppress() + rpar )).setParseAction(pushUMinus) 
        
        # by defining exponentiation as "atom [ ^ factor ]..." instead of "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-righ
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + ZeroOrMore( ( expop + factor ).setParseAction( pushFirst ) )
        
        term = factor + ZeroOrMore( ( multop + factor ).setParseAction( pushFirst ) )
        expr << term + ZeroOrMore( ( addop + term ).setParseAction( pushFirst ) )
        bnf = expr
    return bnf
	

def moo_parse():
	fd = open('test.moo', 'r')
	data = fd.read()	
	fd.close()
	
    point = Literal( "." )

	integer = Word( "+-"+nums, nums )
    fnumber = Combine( integer + 
                       Optional( point + Optional( Word( nums ) ) ) +
                       Optional( CaselessLiteral('e') + Word( "+-"+nums, nums ) ) )
    ident = Word(alphas, alphas+nums+"_")
 
    plus  = Literal( "+" )
    minus = Literal( "-" )
    mult  = Literal( "*" )
    div   = Literal( "/" )
    lpar  = Literal( "(" ).suppress()
    rpar  = Literal( ")" ).suppress()
    addop  = plus | minus
    multop = mult | div
    expop = Literal( "^" )
    
    expr = Forward()
    atom = (Optional("-") + ( fnumber | ident + lpar + expr + rpar ).setParseAction( pushFirst ) | ( lpar + expr.suppress() + rpar )).setParseAction(pushUMinus) 
    
    # by defining exponentiation as "atom [ ^ factor ]..." instead of "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-righ
    # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
    factor = Forward()
    factor << atom + ZeroOrMore( ( expop + factor ).setParseAction( pushFirst ) )
    
    term = factor + ZeroOrMore( ( multop + factor ).setParseAction( pushFirst ) )
    expr << term + ZeroOrMore( ( addop + term ).setParseAction( pushFirst ) )
    
    
