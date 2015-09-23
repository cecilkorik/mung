from language_tools import *
from pyparsing import ParseException
from bytecode import *

def disallow_keywords(tokens,keywords=None):
	if keywords == None:
		keywords = disallow_keywords.keywords
	else:
		keywords = set(keywords)
		
	for t in tokens:
		if isinstance(t, VMIdent):
			if t.name in keywords:
				raise ParseException, "Restricted keyword: %s" % (t.name,)
		elif isinstance(t, unicode):
			tstr = t.encode('ascii', 'ignore')
			if tstr in keywords:
				raise ParseException, "Restricted keyword: %s" % (tstr,)
		elif isinstance(t, str):
			if t in keywords:
				raise ParseException, "Restricted keyword: %s" % (t,)
				
disallow_keywords.keywords = set('if,elseif,else,endif,try,except,finally,endtry,while,endwhile,continue,break,for,foreach,endfor'.split(','))


class ObjRef(object):
	def __init__(self, objnum):
		self.objnum = objnum
		
	def __eq__(self, other):
		return self.objnum == other.objnum




class VMType(VMBaseObject):
	def bytecode(self):
		return [StackLiteral(self)]
	
class VMInteger(VMType):
	def __init__(self, value):
		VMType.__init__(self)
		self.value = int(value)
		
	@staticmethod
	@tokenparser
	def parse(tokens):
		return StackLiteral(VMInteger(tokens[0]))

	def __repr__(self):
		return "%s" % (self.value,)
		
class VMFloat(VMType):
	def __init__(self, value):
		VMType.__init__(self)
		self.value = float(value)

	@staticmethod
	@tokenparser
	def parse(tokens):
		return StackLiteral(VMFloat(tokens[0]))

	def __repr__(self):
		return "%s" % (self.value,)


class VMTable(VMType):
	def __init__(self, value):
		VMType.__init__(self)
		self.value = dict(value)

	@staticmethod
	@tokenparser
	def parse(tokens):
		return StackLiteral(VMTable(tokens[0]))
		
class VMList(VMType):
	def __init__(self, value):
		VMType.__init__(self)
		self.value = list(value)

	@staticmethod
	@tokenparser
	def parse(tokens):
		return StackLiteral(VMList())

class VMTablePair(VMType):
	def __init__(self, value):
		VMType.__init__(self)
		self.key = key
		self.value = value
	
	@staticmethod
	@tokenparser
	def parse(tokens):
		return StackLiteral(VMList())
	
class VMString(VMType):
	def __init__(self, value):
		VMType.__init__(self)
		if isinstance(value, unicode):
			self.value = value
		else:
			self.value = unicode(str(value), 'ascii', 'ignore')
	
	def __repr__(self):
		return "\"%s\"" % (repr(self.value)[1:].strip("'").replace("\\'", "'").replace('"', '\\"'),)
		
	@staticmethod
	@tokenparser
	def parse(tokens):
		return StackLiteral(VMString(tokens[0]))
		
class VMObjRef(VMType):
	def __init__(self, value):
		VMType.__init__(self)
		if isinstance(value, ObjRef):
			self.value = value
		elif isinstance(value, (float, int)):
			self.value = ObjRef(int(value))
		else:
			raise TypeError, "Attempted to create VMObjRef with invalid object reference: %r" % (value,)
			
	@staticmethod
	@tokenparser
	def parse(tokens):
		return StackLiteral(VMObjRef(int(tokens[1])))
		
	def __repr__(self):
		return "#%s" % (self.value.objnum,)

class VMRef(VMBaseObject):
	pass
	
class VMIdent(VMRef):
	def __init__(self, name):
		VMRef.__init__(self)
		self.name = name
		
	def bytecode(self):
		return [StackLiteral(unicode(self.name))]

	@staticmethod
	@tokenparser
	def parse(tokens):
		disallow_keywords(tokens)
		return VMIdent(tokens[0])

	def __repr__(self):
		return "<ident %s>" % (self.name,)


class VMVariable(VMRef):
	def __init__(self, name):
		VMRef.__init__(self)
		self.name = name

	def ref(self):
		return [StackLiteral(unicode(self.name))]

	def bytecode(self):
		return codejoin(self.ref(), GetVariable())
		
	@staticmethod
	@tokenparser
	def parse(tokens):
		disallow_keywords(tokens)
		return VMVariable(tokens[0])

	def __repr__(self):
		return "<variable %s>" % (self.name,)
	
class VMFileRef(VMRef):
	def __init__(self, obj, name):
		VMRef.__init__(self)
		self.obj = obj
		self.name = name

	@staticmethod
	@tokenparser
	def parse(tokens):
		assert tokens[1] == "!"
		return VMFileRef(tokens[0], tokens[2])
		#return codejoin(tokens[0], StackLiteral(tokens[2]), GetProperty())
		
	def ref(self):
		return [self.obj, self.name]

	def __repr__(self):
		return "<fileref %s!%s>" % (self.obj, self.name)
		
	def bytecode(self):
		return codejoin(self.ref(), GetFile())
		
class VMPropRef(VMRef):
	def __init__(self, obj, prop):
		VMRef.__init__(self)
		self.obj = obj
		self.prop = prop

	@staticmethod
	@tokenparser
	def parse(tokens):
		assert tokens[1] == "."
		return VMPropRef(tokens[0], tokens[2])
		#return codejoin(tokens[0], StackLiteral(tokens[2]), GetProperty())
		
	def ref(self):
		return [self.obj, self.prop]

	def __repr__(self):
		return "<propref %s.%s>" % (self.obj, self.prop)
		
	def bytecode(self):
		return codejoin(self.ref(), GetProperty())
		
class VMCoreRef(VMPropRef):
	@staticmethod
	@tokenparser
	def parse(tokens):
		return VMPropRef(VMObjRef(0), tokens[1])

