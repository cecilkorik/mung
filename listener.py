import os, sys, time
import socket
import select
import random

class Connection(object):
	def __init__(self, id, conn, addr):
		self.id = id
		self.conn = conn
		self.addr = addr
		self.input_encoding = 'raw'
		self.output_encoding = 'ascii'
		self.linebuffer = True

	def fileno(self):
		return self.conn.fileno()

	def escape(self, data):
		bytes = map(ord, data)
		for i, byte in enumerate(bytes):
			if byte > 32 and byte < 125:
				bytes[i] = chr(byte)
			elif byte == 10 and self.linebuffer:
				bytes[i] = chr(byte)
			else:
				bytes[i] = "~%x" % (byte,)
		return "".join(bytes)


	def recv(self, bytes=4096):
		data = self.conn.recv(bytes)

		if self.input_encoding == 'raw':
			return unicode(self.escape(data), 'ascii')
		else:
			return unicode(data, self.input_encoding, 'ignore')


class Listener(object):
	def __init__(self):
		self.socket = None
		self.bind_addr = None
		self.bind_port = None
		self.connections = {}
		self.connection_list = []
		self.connection_list_dirty = False

		self.MAX_CONN = 3000

	def listen(self, addr, port):
		if self.socket != None:
			raise ValueError("Already listening on %s:%d" % (self.bind_addr, self.bind_port))

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		s.bind((addr, port))
		self.bind_addr = addr
		self.bind_port = port

		s.setblocking(0)
		s.listen(1)
		self.socket = s

	def add_connection(self, conn, addr):
		addr = "%s:%d" % addr
		while True:
			connid = random.randint(1, 65535)

			if not connid in self.connections:
				print "%s connected from %s" % (connid, addr)
				self.connections[connid] = Connection(connid, conn, addr)
				self.connection_list_dirty = True
				break


	def delete_connection(self, conn):
		print "%s disconnected." % (conn.id,)
		del self.connections[conn.id]
		self.connection_list_dirty = True
	
	def all_connections(self):
		if self.connection_list_dirty:
			self.connection_list = self.connections.values()
			self.connection_list_dirty = False

		return self.connection_list


	def handle_incoming_connections(self):
		while True:
			r, w, x = select.select([self.socket], [], [], 0)

			if not r:
				break

			conn, addr = self.socket.accept()
			conn.setblocking(0)

			if len(self.connections) < self.MAX_CONN:
				self.add_connection(conn, addr)
			else:
				conn.close()



	def scan_for_input(self, callback):
		r, w, x = select.select(self.all_connections(), [], [], 0)
		for conn in r:
			input = conn.recv()
			if input == '':
				self.delete_connection(conn)
			else:
				callback(conn, input)

	def shutdown(self):
		for x in self.connection_list:
			x.conn.close()
	

if __name__ == "__main__":
	l = Listener()
	l.listen("", 7878)
	print "Listening on %s:%d" % (l.bind_addr, l.bind_port)
	
	try:
		while True:
			l.handle_incoming_connections()
			l.scan_for_input()
			time.sleep(1)
	finally:
		l.shutdown()
			


