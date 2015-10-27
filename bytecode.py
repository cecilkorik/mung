from language_tools import *
from builtins import builtin_map
import optimizer




def coerce(value):
	from language_types import *
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
	elif isinstance(value, VMType):
		return value
	else:
		raise TypeError("Unknown type %s cannot be coerced to VMType" % (type(value),))
		
	
def uncoerce(value):
	from language_types import VMType
	assert isinstance(value, VMType)
	return value.value
	

def codejoin(*args):
	rv = []
	for arg in args:
		if isinstance(arg, CodeOpSequence):
			for subarg in arg.sequence:
				rv.extend(codejoin(subarg))
		elif isinstance(arg, list):
			for subarg in arg:
				rv.extend(codejoin(subarg))
		else:
			rv.append(arg)
			
	return rv
	seq = CodeOpSequence.new(rv)
	return seq
	#return flatten(rv, ltypes=(list,))


class CodeOp(VMBaseObject):
	def load_stack(self, vm):
		pass

	def ticks(self):
		return 1

class CodeOpSequence(CodeOp):
	
	@staticmethod
	def new(input):
		c = CodeOpSequence()
		c.sequence = input
		return c
		
	def load_stack(self, vm):
		pass

	def ticks(self):
		return 0

		
class StackCodeOp(CodeOp):
	def __init__(self, stack_value):
		CodeOp.__init__(self)
		self.stack_value = stack_value

	def load_stack(self, vm):
		vm.push(self.stack_value)


class NoOp(CodeOp):
	def execute(self, vm):
		pass

	def ticks(self):
		return 0
		
	@staticmethod
	@tokenparser
	def parse(tokens):
		return []
	
		
class GetProperty(CodeOp):
	def execute(self, vm):
		obj, prop = vm.pop(2)
		objstore = vm.db.get_obj(obj)
		val = objstore.get_prop(prop)
		vm.push(val)

	@staticmethod
	@tokenparser
	def parse(tokens):
		return codejoin(GetProperty())

class SetProperty(CodeOp):
	def execute(self, vm):
		val, prop, obj = vm.pop(3)
		vm.db.set_property(obj, prop, val)
		vm.push(val)

	@staticmethod
	@tokenparser
	def parse(tokens):
		return codejoin(StackLiteral(tokens[0]))

class GetFile(CodeOp):
	def execute(self, vm):
		obj, prop = vm.pop(2)
		objstore = vm.db.get_obj(obj)
		val = objstore.get_file(prop)
		vm.push(val)

class SetFile(CodeOp):
	def execute(self, vm):
		val, prop, obj = vm.pop(3)
		vm.db.set_file(obj, prop, val)
		vm.push(val)
		
class SetVariable(CodeOp):
	def execute(self, vm):
		val, varname = vm.pop(2)
		vm.setvar(varname, val)
		vm.push(val)
		
	@staticmethod
	@tokenparser
	def parse(tokens):
		assert isinstance(tokens[0], GetVariable)
		return codejoin(SetVariable(tokens[0].stack_value))
	
		
class GetVariable(CodeOp):
	def execute(self, vm):
		varname, = vm.pop(1)
		vm.push(vm.getvar(varname))
	
	@staticmethod
	@tokenparser
	def parse(tokens):
		return codejoin(tokens[0], GetVariable())
		
class CallBuiltin(CodeOp):
	def execute(self, vm):
		funcname, args = vm.pop(2)
		funcname = funcname.encode('ascii', 'ignore')
		retval = builtin_map[funcname](vm, args)
		vm.push(retval)

	@staticmethod
	@tokenparser
	def parse(tokens):
		#if not tokens[0] in builtin_map:
		#	raise ParseException, 'Attempt to call undefined builtin function: "%s"' % (tokens[0],)
		return codejoin(tokens[0], tokens[1], CallBuiltin())
		
class CallFunction(CodeOp):
	def execute(self, vm):
		obj, name = vm.pop(2)
		vm.code_push(codejoin(StartContext(), vm.get_code(obj, name), EndContext()))
	
	@staticmethod
	@tokenparser
	def parse(tokens):
		return codejoin(tokens[0], CallFunction())

class ArithAdd(CodeOp):
	def execute(self, vm):
		v1, v2 = vm.pop(2)
		vm.push(v1+v2)
	
	@staticmethod
	@tokenparser
	def parse(tokens):
		if tokens[0] == "+":
			return codejoin(tokens[1], ArithAdd())
		else:
			return codejoin(tokens[1], ArithSub())

class ArithSub(CodeOp):
	def execute(self, vm):
		v1, v2 = vm.pop(2)
		vm.push(v1-v2)


