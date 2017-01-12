import utils
import time

t1=time.time()

t=["Mandan,_North_Dakota", "Louisiana"]
print(str(utils.neo4jPath(t)))

t2=time.time()
print(t2-t1)

import redis
rds=redis.Redis()
t3=time.time()
print(rds.get('%s:United_States' % t[0]))
t4=time.time()
print(t4-t3)
