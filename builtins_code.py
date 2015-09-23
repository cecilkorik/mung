
class builtin_functions(object):
	def __init__(self):
		pass
		
	@staticmethod
	def serverlog(vm, args):
		print "serverlog: %s" % (args,)

bi = builtin_functions()

