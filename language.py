import time
from builtins import builtin_map
from language_types import coerce, uncoerce

class VirtualMachine(object):
	def __init__(self, db):
		self.db = db
		self.active_task_id = None
		self.sleepytime = None
		self.codestack = []
		self.stack = []
		self.contexts = []
		self.tasks = {}
		self.task_sequence = []
		self.ticks_used = 0
		self.exception_thrown = None
		
	def pop_code(self):
		return self.code_stack.pop()
		
	def push_code(self, code):
		self.code_stack.append(code)
		
	def pop(self, count=1):
		return [uncoerce(self.stack.pop()) for x in range(count)]
		
	def push(self, value):
		self.stack.append(coerce(value))
	
	def setvar(self, varname, val):
		self.contexts[-1][varname] = val
		
	def getvar(self, varname):
		return self.contexts[-1][varname]
		
	def push_context(self):
		self.contexts.append({})
	
	def pop_context(self):
		self.contexts.pop()
		
	def suspend_start_next(self, delay):
		now = time.time()
		newtask = heapq.heappushpop(self.task_sequence, (now+max(0.0,delay), self.stack, self.contexts, self.ticks_used))
		return activate_task(newtask)
		
	def finished_start_next(self):
		now = time.time()
		newtask = heapq.heappop(self.task_sequence)
		return activate_task(newtask)
	
	def activate_task(self, task):
		if now < task[0]:
			"task isn't ready to execute yet"
			self.sleepytime = task[0] - now
			heapq.heappush(self.task_sequence, task[0])
			return False
			
		self.active_task_id = task[0]
		self.stack = task[1]
		self.contexts = task[2]
		self.ticks_used = task[3]
		self.exception_thrown = None
	
	def get_next_task(self):
		heapq.heappop(self.task_sequence)
	
	def uncaught_exception(self):
		pass
	
	def run_active_task(self):
		task_id = self.active_task_id
		while task_id == self.active_task_id and self.code_stack and self.exception_thrown == None:
			nextop = self.pop_code()
			nextop.execute(self)
		
		if self.exception_thrown != None:
			self.uncaught_exception()
			self.finished_start_next()
			
		if task_id == self.active_task_id:
			self.finished_start_next()
			
		self.finished_start_next
			
	
	def run(self):
		self.sleepytime = None
		if self.active_task_id == None:
			finished_start_next()
			if self.active_task_id == None:
				return
			
		
		
		
		

class CodeOp(object):
	def __init__(self):
		pass
		
class GetProperty(CodeOp):
	def execute(self, vm):
		prop, obj = vm.pop(2)
		vm.stack.append(vm.db.get_property(obj, prop))

class SetProperty(CodeOp):
	def execute(self, vm):
		val, prop, obj = vm.pop(3)
		vm.db.set_property(obj, prop, val)

class GetFile(CodeOp):
	def execute(self, vm):
		prop, obj = vm.pop(2)
		vm.stack.append(vm.db.get_file(obj, prop))

class SetFile(CodeOp):
	def execute(self, vm):
		val, prop, obj = vm.pop(3)
		vm.db.set_file(obj, prop, val)
		
class SetVariable(CodeOp):
	def execute(self, vm):
		val, varname = vm.pop(2)
		vm.setvar(varname, val)
		
class GetVariable(CodeOp):
	def execute(self, vm):
		varname, = vm.pop(1)
		vm.push(vm.getvar(varname))
		
class CallBuiltin(CodeOp):
	def __init__(self):
		pass
		
	def execute(self, vm):
		funcname, = vm.pop(1)
		builtin_map[funcname](vm)
		
class DiscardStack(CodeOp):
	def __init__(self):
		pass
	def execute(self, vm):
		count, = vm.pop(1)
		vm.pop(count)


class StartContext(CodeOp):
	def execute(self, vm):
		vm.push_context()

class EndContext(CodeOp):
	def execute(self, vm):
		vm.pop_context()