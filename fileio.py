import graph
import sys

def read_file(filename):
	ret = []

	count = 0

	for line in open(filename, 'r'):
		if line[0] == 't':
			if count > 0:
				ret.append(g)
			g = graph.Graph()
			g.id = count
			count += 1
			continue

		if line[0] == 'v':
			n = graph.Node()
			n.id, n.label = [int(x) for x in line.split()[1:]]
			g.nodes.append(n)
			continue

		if line[0] == 'e':
			e = graph.Edge()
			e.id = g.nedges
			g.nedges += 1
			e.fromn, e.to, e.label = [int(x) for x in line.split()[1:]]

			g.nodes[e.fromn].edges.append(e)
			e2 = graph.Edge()
			e2.fromn = e.to
			e2.to = e.fromn
			e2.label = e.label
			e2.id = e.id
			g.nodes[e.to].edges.append(e2)		

	ret.append(g)
	return ret
