import random, heapq
from parse import Parser
from language import *
import errors

"""
class VMMemory(object):
	def __init__(self):
		self.objects = []
		
	def create(self, i):
		self.objects[i] = None
		
	def create_new(self):
		self.objects.append(abc)
		
	def destroy(self, i):
		self.objects[i] = None
		
	def renumber(self, i, j):
		self.objects[j], self.objects[i] = self.objects[i], self.objects[j]
		
	def trim(self):
		newmax = None
		for i in xrange(len(self.objects)-1, -1, -1):
			if self.objects[i] != None:
				newmax = i
				break
		if newmax != None:
			self.objects = self.objects[:newmax+1]
		
	def get_obj(self, i):
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
"""		

class VMContext(object):
	def __init__(self, vars):
		self.variables = vars

class VMTask(object):
	def __init__(self, id, code, vars):
		self.task_id = id
		self.code_stack = [x for x in reversed(code)]
		self.exc_stack = []
		self.stack = []
		self.contexts = [VMContext(vars)]

	def context(self):
		return self.contexts[-1]

class VirtualMachine(object):
	def __init__(self, db):
		self.db = db
		self.active_task_id = None
		self.sleepytime = None
		self.contexts = []
		self.tasks = {}
		self.task = None
		self.active_task_heap = []
		self.next_task_heap = []
		self.ticks_used = 0
		self.max_ticks = 300000
		self.max_tasks = 2**16
		
		
	def generate_task_id(self):
		rv = random.randint(1,self.max_tasks)
		if len(self.tasks) >= self.max_tasks:
			raise RangeError("Maximum number of tasks exceeded")
		while rv in self.tasks:
			rv += 1
			if rv > self.max_tasks:
				rv = 1
		
		return rv
		
	
	def spawn_cmd_task(self, bytecode, vars):
		task = VMTask(self.generate_task_id(), bytecode, vars)
		self.tasks[task.task_id] = task
		heapq.heappush(self.active_task_heap, (time.time(), task.task_id, task))
		
	def spawn_forked_task(self, bytecode, vars):
		task = VMTask(self.generate_task_id(), bytecode, vars)
		self.tasks[task.task_id] = task
		heapq.heappush(self.next_task_heap, (time.time(), task.task_id, task))
		
	def code_pop(self):
		return self.task.code_stack.pop()
		
	def code_push(self, code):
		if isinstance(code, list):
			for op in reversed(code):
				self.task.code_stack.append(op)
		else:
			self.task.code_stack.append(code)
		
	def exc_pop(self):
		return self.task.exc_stack.pop()
		
	def exc_push(self, exc):
		self.task.exc_stack.append(exc)
		
	def pop(self, count=1):
		stack = [uncoerce(self.task.stack.pop()) for x in xrange(count)]
		return [x for x in reversed(stack)]

	def pop_raw(self, count=1):
		stack = [self.task.stack.pop() for x in xrange(count)]
		return [x for x in reversed(stack)]
		
	def push(self, value):
		self.task.stack.append(coerce(value))
	
	def setvar(self, varname, val):
		self.task.context().variables[varname] = val
		
	def getvar(self, varname):
		return self.task.context().variables[varname]
		
	def push_context(self):
		self.task.contexts.append(VMContext())
	
	def pop_context(self):
		self.task.contexts.pop()
		
		if not self.task.contexts:
			del self.tasks[self.active_task_id]
			self.active_task_id = None
			self.task = None
			self.finished_start_next()
		
	def suspend_start_next(self, delay):
		now = time.time()
		newtask = heapq.heappop(self.active_task_heap)
		heapq.heappush(self.next_task_heap, (now+max(0.0,delay), self.active_task_id, self.task))
		return self.activate_task(newtask)
		
	def finished_start_next(self):
		if self.active_task_heap:
			now = time.time()
			newtask = heapq.heappop(self.active_task_heap)
			return self.activate_task(newtask)
		elif self.next_task_heap:
			now = time.time()
			newtask = heapq.heappop(self.next_task_heap)
			return self.activate_task(newtask)
			
	
	def activate_task(self, task):
		now = time.time()
		if now < task[0]:
			"task isn't ready to execute yet"
			self.sleepytime = task[0] - now
			heapq.heappush(self.next_task_heap, task)
			return False
			
		self.active_task_id = task[1]
		self.task = task[2]
		self.ticks_used = 0
	
	def uncaught_exception(self):
		for exc in self.task.exc_stack:
			print "Unhandled exception: %s" % (exc,)
	
	def run_active_task(self):
		task_id = self.active_task_id
		while task_id == self.active_task_id and self.task.code_stack:
			nextop = self.code_pop()
			self.execute(nextop)
		
		if self.task.exc_stack:
			self.uncaught_exception()
			self.finished_start_next()
			
		if task_id == self.active_task_id:
			self.finished_start_next()
			
	
	def run(self):
		self.sleepytime = None
		if self.active_task_id == None:
			self.finished_start_next()
			if self.active_task_id == None:
				"vm is idle"
				return
		self.run_active_task()
		
	
	def jump(self, target):
		while self.task.code_stack:
			nextop = self.code_pop()
			if isinstance(nextop, EndBlock):
				if nextop.label == target:
					self.execute(nextop)
					break

	def jump_code(self, target):
		while self.code_stack:
			nextop = self.code_pop()
			if type(nextop) == target:
				if isinstance(nextop, target):
					self.execute(nextop)
					break
			if isinstance(nextop, EndBlock):
				if nextop.label == target:
					break

		
	def raise_exc(self, exc=None):
		if exc != None:
			self.exc_push(exc)
			
		while self.code_stack:
			nextop = self.code_pop()
			if isinstance(nextop, ExcHandlerBlock):
				break
			elif isinstance(nextop, FinallyBlock):
				break

		self.execute(nextop)
	
	def execute(self, op):
		self.ticks_used += op.ticks()
		if self.ticks_used > self.max_ticks:
			"ran out of ticks"
			"resource exceptions cannot be caught, so stop execution immediately"
			self.exc_push(errors.E_TICKS)
			self.uncaught_exception()
			self.finished_start_next()
		else:
			print "executing %s with stack %s" % (op, self.task.stack)
			#op.load_stack(self)
			op.execute(self)
			
	def test(self):
		import parse
		testcode = parse.static_parser.test()
		self.spawn_forked_task(testcode, {})
		self.run()
			
static_vm = VirtualMachine(None)
			
if __name__ == "__main__":
	static_vm.test()