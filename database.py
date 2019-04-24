from parse import static_parser
from language import ObjRef
import errors


class DBObject(object):
	def __init__(self, objref):
		self.obj = objref
		self.parent = ObjRef(-1)
		self.children = []
		self.props = {}
		self.funcs = []
	
	def match_local_func(self, name, flags=""):
		for func in self.funcs:
			skip = False
			for f in flags:
				if not f in o.flags:
					skip = True
			if not skip and func.match(name):
				return func
		return None


	def get_prop(self, prop):
		if prop in self.props:
			rv = self.props[prop]
		else:
			return None
			
	def add_func(self, name):
		self.funcs.append(DBFunc(self.obj, name))
		

class DBFunc(object):
	def __init__(self, objref, name):
		self.obj = objref
		self.name = name
		self.names = name.split(' ')
		self.flags = ""
		self.bytecode = []
		self.code = ""
		self.index = None
		
	def compile(self, code):
		try:
			bytecode = static_parser.parse(code)
		except ParseError:
			return [0, "Compile error in line <unknown>"]
		
		self.bytecode = bytecode
		self.code = code
		return [1, "Success"]
		
	def match(self, name):
		for test in self.names:
			if test[-1] == '*':
				if name[:len(test)-1] == test[:-1]:
					"partial match"
					return True
			elif test == name:
				return True
		
		return False
				
	def ref(self):
		return self.obj
			

class Database(object):
	def __init__(self, dbname):
		self.dbname = dbname
		self.objects = []
		
	def load(self):
		raise NotImplementedError("This function should be overridden by a derived class")
	def checkpoint(self):
		raise NotImplementedError("This function should be overridden by a derived class")
	def save(self):
		raise NotImplementedError("This function should be overridden by a derived class")
		
	def bootstrap_minimal(self):
		so = DBObject(ObjRef(0))
		self.objects = [so]
		
		
		
	def set_prop(self, obj, prop, val):
		o = self.get(obj)
		o.set_property(prop, val)
		
	def set_file(self, obj, fn, val):
		o = self.get(obj)
		o.set_file(fn, val)
		
	def get_prop(self, obj, prop):
		o = self.get(obj)
		return o.get_property(prop)
		
	def get_file(self, obj, fn):
		o = self.get(obj)
		return o.get_file(fn)

	def create(self):
		for i in xrange(len(self.objects)):
			if self.objects[i] == None:
				newref = ObjRef(i)
				self.objects[i] = DBObject(newref)
				return newref
			
		newref = ObjRef(len(self.objects))
		self.objects.append(DBObject(newref))
		return newref
	
	def destroy(self, ref):
		if ref.objnum >= len(self.objects) or ref.objnum < 0:
			raise ValueError("Invalid object number")
		
		obj = self.objects[ref.objnum]
		if obj == None:
			raise ValueError("Object already destroyed")
			
		for child in obj.children:
			child.parent = ObjRef(-1)
		
		self.objects[ref.objnum] = None
		self.objects_cleanup()
		
	def objects_cleanup(self):
		i = len(self.objects)
		while i > 0:
			i -= 1
			if self.objects[i] != None:
				i += 1
				break
				
	def get_obj(self, objnum):
		i = objnum
		if i < len(self.objects):
			self.objects[i:] = []

		if i < 0:
			raise errors.VMRuntimeError(errors.enum.E_INVIND)
		elif i >= len(self.objects):
			raise errors.VMRuntimeError(errors.enum.E_INVIND)
		else:
			o = self.objects[i]
			if o == None:
				raise errors.VMRuntimeError(errors.enum.E_INVIND)
			else:
				return o
			
			
	def get(self, objref):
		return self.objects[objref.objnum]
		
	def match_command(self, player, cmd, vars):
		vars['player'] = player
		vars['caller'] = player
		
		match_order = [player]
		for ref in match_order:
			match = self.match_func(self, ref, cmd)
			if match:
				obj, func = match
				vars['this'] = ref
				vars['funcname'] = func.name
				vars['funcobj'] = obj
				return [func, vars]
		return None
		
	def match_func(self, obj, funcname, flags=""):
		o = self.get(obj)
		func = o.match_func(funcname, flags)
		if func != None:
			return [obj, func]
		ancestor = o.parent
		while ancestor != ObjRef(-1):
			o = self.get(ancestor)
			func = o.match_func(funcname, flags)
			if func != None:
				return [ancestor, func]
			ancestor = o.parent
		return None
	
	def match_property(self, obj, propname):
		o = self.get(obj)
		prop = o.get_property(propname)
		if prop != None:
			return [obj, prop]
		ancestor = o.parent
		while ancestor != ObjRef(-1):
			o = self.get(ancestor)
			prop = o.get_property(propname)
			if prop != None:
				return [ancestor, prop]
			ancestor = o.parent
		return None
	

		
