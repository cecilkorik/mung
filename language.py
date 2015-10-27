import sys
import time
import bisect
import optimizer
import traceback
from pyparsing import ParseException
from language_types import *
from bytecode import *

class PropertyStorage(object):
	def __init__(self):
		self.name = None
		self.flags = ""
		self.owner = None
		self.value = None

class FileStorage(object):
	def __init__(self):
		self.name = None
		self.flags = ""
		self.owner = None
		self.filepath = None

class FunctionStorage(object):
	def __init__(self):
		self.name = None
		self.flags = ""
		self.owner = None
		self.bytecode = []
		
		
class ObjectStorage(object):
	def __init__(self):
		self.props = []
		self.files = []
		self.funcs = []


