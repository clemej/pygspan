#
# gspan.py : An non-Pythonic implementation of gSpan
# 
# This is not how you would write gspan in python. It is
# some scratch code I'm writing as an experiment to help me
# understand gspan better to write a C implementation.
# 
# Author: John Clemens <john at deater.net>
# Copyright (c) 2015 
# 
# This is a Python port of the C++ implementation of gSpan found
# here: https://github.com/Jokeren/DataMining-gSpan
#

import graph
import functools
import collections

__subgraph_count = 0

# 
# I'm using a couple of structs as named tuples here. This takes care of the
# __eq__ functions that are needed for fds_code to be used as a ditionary key
#
pre_dfs = collections.namedtuple('pre_dfs',['id','edge','prev'])
dfs_code = collections.namedtuple('dfs_code',
			['fromn','to','from_label','edge_label','to_label'])

# 
# These are the comparison functions for sorting the order the keys are
# traversed in the dictionary
#
def dfs_code_compare(a):
	return (a.from_label, a.edge_label, a.to_label)

def dfs_code_backward_compare(a):
	return (a.to, a.edge_label)

def dfs_code_forward_compare(a):
	return (-a.fromn, a.edge_label, a.to_label)

# One class here to maintain the history information. 
class history():
	def __init__(self):
		self.edges = []
		self.has_edges = set()
		self.has_node = set()

	def build(self, pdfs):
		ps = pdfs
		while ps != None:
			self.edges.append(ps.edge)
			self.has_edges.add(ps.edge.id)
			self.has_node.add(ps.edge.fromn)
			self.has_node.add(ps.edge.to)
			ps = ps.prev
		self.edges = list(reversed(self.edges))

# 
# Calculates the freqent labels
#
def trim_infrequent_nodes(database, minsup):
	totrim = []
	frequent = []
	freq_labels = {}

	for g in database:
		nset = set()

		for n in g.nodes:
			nset.add(n.label)

		for l in list(nset):
			if l in freq_labels:
				freq_labels[l] += 1
			else:
				freq_labels[l] = 1

	for label in freq_labels:
		if freq_labels[label] < minsup:
			totrim.append(label)
		else:
			frequent.append(label)
	print frequent
	print totrim
	return database, frequent, totrim, freq_labels

#
# Build the right most path through the DFS codes 
# 
def build_right_most_path(dfs_codes):
	path = []
	prev_id = -1
	#print list(reversed(list(enumerate(dfs_codes))))
	for idx,c in reversed(list(enumerate(dfs_codes))):
		if c.fromn < c.to and (len(path) == 0 or prev_id == c.to):
			prev_id = c.fromn
			path.append(idx)
	#print path
	return path

# 
# Iterate through the projection to find potential next edges (?)
#
def genumerate(projection, right_most_path, dfs_codes, min_label, db):
	#print min_label, len(projection)
	pm_backward = {}
	pm_forward = {}

	for p in projection:
		h = history()
		h.build(p)

		#print p.id, p.edge.fromn, p.edge.to, p.prev
		pm_backward = get_backward(p, right_most_path, h, pm_backward, 
						dfs_codes, db)
		pm_forward = get_first_forward(p, right_most_path, h, pm_forward,
						dfs_codes, db, min_label)
		pm_forward = get_other_forward(p, right_most_path, h, pm_forward,
						dfs_codes, db, min_label)
	return pm_backward, pm_forward

#
# Get initial edges from the graph to grow.
#
def get_forward_init(node, graph):
	edges = []
	
	for e in node.edges:
		if node.label <= graph.nodes[e.to].label:
			edges.append(e)
	return edges

