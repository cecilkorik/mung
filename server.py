import os, sys, time
from listener import Listener
from language import VirtualMachine
from database_fake import Fake_Database as Database

class Server(object):
	def __init__(self, dbname):
		self.dbname = dbname
		self.db = Database(dbname)
		self.vm = VirtualMachine(self.db)
		self.max_sleep = 0.1
		self.min_sleep = 0.005
		self.vm_sleep_fudge = 0.85
		self.server_started = None
		self.loop_started = None
		self.listeners = []

	def listen(self, addr, port):
		l = Listener()
		l.listen(addr, port)
		self.listeners.append(l)
	
	def mainloop(self):
		self.server_started = time.time()
		while True:
			self.loop_started = time.time()
			for l in self.listeners:
				l.handle_incoming_connections()
				l.scan_for_input(self.read_input)
			self.vm.run()
			for l in self.listeners:
				l.flush_output()
			self.idlewait()


	def read_input(self, conn, data):
		ds = data.split('\n')
		if ds[-1] == '':
			del ds[-1]
		for line in ds:
			print "%s: %s" % (conn.id, line)
			
	def idlewait(self):
		if self.vm.sleepytime == None:
			"virtual machine is still busy anyway, no sleeping on the job!"
			return
		
		"also check how much time we have spent already. if it's already been our polling"
		"time (or longer!), there's no sense waiting even more!"
		time_already_spent = time.time() - self.loop_started
		
		sleepytime = min(self.max_sleep - time_already_spent, self.vm.sleepytime * self.vm_sleep_fudge)
		if sleepytime < self.min_sleep or sleepytime < 0.0:
			return
			
		time.sleep(sleepytime)
		
		

if __name__ == "__main__":
	srv = Server("Test")
	srv.listen("", 7878)
	srv.mainloop()
