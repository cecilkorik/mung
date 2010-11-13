import os, sys, time
from listener import Listener

class Server(object):
	def __init__(self, dbname):
		self.dbname = dbname
		self.listeners = []

	def listen(self, addr, port):
		l = Listener()
		l.listen(addr, port)
		self.listeners.append(l)
	
	def mainloop(self):
		while True:
			for l in self.listeners:
				l.handle_incoming_connections()
				l.scan_for_input(self.read_input)
			time.sleep(2)


	def read_input(self, conn, data):
		ds = data.split('\n')
		if ds[-1] == '':
			del ds[-1]
		for line in ds:
			print "%s: %s" % (conn.id, line)

if __name__ == "__main__":
	srv = Server("Test")
	srv.listen("", 7878)
	srv.mainloop()