#
# Search to backward edges as potential next edges
#
def get_backward(prev_dfs, right_most_path, hist, pm_backward, dfs_codes, db):
	last_edge = hist.edges[right_most_path[0]]
	g = db[prev_dfs.id]
	last_node = g.nodes[last_edge.to]

	for idx,rmp in reversed(list(enumerate(right_most_path[1:]))):
		edge = hist.edges[rmp]

		for e in last_node.edges:
			if e.id in hist.has_edges:
				continue
			if e.to not in hist.has_node:
				continue
			#print 'here3'
			from_node = g.nodes[edge.fromn]
			to_node = g.nodes[edge.to]
			#print 'here3',g.id,last_edge.fromn,last_edge.to,last_node.id, edge.fromn, edge.to, edge.label, idx, from_node.id, to_node.id
			if e.to == edge.fromn and (e.label > edge.label or (e.label == edge.label and last_node.label >= to_node.label)):
				#print 'here4'
				from_id = dfs_codes[right_most_path[0]].to
				to_id = dfs_codes[rmp].fromn
				
				dfsc = dfs_code(from_id, to_id, last_node.label, e.label, from_node.label)
				pdfs = pre_dfs(g.id, e, prev_dfs)
				
				if dfsc in pm_backward:
					pm_backward[dfsc].append(pdfs)
				else:
					pm_backward[dfsc] = [pdfs,]
	
	return pm_backward

#
# Find the first forward edge as a next edge
# 
def get_first_forward(prev_dfs, right_most_path, hist, pm_forward, dfs_codes, db, min_label):
	last_edge = hist.edges[right_most_path[0]]
	g = db[prev_dfs.id]
	last_node = g.nodes[last_edge.to]

	for e in last_node.edges:
		to_node = g.nodes[e.to]
		
		if e.to in hist.has_node or to_node.label < min_label:
			continue

		to_id = dfs_codes[right_most_path[0]].to
		dfsc = dfs_code(to_id, to_id+1, last_node.label, e.label, to_node.label)

		pdfs = pre_dfs(g.id,e,prev_dfs)

		if dfsc in pm_forward:
			pm_forward[dfsc].append(pdfs)
		else:
			pm_forward[dfsc] = [pdfs,]

	return pm_forward
#
# Append any other forward edges as potential next edges
# 
def get_other_forward(prev_dfs, right_most_path, hist, pm_forward, dfs_codes, db, min_label):
	g = db[prev_dfs.id]

	for rmp in right_most_path:
		cur_edge = hist.edges[rmp]
		cur_node = g.nodes[cur_edge.fromn]
		cur_to = g.nodes[cur_edge.to]

		for e in cur_node.edges:
			to_node = g.nodes[e.to]
			
			if to_node.id == cur_to.id or to_node.id in hist.has_node or to_node.label < min_label:
				continue

			if cur_edge.label < e.label or (cur_edge.label == e.label and cur_to.label <= to_node.label):
				from_id = dfs_codes[rmp].fromn
				to_id = dfs_codes[right_most_path[0]].to

				dfsc = dfs_code(from_id, to_id+1, cur_node.label, e.label, to_node.label)
				pdfs = pre_dfs(g.id,e,prev_dfs)

				if dfsc in pm_forward:
					pm_forward[dfsc].append(pdfs)
				else:
					pm_forward[dfsc] = [pdfs,]

	return pm_forward

#
# Count how many graphs this projection shows up (?)
#
def count_support(projection):
	prev_id = -1
	size = 0

	for p in projection:
		if prev_id != p.id:
			prev_id = p.id
			size += 1
	return size

#
# Build a graph for a given set of dfs codes. 
#
def build_graph(dfs_codes):
	g = graph.Graph()

	numnodes = max([x[0] for x in dfs_codes] + [x[1] for x in dfs_codes])+1
	for i in range(numnodes):
		n = graph.Node()
		g.nodes.append(n)

	for idx,c in enumerate(dfs_codes):
		g.nodes[c.fromn].id = c.fromn
		g.nodes[c.fromn].label = c.from_label
		g.nodes[c.to].id = c.to
		g.nodes[c.to].label = c.to_label

		e = graph.Edge()
		e.id = g.nedges
		e.fromn = c.fromn
		e.to = c.to
		e.label = c.edge_label
		g.nodes[c.fromn].edges.append(e)

		e2 = graph.Edge()
		e2.id = e.id
		e2.label = e.label
		e2.fromn = c.to
		e2.to = c.fromn
		g.nodes[c.to].edges.append(e2)

		g.nedges += 1

	return g

