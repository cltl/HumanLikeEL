import redis

rds=redis.Redis()

def getMostPopularCandidates(candidates): 
	candScores={}
	for candidate in candidates:
		try: 
			score=float(rds.get('pr:%s' % candidate))
			candScores[candidate]=score
		except:
			continue
                        #print('ERROR: No pr for %s' % candidate)

	sortedCands=sorted(candScores.items(), key=lambda t:float(t[1]), reverse=True)
	return list(x[0] for x in sortedCands)#keys()

#s=set(['Barack_Obama', 'Bill_Clinton', 'Amsterdam', 'United_States'])
#print(getMostPopularK(s, 2))

"""
        bestScore=0.0 
        bestCandidate=None 
        for candidate in candidates: 
                try: 
                        score=float(rds.get('pr:%s' % candidate)) 
                        if score>bestScore: 
                                bestScore=score 
                                bestCandidate=candidate 
                except: 
                        print('ERROR: No pr for %s' % candidate) 
 
        return bestCandidate
"""
