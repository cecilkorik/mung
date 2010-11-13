

class VMType(object):
	pass
	
class VMInteger(VMType):
	def __init__(self, value):
		self.value = int(value)
class VMFloat(VMType):
	def __init__(self, value):
		self.value = float(value)
class VMTable(VMType):
	def __init__(self, value):
		self.value = dict(value)
		
class VMString(VMType):
	def __init__(self, value):
		if isinstance(value, unicode):
			self.value = value
		else:
			self.value = unicode(str(value), 'ascii', 'ignore')
		
class VMObjRef(VMType):
	def __init__(self, value):
		if isinstance(value, ObjRef):
			self.value = value
		elif isinstance(value, (float, int)):
			self.value = ObjRef(int(value))
		else:
			raise TypeError, "Attempted to create VMObjRef with invalid object reference: %r" % (value,)
	

def coerce(value):
	if isinstance(value, int):
		return VMInteger(value)
	elif isinstance(value, (tuple, list)):
		return VMList(list(value))
	elif isinstance(value, unicode):
		return VMString(value)
	elif isinstance(value, dict):
		return VMTable(value)
	elif isinstance(value, ObjRef):
		return VMObjRef(value)
	elif isinstance(value, float):
		return VMFloat(value)
	elif value == None:
		return VMInteger(0)
	else:
		raise TypeError("Unknown type %s cannot be coerced to VMType" % (type(value),))
		
	
def uncoerce(value):
	assert isinstance(value, VMType)
	return value.value