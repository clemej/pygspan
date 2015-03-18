

class Edge():
	def __init__(self):
		self.id = None
                self.fromn = None
		self.to = None
		self.label = None

class Node():
	def __init__(self):
		self.id = None
		self.label = None
		self.edges = []

class Graph():
	def __init__(self):
		self.id = None
		self.nedges = 0
		self.nodes = []

	def gprint(self, nsupport):
		edges = []
		ret = 't # %d * %d\n' % (self.id, nsupport)
		for n in sorted(self.nodes, key=lambda x: x.id):
			ret += 'v %d %d\n' % (n.id, n.label)
			for e in n.edges:
				if e.id in [x.id for x in edges]:
					continue
				edges.append(e)
		for e in sorted(edges, key=lambda x: x.fromn):
			ret += 'e %d %d %d\n' % (e.fromn, e.to, e.label)

		print ret

	def __repr__(self):
		edges = []
		ret = 't # %d\n' % (self.id)
		for n in sorted(self.nodes, key=lambda x: x.id):
			ret += 'v %d %d\n' % (n.id, n.label)
			for e in n.edges:
				if e.id in [x.id for x in edges]:
					continue
				edges.append(e)
		for e in sorted(edges, key=lambda x: x.fromn):
			ret += 'e %d %d %d\n' % (e.fromn, e.to, e.label)

		return ret


