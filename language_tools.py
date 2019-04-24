import sys
import traceback
import bisect
from pyparsing import ParseException

def tokenparser(func):
	def newfunc(s, loc, tokens):
		try:
			rv = func(tokens)
			pos = lineno(s, loc)
			if isinstance(rv, VMBaseObject):
				rv.pos = pos
				return rv
			assert not False in [isinstance(x, (VMBaseObject, list)) for x in rv]
			for x in rv:
				if isinstance(x, VMBaseObject) and x.pos == None:
					x.pos = pos
		except:
			e = sys.exc_info()
			if e[0] == ParseException:
				raise
			gd = globals()
			funcobj = None
			for x in gd:
				if hasattr(gd[x], "parse") and gd[x].parse == newfunc:
					funcobj = x
			print("Error with %s.parse tokens: %s" % (funcobj, tokens))
			traceback.print_exc(e)
			raise

		return [rv]
		
	return newfunc

	
def lineno(s, loc):
	if hash(s) in lineno.cache:
		cache = lineno.cache[hash(s)]
	else:
		cache = []
	
		i = 0
		while True:
			n = s[i:].find("\n") + i
			if n < i:
				break
			cache.append(n)
			i = n + 1
			
		cache.append(len(s))
		
		lineno.cache[hash(s)] = cache
	
	cachepos = bisect.bisect_left(cache, loc)
	line = cachepos + 1
	if cachepos == 0:
		char = loc + 1
	else:
		char = loc - cache[cachepos-1]
		
	
	return (line, char)
	
lineno.cache = {}

	
class VMBaseObject(object):
	def __init__(self):
		self.pos = None

	def bytecode(self):
		return [self]

	def __repr__(self):
		return "<%s>" % (self.__class__.__name__,)
