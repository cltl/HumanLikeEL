import utils
import time
from multiprocessing.dummy import Pool as ThreadPool

THREADS=64

def yieldCandidatePairs():
#	p1=['France', 'Italy', 'Silvio_Berlusconi', 'North_Dakota', 'Utrecht', 'John_Travolta', 'United_States']
#	p2=['United_States_Armed_Forces', 'United_States_Forces_Korea', 'United_States_Forces_Azores', 'United_States_Forces_Japan', 'United_States_Forces_–_Iraq', 'United_States_Joint_Forces_Command', 'United_States_Naval_Forces_Europe', 'United_States_Air_Forces_Central_Command', 'United_States_Army_Forces_Command', 'United_States_Fleet_Forces_Command', 'Ninth_Air_Force', 'United_States_Africa_Command', 'United_States_special_operations_forces']
	p1=['Mandan,_North_Dakota', 'Mandan']
	p2=['North_Dakota', 'Louisiana']
	print(len(p1), len(p2), len(p1)*len(p2))
	for m1 in p1:
		for m2 in p2:
			yield (m1,m2)

pool = ThreadPool(THREADS)
iterablePairs = yieldCandidatePairs()
t1=time.time()
results = pool.map(utils.neo4jPath, iterablePairs)
print(results)
t2=time.time()
print(t2-t1)
