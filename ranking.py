import redis

rds=redis.Redis()

def getMostPopularCandidate(candidates): 
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
