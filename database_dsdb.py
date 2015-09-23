# Dead Simple Database

class DSDB_Database(Database):
	def __init__(self, dbname):
		self.dbname = dbname
		self.fn = "%s.dsdb" % (dbname,)
		self.load_from_file()
	
	def load_from_file(self):
		fd = open(self.fn, 'rb')
		fd
