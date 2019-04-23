try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO


class FullBufferError(Exception):
	
class RingBuffer(object):
	def __init__(self, size, overflow=True):
		self.size = size
		self.buffer = StringIO()
		self.buffer_pos = 0
		self.read_pos = 0
		self.bytes_written = 0
		self.first_read = True
		self.allow_overflow = overflow
		self.emptyclass = RingBuffer
		self.fullclass = RingBufferFull
		self.empty = True
		
	def sizeleft(self):
		return self.size - self.buffer_pos + self.read_pos
		
	def bytes_waiting(self):
		return self.size - self.sizeleft()

	def write(self, data):
		if data:
			self.empty = False
		ld = len(data)
		if ld > self.sizeleft() and not self.allow_overflow:
			raise FullBufferError("Data would overflow the buffer")
		if self.buffer_pos + ld >= self.size:
			self.__class__ = self.fullclass
			split = self.size - self.buffer_pos
			self.buffer.write(data[:split])
			self.buffer.seek(0, 0)
			self.buffer_pos = 0
			self.bytes_written += split
			self.write(data[split:])
		else:
			self.buffer.write(data)
			self.buffer_pos += len(data)
			self.bytes_written += len(data)
		
	def read(self, bytes=0):
		self.buffer.seek(self.read_pos, 0)
		maxbytes = self.bytes_waiting()
		if bytes > 0 and bytes < maxbytes:
			maxbytes = bytes
			
		rb = self.buffer.read(maxbytes)
		self.read_pos = self.buffer.tell()
		self.buffer.seek(self.buffer_pos, 0)
		
		if self.read_pos == self.buffer_pos:
			self.empty = True
		return rb

	def rewind(self, bytes):
		if bytes > self.read_pos:
			raise ValueError("Buffer is not big enough to rewind that far")
		
		self.read_pos -= bytes
		if bytes > 0:
			self.empty = False
			
		

class SplitRingBuffer(RingBuffer):
	def __init__(self, size, split, overflow=True):
		RingBuffer.__init__(self, size, overflow)
		self.emptyclass = SplitRingBuffer
		self.fullclass = SplitRingBufferFull
		self.splitpos = split
		self.read_pos = split
	
	def read_head():
		self.buffer.seek(0, 0)
		rb = self.buffer.read()
		self.buffer.seek(self.buffer_pos, 0)
		return (True, rb)
		

class RingBufferFull(object):
	def __init__(self, size):
		raise NotImplementedError("You should not create this class manually, use RingBuffer() instead")
	
	def overflow_buffer():
		self.buffer_pos = 0
		self.seek_to_start()
		
	def seek_to_start():
		self.buffer.seek(0, 0)

	def sizeleft(self):
		if self.read_pos == None:
			return self.size
		elif self.read_pos == self.buffer_pos and self.empty:
			return self.size
		elif self.read_pos == self.buffer_pos:
			return 0
		elif self.read_pos < self.buffer_pos:
			return self.size - self.buffer_pos + self.read_pos
		else:
			return self.read_pos - self.buffer_pos
				
	def write(self, data):
		if data:
			self.empty = False

		di = 0
		ld = len(data)

		# check for overflow before we start
		if ld > self.sizeleft() and not self.allow_overflow:
			# overflow will happen, raise an exception
			raise FullBufferError("Data would overflow the buffer")

		while (ld - di) + self.buffer_pos >= self.size:
			# write data from the current buffer_pos all the way to the end of the ringbuffer
			self.buffer.write(data[di:di + (self.size - self.buffer_pos)])
			
			if self.read_pos != None and self.read_pos > self.buffer_pos:
				# our read pos was between the buffer_pos and the end. since we just overwrote 
				# all that, it has been overwritten and we've lost our place, doh!
				self.read_pos = None
			self.overflow_buffer()
			di += (self.size - self.buffer_pos)
		
		# no more writing past the end of the buffer, now we can just do a simple write
		self.buffer.write(data[di:])
		if self.read_pos != None and self.buffer_pos <= self.read_pos and (self.buffer_pos + ld - di) > self.read_pos:
			self.read_pos = None
		self.buffer_pos += ld - di
		self.bytes_written += ld
	
	def read(self, bytes=0):
		pos = self.read_pos
		fullread = False
		if pos == None:
			pos = self.buffer_pos
			
		maxlen = self.bytes_waiting()
		self.buffer.seek(pos, 0)
		if bytes > 0 and maxlen > bytes:
			maxlen = bytes
		
		if maxlen == 0:
			return ''
		
		split = self.size - pos
		if split >= maxlen:
			self.buffer.seek(pos, 0)
			rb = self.buffer.read(maxlen)
			self.read_pos = self.buffer.tell()
			self.buffer.seek(self.buffer_pos, 0)
		else:
			self.buffer.seek(pos, 0)
			rb = self.buffer.read(split)
			self.seek_to_start()
			rb += self.buffer.read(maxlen - split)
			self.read_pos = self.buffer.tell()
			self.buffer.seek(self.buffer_pos, 0)
		
		if self.read_pos == self.buffer_pos and bytes > 0:
			"we've read everything out of the buffer"
			self.empty = True
			
		return rb

	def rewind(self, bytes):
		if bytes > self.sizeleft():
			raise ValueError("Buffer is not big enough to rewind that far")
		
		self.read_pos -= bytes
		if self.read_pos < 0:
			self.read_pos += self.size

		if bytes > 0:
			self.empty = False




class SplitRingBufferFull(RingBufferFull):
	def read(self, bytes=0):
		pass

	def overflow_buffer():
		self.buffer_pos = self.split_pos
		
	def seek_to_start():
		self.buffer.seek(self.split_pos, 0)

	def read_head():
		self.buffer.seek(0, 0)
		rb = self.buffer.read(self.split_pos)
		self.buffer.seek(self.buffer_pos, 0)
		return (False, rb)
		
		