#
# Check if a given DFS code is a minimum DFS code. Recursive.
#
def is_min(dfs_codes):

	if len(dfs_codes) == 1:
		return True

	min_dfs_codes = []
	mingraph = build_graph(dfs_codes)
	
	projection_map = {}
	for n in mingraph.nodes:
		edges = []
		edges += get_forward_init(n, mingraph)
		if len(edges) > 0:
			 for e in edges:
				nf = mingraph.nodes[e.fromn]
				nt = mingraph.nodes[e.to]
				dfsc = dfs_code(0,1,nf.label,e.label,nt.label)

				pdfs = pre_dfs(0,e,None)

				if dfsc in projection_map:
					projection_map[dfsc].append(pdfs)
				else:
					projection_map[dfsc] = [pdfs,]

	pm = sorted(projection_map, key=dfs_code_compare)[0]
	min_dfs_codes.append(dfs_code(0,1,pm[2],pm[3],pm[4]))
	if dfs_codes[len(min_dfs_codes)-1] != min_dfs_codes[-1]:
		return False

	return projection_min(projection_map[pm], dfs_codes, min_dfs_codes, mingraph)

def judge_backwards(right_most_path, projection, min_dfs_codes, min_label, mingraph):
	pm_backwards = {}

	for idx, c in reversed(list(enumerate(right_most_path[1:]))):
		for j in projection:
			h = history()
			h.build(j)
			
			last_edge = h.edges[right_most_path[0]]
			last_node = mingraph.nodes[last_edge.to]

			edge = h.edges[right_most_path[idx]]
			to_node = mingraph.nodes[edge.to]
			from_node = mingraph.nodes[edge.fromn]

			for e in last_node.edges:
				if e.id in h.has_edges:
					continue
				if e.to not in h.has_node:
					continue
				if e.to == edge.fromn and (e.label > edge.label or (e.label == edge.label and last_node.label > to_node.label)):
					from_id = min_dfs_codes[right_most_path[0]].to
					to_id = min_dfs_codes[right_most_path[idx]].fromn

					dfsc = dfs_code(from_id, to_id, last_node.label, e.label, from_node.label)
					pdfs = pre_dfs(0,e,j)

					if dfsc in pm_backwards:
						pm_backwards[dfsc].append(pdfs)
					else:
						pm_backwards[dfsc] = [pdfs,]

		if len(pm_backwards.keys()) != 0: 
			return True, pm_backwards

	return False, pm_backwards

#
# Used to 
#
def judge_forwards(right_most_path, projection, min_dfs_codes, min_label, mingraph):
	
	pm_forward = {}

	for idx,p in enumerate(projection):
		h = history()
		h.build(p)

		last_edge = h.edges[right_most_path[0]]
		last_node = mingraph.nodes[last_edge.to]

		for e in last_node.edges:
			to_node = mingraph.nodes[e.to]

			if e.to in h.has_node or to_node.label < min_label:
				continue

			to_id = min_dfs_codes[right_most_path[0]].to
			dfsc = dfs_code(to_id, to_id+1, last_node.label, e.label, to_node.label)
			pdfs = pre_dfs(0,e,p)

			if dfsc in pm_forward:
				pm_forward[dfsc].append(pdfs)
			else:
				pm_forward[dfsc] = [pdfs,]
	
	if len(pm_forward.keys()) == 0:
		for rmp in right_most_path:
			for p in projection:
				h = history()
				h.build(p)

				cur_edge = h.edges[rmp]
				cur_node = mingraph.nodes[cur_edge.fromn]
				cur_to = mingraph.nodes[cur_edge.to]
				
				for e in cur_node.edges:
					to_node = mingraph.nodes[e.to]
					
					if cur_edge.to == to_node.id or to_node.id in h.has_node or to_node.label < min_label:
						continue

					if cur_edge.label < e.label or (cur_edge.label == e.label and cur_to.label <= to_node.label):
						from_id = min_dfs_codes[rmp].fromn
						to_id = min_dfs_codes[right_most_path[0]].to
						dfsc = dfs_code(from_id, to_id+1, cur_node.label, e.label, to_node.label)

						pdfs = pre_dfs(0,e,p)
						
						if dfsc in pm_forward:
							pm_forward[dfsc].append(pdfs)
						else:
							pm_forward[dfsc] = [pdfs,]
			
			if len(pm_forward.keys()) != 0:
				break

	if len(pm_forward.keys()) != 0:
		return True, pm_forward
	else:
		return False, pm_forward