class ArithMul(CodeOp):
	def execute(self, vm):
		v1, v2 = vm.pop(2)
		vm.push(v1*v2)
	
	@staticmethod
	@tokenparser
	def parse(tokens):
		if tokens[0] == "*":
			return codejoin(tokens[1], ArithMul())
		else:
			return codejoin(tokens[1], ArithDiv())

class ArithDiv(CodeOp):
	def execute(self, vm):
		v1, v2 = vm.pop(2)
		vm.push(v1/v2)

class ArithExp(CodeOp):
	def execute(self, vm):
		v1, v2 = vm.pop(2)
		vm.push(v1**v2)
	
	@staticmethod
	@tokenparser
	def parse(tokens):
		return codejoin(tokens[1], ArithExp())

		
class BoolCompare(CodeOp):
	map = {
		'==': lambda x, y: int(x==y),
		'!=': lambda x, y: int(x!=y),
		'>': lambda x, y: int(x>y),
		'<': lambda x, y: int(x<y),
		'<=': lambda x, y: int(x<=y),
		'>=': lambda x, y: int(x>=y),
		'in': lambda x, y: int(x in y)
	}

	def __init__(self, cmpfunc):
		CodeOp.__init__(self)
		self.cmp = cmpfunc
		
	def execute(self, vm):
		v1, v2 = vm.pop(2)
		vm.push(self.cmp(v1, v2))
	
	@staticmethod
	@tokenparser
	def parse(tokens):
		op = tokens[0]
		
		return codejoin(tokens[1], BoolCompare(BoolCompare.map[op]))
		
		
class BoolLogic(CodeOp):
	map = {
		'&&': lambda x, y: int(x and y),
		'||': lambda x, y: int(x or y),
		'~~': lambda x, y: int((x or y) and not (x and y)),
		'and': lambda x, y: int(x and y),
		'or': lambda x, y: int(x or y),
		'xor': lambda x, y: int((x or y) and not (x and y)),
	}

	def __init__(self, cmpfunc):
		CodeOp.__init__(self)
		self.cmp = cmpfunc
		
	def execute(self, vm):
		v1, v2 = vm.pop(2)
		vm.push(self.cmp(v1, v2))
	
	@staticmethod
	@tokenparser
	def parse(tokens):
		op = tokens[0]
		
		return codejoin(tokens[1], BoolLogic(BoolLogic.map[op]))

class UnaryOp(CodeOp):
	map = {
		"!": lambda x: int(not x),
		"-": lambda x: -x
	}

	def __init__(self, cmpfunc):
		CodeOp.__init__(self)
		self.cmp = cmpfunc
		
	def execute(self, vm):
		v = vm.pop(1)
		vm.push(self.cmp(v))
	
	@staticmethod
	@tokenparser
	def parse(tokens):
		rv = []
		ops = []
		for t in tokens:
			if isinstance(t, (str, unicode)) and t in UnaryOp.map:
				ops.append(UnaryOp(UnaryOp.map[t]))
			else:
				rv.append(t)
		return codejoin(rv, ops)

class Assignment(CodeOp):
	@staticmethod
	@tokenparser
	def parse(tokens):
		from language_types import VMVariable, VMPropRef, VMFileRef
		if len(tokens) > 2:
			assert tokens[1] == "="
			var = tokens[0]
			if isinstance(var, VMVariable):
				var = var.ref() + [SetVariable()]
			elif isinstance(var, VMPropRef):
				var = var.ref() + [SetProperty()]
			elif isinstance(var, VMFileRef):
				var = var.ref() + [SetFile()]
			else:
				raise ValueError, "Assignment to unknown type: %s" % (var,)
				
			return codejoin(tokens[2:], var)
		return tokens

class StackLiteral(StackCodeOp):
	def execute(self, vm):
		vm.push(self.stack_value)
		
	@staticmethod
	@tokenparser
	def parse(tokens):
		return StackLiteral(tokens[0])
	
	def __repr__(self):
		try:
			nv = coerce(self.stack_value)
		except TypeError:
			return "<** INVALID STACKLITERAL: %r **>" % (self.stack_value,)
		return "<StackLiteral %s>" % (coerce(self.stack_value),)


class StackToList(CodeOp):
	def execute(self, vm):
		from language_types import VMList
		count, = vm.pop(1)
		stacklist = vm.pop_raw(count)
		i = 0
		while i < len(stacklist):
			if isinstance(stacklist[i], VMList) and stacklist[i].flat:
				nexti = i + len(stacklist[i])
				stacklist[i:i+1] = uncoerce(stacklist[i])
			else:
				stacklist[i] = uncoerce(stacklist[i])
				nexti = i + 1

			i = nexti
		vm.push(stacklist)
		
	@staticmethod
	@tokenparser
	def parse(tokens):
		if not tokens:
			return codejoin(StackLiteral(0), StackToList())
		rv = codejoin(tokens[0][0], StackLiteral(len(tokens)), StackToList())
		return rv
	
