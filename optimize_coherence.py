import utils
import time

t1=time.time()

m1="Jamaica"
m2="Nikola_Grueki"
print(str(utils.neo4jPath(m1, m2)))

t2=time.time()
print(t2-t1)

import redis
rds=redis.Redis()
t3=time.time()
print(rds.get('%s:United_States' % m1))
t4=time.time()
print(t4-t3)
