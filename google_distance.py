import networkx as nx
import math
import time
import os.path

def load_wiki_edges():
	f="resources/rels.tsv"
	g=nx.Graph()
	c=0
	with open(f, 'r') as edges:
		for edge in edges:
			if c>0:
				e=edge.split()
				g.add_edge(int(e[0]), int(e[1]))
			c+=1
	return g

def compute_google_distance(g, n1, n2):
	d1=g.degree(n1)
	d2=g.degree(n2)
	common=len(list(nx.common_neighbors(g,n1, n2)))
	maxdegree=max(d1,d2)
	commondegree=max(1,common)
	mindegree=min(d1,d2)
	print(maxdegree,commondegree,mindegree)
	return (math.log(maxdegree)-math.log(commondegree))/(math.log(len(g))-math.log(mindegree))

"""
wsize=4000000
g=nx.gnm_random_graph(wsize, 125000000)
"""
graphFile='resources/wikigraph.p'
t1=time.time()
if not os.path.isfile(graphFile):
	print("Graph file not found. Constructing the wiki graph now...")
	g=load_wiki_edges()
	nx.write_gpickle(g, graphFile)
else:
	print("Graph file exists. Reading from file...")
	g=nx.read_gpickle(graphFile)
t2=time.time()
print("Time needed to load the graph", t2-t1)
t3=time.time()
print(compute_google_distance(g, 100,200))
t4=time.time()
print("Time needed to compute google distance", t4-t3)