class Flatten(CodeOp):
	def execute(self, vm):
		flatlist, = vm.pop_raw(1)
		flatlist.flat = 1
		vm.push(flatlist)
		
	@staticmethod
	@tokenparser
	def parse(tokens):
		if len(tokens) > 0 and tokens[0] == '@':
			return codejoin(tokens[0], Flatten())
		else:	
			return tokens
	
		
class CallFunc(CodeOp):
	def execute(self, vm):
		obj, funcname, args = vm.pop(3)
		vm.push_context(args)
		vm.push_code(codejoin(
				vm.get_code(obj, funcname),
				EndContext()
			))
		

	@staticmethod
	@tokenparser
	def parse(tokens):
		assert len(tokens) == 4 and tokens[1] == ":"
		return codejoin(tokens[0], tokens[2], tokens[3], CallFunc())
		
		
class DiscardStack(CodeOp):
	def execute(self, vm):
		vm.pop(1)


	@staticmethod
	@tokenparser
	def parse(tokens):
		return codejoin(DiscardStack())

class ExtractStack(CodeOp):
	def __init__(self, callback, count):
		CodeOp.__init__(count)
		self.callback = callback
	
	def execute(self, vm):
		count, = vm.pop(1)
		self.callback(vm.pop(count))

class KeywordReturn(CodeOp):
	def execute(self, vm):
		vm.jump_code(EndContext)

	@staticmethod
	@tokenparser
	def parse(tokens):
		return codejoin(tokens[1:], KeywordReturn())
		
class LoopBreak(CodeOp):
	def execute(self, vm):
		vm.jump("break")
		
class LoopContinue(CodeOp):
	def execute(self, vm):
		vm.jump("cont")
		
class StartContext(CodeOp):
	def execute(self, vm):
		vm.push_context()

class EndContext(CodeOp):
	def execute(self, vm):
		vm.pop_context()
		
class LabelCodeOp(CodeOp):
	def __init__(self, label):
		CodeOp.__init__(self)
		self.label = label
	def execute(self, vm):
		pass

	def ticks(self):
		return 0
		
class JumpUncond(LabelCodeOp):
	def execute(self, vm):
		vm.jump(self.label)

class JumpIfFalse(LabelCodeOp):
	def execute(self, vm):
		cond, = vm.pop(1)
		if not cond:
			vm.jump(self.label)

class JumpIfTrue(LabelCodeOp):
	def execute(self, vm):
		cond, = vm.pop(1)
		if cond:
			vm.jump(self.label)

class EndBlock(LabelCodeOp):
	def execute(self, vm):
		pass


class FinallyBlock(EndBlock):
	def execute(self, vm):
		if vm.exc_stack:
			# finally can be invoked by the exception handler itself, so
			# it's possible the error has not been handled yet.
			# if there is an unhandled exception still on the stack, then 
			# continue searching for a handler.
			vm.reraise()


class ExcHandlerBlock(EndBlock):
	def __init__(self, label, code):
		EndBlock.__init__(self, label)
		
		self.code = code

	def execute(self, vm):
		while vm.exc_stack:
			# get the exception that's being handled and place it on the real stack
			exc = vm.exc_pop()
			vm.push(exc)
			
			# and queue up the exception handler code
			vm.code_push(self.code)
			


class WhileBlock(CodeOp):
	def __init__(self):
		CodeOp.__init__(self)
		
		self.cond = None
		self.block = []

	def execute(self, vm):
		# load the block's code into the vm at runtime
		# prevents conflicts with jump targets
		vm.code_push(codejoin(
				self.cond,
				JumpIfFalse("break"),
				self.block,
				EndBlock("cont"),
				self,
				EndBlock("break")
			))
	
	@staticmethod
	@tokenparser
	def parse(tokens):
		rv = WhileBlock()
		
		for i in xrange(1, len(tokens)):
			tok = tokens[i]
			if rv.cond == None:
				rv.cond = tok
			else:
				rv.block.append(tok)
		
		return rv
		
