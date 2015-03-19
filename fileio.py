import graph
import sys

def read_file(filename, frequent=[]):
	ret = []

	count = 0
	id_map = {}
	node_id = 0
	labels = []
	
	for line in open(filename, 'r'):
		if line[0] == 't':
			if count > 0:
				ret.append(g)
				id_map = {}
				labels = []
				node_id = 0
				edge_id = 0

			g = graph.Graph()
			g.id = count
			count += 1
			continue

		if line[0] == 'v':
			nid, label = [int(x) for x in line.split()[1:]]
			labels.append(label)
			if len(frequent) > 0:
				if label not in frequent:
					#print 'deleting node',g.id,nid,label
					continue
				
			n = graph.Node()
			n.id = node_id
			n.label = label
			id_map[nid] = node_id
			g.nodes.append(n)
			node_id += 1
			continue

		if line[0] == 'e':
			fromn, to, label = [int(x) for x in line.split()[1:]]
			label_from = labels[fromn]
			label_to = labels[to]
			if len(frequent) > 0:
				if label_from not in frequent or \
						label_to not in frequent:
					#print 'deleting edge',g.id, fromn, to, label
					continue

			e = graph.Edge()
			e.id = g.nedges
			g.nedges += 1
			e.fromn = id_map[fromn]
			e.to = id_map[to]
			e.label = label

			g.nodes[e.fromn].edges.append(e)

			e2 = graph.Edge()
			e2.fromn = e.to
			e2.to = e.fromn
			e2.label = e.label
			e2.id = e.id
			g.nodes[e.to].edges.append(e2)		

	ret.append(g)
	return ret
