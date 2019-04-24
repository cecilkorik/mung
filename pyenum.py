class pyenum(object):
	def __setattr__(self, name, val):
		global enum_reversals
		
		object.__setattr__(self, name, val)
		if not self in enum_reversals:
			enum_reversals[self] = {}
		enum_reversals[self][val] = name
	
enum_reversals = {}
	
def reverse_enum(e, v):
	global enum_reversals
	
	if e in enum_reversals:
		return enum_reversals[e][v]
	return None