class TryBlock(CodeOp):
	def __init__(self):
		CodeOp.__init__(self)
		
		self.var = None
		self.blocks = {}
		self.blocks = {"try": [], "except": [], "else": [], "finally": []}
		
	def execute(self, vm):
		code = []
		code.append(self.blocks["try"])
		
		if "else" in self.blocks:
			code.append(JumpUncond("exc_else"))
		elif "finally" in self.blocks:
			code.append(JumpUncond("exc_finally"))
		else:
			code.append(JumpUncond("exc_normalexit"))
			
		if "except" in self.blocks:
			handler_code = codejoin(
					SetVariable(self.var),
					self.blocks["except"]
				)
			code.append(ExcHandlerBlock("exc_handler", handler_code))
			if "finally" in self.blocks:
				code.append(JumpUncond("exc_finally"))
			else:
				code.append(JumpUncond("exc_normalexit"))
			
		if "else" in self.blocks:
			vm.code_push(self.blocks["else"])
			if "finally" in self.blocks:
				code.append(JumpUncond("exc_finally"))
			else:
				code.append(JumpUncond("exc_normalexit"))
			
		if "finally" in self.blocks:
			code.append(FinallyBlock("exc_finally"))
			code.append(self.blocks["finally"])
		
		code.append(EndBlock("exc_normalexit"))
		vm.code_push(code)
	
	@staticmethod
	@tokenparser
	def parse(tokens):
		rv = TryBlock()
		
		active_tok = None
		for i in xrange(1, len(tokens)):
			tok = tokens[i]
			if tok in ("try", "except", "else", "finally"):
				active_tok = tok
				continue
			
			if active_tok == "except" and self.var == None:
				self.var = tok
			else:
				self.blocks[active_tok].append(tok)
		
		return rv
	
class ForeachExtractList(CodeOp):
	def __init__(self, foreach):
		CodeOp.__init__(self)
		self.foreach = foreach
		self.pos = foreach.pos
	
	def execute(self, vm):
		ldata, = vm.pop(1)
		if isinstance(ldata, dict):
			vm.push(ldata.keys())
			vm.push(0)
		elif isinstance(ldata, list):
			vm.push(ldata)
			vm.push(0)
		else:
			vm.raise_exc("Error")

class ForeachPop(CodeOp):
	def __init__(self, foreach):
		CodeOp.__init__(self)
		self.foreach = foreach
		self.pos = foreach.pos
		
	def execute(self, vm):
		ldata, idx = vm.pop(2)
		if idx > len(ldata):
			"no more values to pop"
			vm.push(0)
		else:
			"more values to pop"
			val = ldata[idx]
			vm.set_var(self.foreach.var, val)
			vm.push(ldata)
			vm.push(idx+1)
			vm.push(1)
		

class ForeachIterator(CodeOp):
	def __init__(self, foreach):
		CodeOp.__init__(self)
		self.foreach = foreach
		self.pos = foreach.pos
		
	def execute(self, vm):
		vm.code_push(codejoin(
				ForeachPop(),
				JumpIfFalse("break"),
				self.foreach.block,
				EndBlock("cont"),
				self,
				EndBlock("break")
			))


class ForeachBlock(CodeOp):
	def __init__(self):
		CodeOp.__init__(self)
		
		self.src = None
		self.list = None
		self.var = None
		self.block = []


	def execute(self, vm):
		# load the block's code into the vm at runtime
		# prevents conflicts with jump targets
		vm.code_push(codejoin(
				self.src,
				ForeachExtractList(),
				self.new_iterator()
			))
	
	def new_iterator(self):
		return ForeachIterator(self)
	
	@staticmethod
	@tokenparser
	def parse(tokens):
		rv = ForeachBlock()
		
		for i in xrange(1, len(tokens)):
			tok = tokens[i]
			if rv.var == None:
				rv.var = tok
			elif tok == "in":
				continue
			elif rv.src == None:
				rv.src = tok
			else:
				rv.block.append(tok)
		
		return rv


class IfBlock(CodeOp):
	def __init__(self):
		CodeOp.__init__(self)
		
		self.conditions = []

	def execute(self, vm):
		# load the ifblock code into the vm at runtime
		# why, I don't know, but it makes my life easier
		code = []
		for cond, block in self.conditions:
			code.append(cond)
			code.append(JumpIfFalse("next"))
			code.append(block)
			code.append(JumpUncond("endif"))
			code.append(EndBlock("next"))
		code.append(EndBlock("endif"))
		codeseq = codejoin(code)
		vm.code_push(codeseq)
	
	@staticmethod
	@tokenparser
	def parse(tokens):
		conds = []
		tok_count = 0
		active_tok = None
		for i in xrange(len(tokens)):
			tok = tokens[i]

			if tok == "endif":
				break
			if tok in ("if", "elseif", "else"):
				tok_count += 1
				active_tok = tok
			else:
				if tok_count > len(conds):
					if active_tok == "else":
						cond = [StackLiteral(1)]
						block = tok
					else:
						cond = [tok]
						block = []
					conds.append([cond, [block]])
				else:
					conds[tok_count-1][1].append(tok)
					
		ib = IfBlock()
		conds = [[optimizer.optimize(x), optimizer.optimize(y)] for x, y in conds]
		ib.conditions = conds
		return ib
