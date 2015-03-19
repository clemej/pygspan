import sys
import os

import fileio
import gspan

if __name__ == '__main__':
	print 'Database: ', sys.argv[1]
	database = fileio.read_file(sys.argv[1])
	print 'Number Graphs Read: ', len(database)
	print 'Support: ', sys.argv[2],
	minsup = int(1+(float(sys.argv[2])*len(database)))
	print minsup
	database, freq, trimmed, flabels = gspan.trim_infrequent_nodes(database, minsup)
	database = fileio.read_file(sys.argv[1], frequent = freq)
	print 'Trimmed ', len(trimmed), ' labels from the database'
	print flabels
	gspan.project(database, freq, minsup, flabels)