#
# Build a minimum projection (??) 
#
def projection_min(projection, dfs_codes, min_dfs_codes, mingraph):
	right_most_path = build_right_most_path(min_dfs_codes)
	min_label = min_dfs_codes[0].from_label

	ret, pm_backward = judge_backwards(right_most_path, projection, min_dfs_codes, min_label, mingraph)
	#print ret,pm_backward.keys()
	if ret:
		for pm in sorted(pm_backward, key=dfs_code_backward_compare):
			#print '--- ',pm
			min_dfs_codes.append(pm)
			if dfs_codes[len(min_dfs_codes)-1] != min_dfs_codes[-1]:
				return False

			return projection_min(pm_backward[pm], dfs_codes, min_dfs_codes, mingraph)
	
	ret, pm_forward = judge_forwards(right_most_path, projection, min_dfs_codes, min_label, mingraph)
	if ret:
		for pm in sorted(pm_forward, key=dfs_code_forward_compare):
			min_dfs_codes.append(pm)
			if dfs_codes[len(min_dfs_codes)-1] != min_dfs_codes[-1]:
				return False

			return projection_min(pm_forward[pm], dfs_codes, min_dfs_codes,mingraph)
	return True

#
# Draw a frequent subgraph with its support.
# 
def show_subgraph(dfs_codes, nsupport):
	global __subgraph_count

	g = build_graph(dfs_codes)
	g.id = __subgraph_count
	__subgraph_count += 1
	g.gprint(nsupport)

# 
# Generate initial edges and start the mining process
#
def project(database, frequent_nodes, minsup, freq_labels):
	global __subgraph_count
	dfs_codes = []

	projection_map = {}
        
        # Print out all single-node graphs up front.	
	for l in frequent_nodes:
		print 't # %d * %d' % (__subgraph_count, freq_labels[l])
		print 'v 0 %d\n' % (l,)
		__subgraph_count += 1		

	for g in database:
		for n in g.nodes:
			#edges = []
			edges = get_forward_init(n, g)
			if len(edges) > 0:
				 for e in edges:
					nf = g.nodes[e.fromn]
					nt = g.nodes[e.to]
					dfsc = dfs_code(0,1,nf.label,e.label,nt.label)

					pdfs = pre_dfs(g.id,e,None)

					if dfsc in projection_map:
						projection_map[dfsc].append(pdfs)
					else:
						projection_map[dfsc] = [pdfs,]

	#for pm in sorted(projection_map, key=dfs_code_compare):
	#	print pm
	#print '----'
	# Start Subgraph Mining
	for pm in reversed(sorted(projection_map, key=dfs_code_compare)):
		#print pm
		# Partial pruning like apriori
		if len(projection_map[pm]) < minsup:
			continue
		
		dfs_codes.append(dfs_code(0,1,pm[2],pm[3],pm[4]))

		dfs_codes = mine_subgraph(database, projection_map[pm], 
							dfs_codes, minsup)

		dfs_codes.pop()

# 
# recursive subgraph mining routine
# 
def mine_subgraph(database, projection, dfs_codes, minsup):
	nsupport = count_support(projection) 
	if nsupport < minsup:
		return dfs_codes

	if not is_min(dfs_codes):
		return dfs_codes

	show_subgraph(dfs_codes, nsupport)

	right_most_path = build_right_most_path(dfs_codes)
	min_label = dfs_codes[0].from_label
	
	pm_backward, pm_forward = genumerate(projection, right_most_path, dfs_codes, min_label, database)
	#print pm_backward.keys()
	
	#print '-----'
	#for pm in sorted(pm_backward, key=dfs_code_backward_compare):
	#	print pm
	#print '-'
	#for pm in reversed(sorted(pm_forward, key=dfs_code_forward_compare)):
	#	print pm
	#print '------'

	for pm in sorted(pm_backward, key=dfs_code_backward_compare):
		dfs_codes.append(pm)
		dfs_codes = mine_subgraph(database, pm_backward[pm], dfs_codes, minsup)
		dfs_codes.pop()

	for pm in reversed(sorted(pm_forward, key=dfs_code_forward_compare)):
		dfs_codes.append(pm)
		dfs_codes = mine_subgraph(database, pm_forward[pm], dfs_codes, minsup)
		dfs_codes.pop()

	return dfs_codes
	
