import os, sys, time
import socket
import select
import random
from ringbuffer import RingBuffer

class Poller(object):
	POLLIN = 1
	POLLERR = 2
	POLLRD = 3	# POLLIN | POLLERR
	POLLWR = 4
	
	def __init__(self):
		try:
			self.mode = select.poll()
			Poller.POLLIN = select
			Poller.POLLRD = select.POLLIN|select.POLLPRI|select.POLLHUP|select.POLLERR|select.POLLNVAL
			Poller.POLLWR = select.POLLOUT
		except:
			self.mode = select.select
			Poller.POLLIN = 1
			Poller.POLLERR = 2
			Poller.POLLRD = Poller.POLLIN|Poller.POLLERR
			Poller.POLLWR = 4
			
		self.registered = {}
	
	def register_read(self, listener, fd):
		if not fd in self.registered:
			self.registered[fd.fileno()] = [0, listener, fd]
		self.registered[fd.fileno()][0] |= Poller.POLLRD
		if self.mode != select.select:
			self.mode.register(fd.fileno(), Poller.POLLRD)
		
	def register_write(self, listener, fd):
		if not fd in self.registered:
			self.registered[fd.fileno()] = [0, listener, fd]
		self.registered[fd.fileno()][0] |= Poller.POLLWR
		if self.mode != select.select:
			self.mode.register(fd.fileno(), Poller.POLLRD|Poller.POLLWR)
	
	def unregister(self, fd):
		if self.mode == select.select and fd in self.registered:
			del self.registered[fd.fileno()]
		else:
			self.mode.unregister(fd.fileno())
		
	def get_fd(self, fd, flags):
		return (self.registered[fd][1], self.registered[fd][2], flags)
	
	def poll(self, timeout):
		if self.mode == select.select:
			rdfd = []
			wrfd = []
			for fd, flags in self.registered.items():
				if flags & Poller.POLLRD:
					rdfd.append(fd)
				if flags & Poller.POLLWR:
					wrfd.append(fd)
			r, w, x = select.select(rdfd, wrfd, rdfd, timeout)
			return [self.get_fd(fd, Poller.POLLIN) for fd in r] + [self.get_fd(fd, Poller.POLLWR) for fd in w] + [self.get_fd(fd, Poller.POLLERR) for fd in x]
		else:
			timeout = int(round(timeout * 1000.0, 0))
			return [self.get_fd(fd, flags) for fd, flags in self.mode.poll(timeout)]

class Connection(object):
	def __init__(self, id, conn, addr):
		self.id = id
		self.conn = conn
		self.addr = addr
		self.input_encoding = 'raw'
		self.output_encoding = 'ascii'
		self.linebuffer = True
		self.output_buffer = RingBuffer(65536, True)

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
			
	def send(self, data):
		assert isinstance(data, unicode)
		try:
			encoded = data.encode(self.output_encoding, 'replace')
		except UnicodeEncodeError:
			try:
				encoded = data.encode(self.output_encoding, 'ignore')
			except UnicodeEncodeError:
				encoded = data.encode('ascii', 'ignore')
				
		if len(encoded) > self.output_buffer.sizeleft():
			return False
			
		self.output_buffer.write(encoded)
		return True
		
	def output_waiting(self):
		return self.output_buffer.bytes_waiting() > 0
	
	def flush_buffer(self):
		if not self.output_waiting():
			return
			
		data = self.output_buffer.read()
		count = self.conn.send(data)
		if count < len(data):
			self.output_buffer.rewind(len(data) - count)
		


class Listener(object):
	def __init__(self):
		self.socket = None
		self.bind_addr = None
		self.bind_port = None
		self.connections = {}
		self.connection_list = []
		self.connection_list_dirty = False
		self.remove_from_poller = []

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
				print("%s connected from %s" % (connid, addr))
				self.connections[connid] = Connection(connid, conn, addr)
				self.connection_list_dirty = True
				break


	def delete_connection(self, conn):
		print("%s disconnected." % (conn.id,))
		del self.connections[conn.id]
		self.remove_from_poller.append(conn.conn)
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

	def send(connid, data):
		conn = self.connections[connid]
		conn.send(data)
		

	def scan_for_input(self, callback):
		r, w, x = select.select(self.all_connections(), [], [], 0)
		for conn in r:
			input = conn.recv()
			if input == '':
				self.delete_connection(conn)
			else:
				callback(conn, input)
				
	def update_poller(self, poll):
		for dconn in self.delete_from_poller:
			poll.unregister(dconn)
		self.delete_from_poller = []
		for conn in self.all_connections():
			if conn.output_waiting():
				poll.register_write(self, conn.conn)
			else:
				poll.register_read(self, conn.conn)
			
		
	
	def flush_output(self):
		for conn in self.all_connections():
			if conn.output_waiting():
				conn.flush_buffer()

	def shutdown(self):
		for x in self.connection_list:
			x.conn.close()
	

if __name__ == "__main__":
	l = Listener()
	l.listen("", 7878)
	print("Listening on %s:%d" % (l.bind_addr, l.bind_port))
	
	try:
		while True:
			l.handle_incoming_connections()
			l.scan_for_input()
			time.sleep(1)
	finally:
		l.shutdown()
			


