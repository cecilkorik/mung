from pyparsing import ParseResults

def flatten_orig(l, ltypes=(list, tuple)):
	ltype = type(l)
	l = list(l)
	i = 0
	while i < len(l):
		while isinstance(l[i], ltypes):
			if not l[i]:
				l.pop(i)
				i -= 1
				break
			else:
				l[i:i + 1] = l[i]
		i += 1
	return ltype(l)

def bytecode_flatten(l, ltypes=(list, tuple, ParseResults)):
	l = list(l)
	i = 0
	while i < len(l):
		broken = False
		while isinstance(l[i], ltypes):
			if not l[i]:
				l.pop(i)
				broken = True
				break
			else:
				l[i:i + 1] = list(l[i])
		if broken:
			continue
		assert not isinstance(l[i], ltypes)
		assert not isinstance(l[i], (str, unicode, dict))
		bc = l[i].bytecode()
		if len(bc) > 1 or bc[0] != l[i]:
			l[i:i+1] = bc
			continue
		i += 1
	return l

def optimize(data):
	"""
	yeah, this is some pretty intense optimiziation, I know... 
	it will hopefully be expanded on later...
	"""
	
	data = bytecode_flatten(data)
	
	for x in data:
		if not hasattr(x, "pos"):
			print("Missing position on element %s" % (x,))
	
	return data
		