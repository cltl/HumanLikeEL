import time
from py2neo import Graph

def commonNeighbors(n1, n2):

	query="""MATCH (source:Page {name:\"%s\"})--(neighbor)--(target:Page {name:\"%s\"})
	RETURN count(neighbor) AS common_neighbors""" % (n1, n2)
	gn=Graph()
	result=gn.run(query).evaluate()
	return result
t1=time.time()
x=commonNeighbors('Jamaica', 'John_Travolta')
t2=time.time()
print(t2-t1)
print(x)
