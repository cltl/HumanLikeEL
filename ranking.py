import redis
import utils
rds=redis.Redis()

############# 1) PageRank ################

def getMostPopularCandidates(candidates): 
	candScores={}
	for candidate in candidates:
		try: 
			score=float(rds.get('pr:%s' % candidate))
			candScores[candidate]=score
		except:
			continue
			#print('ERROR: No pr for %s' % candidate)
	return utils.sortAndReturnKeys(candScores)

############# 2) Time popularity ###########

def getMostTemporallyPopularCandidates(candidates, pkl):
        candScores={}
        for candidate in candidates:
                try:
                        score=pkl[candidate]
                        candScores[candidate]=score
                except:
                        continue
        return utils.sortAndReturnKeys(candScores)

############# 2) Coherence - shortest path ###########

def getMostCoherentCandidates(candidates, lastN, N):
	candScores={}
	for candidate in candidates:
		score=computeCoherence(candidate, lastN, N)
		candScores[candidate]=score

	return utils.sortAndReturnKeys(candScores)

def computeCoherence(candidate, lastN, N):
	total=0.0
	for entity in lastN:
		if entity.sys_link!='NIL':
			total+=computeShortestPathCoherence(entity.sys_link, candidate)/N

	print("Coherence of ", candidate, "with", lastN, total)
	return total

def computeShortestPathCoherence(m1, m2):
	if m1==m2:
		return 1.0
	
	fromCache=rds.get("%s:%s" % (m1, m2))
	if fromCache:
		return float(fromCache)
	else:
		path=utils.neo4jPath(m1, m2)
#
		if path:
			rds.set("%s:%s" % (m1, m2), 1/path)
			rds.set("%s:%s" % (m2, m1), 1/path)
			return 1.0/path
		else:
			rds.set("%s:%s" % (m1, m2), 0.0)
			rds.set("%s:%s" % (m2, m1), 0.0)
			return 0.0

############### 3) ?
