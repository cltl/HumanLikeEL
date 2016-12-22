import networkx as nx
import time

MILLION=1000000

t1=time.time()
g=nx.dense_gnm_random_graph(5*MILLION, 125*MILLION)
t2=time.time()
print(t2-t1)

t3=time.time()
nx.shortest_path_length(g, source=111111, target=4040400)
t4=time.time()
print(t4-t3)

