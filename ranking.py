import redis
import math

import utils

rds=redis.Redis()

############# Disambiguate second time ##########

def disambiguate_mentions_deep(entity_mentions):
	current=0
	for em in entity_mentions:
		if em.sys_link and not em.anchor_mention:
			lastN=utils.getLastN(entity_mentions, current)
			coherence=compute_coherence(em.sys_link.subject, lastN)
			#maxScore=coherence
			if em.total_pr>0:
				maxScore=coherence*em.sys_link.ss_score*(em.sys_link.lotus_score/em.total_lotus)*(em.sys_link.pr_score/em.total_pr)
			else:
				maxScore=coherence*em.sys_link.ss_score*(em.sys_link.lotus_score/em.total_lotus)
			maxCandidate=em.sys_link
			print(em.mention, em.sys_link.subject, em.sys_link.ss_score, (em.sys_link.lotus_score/em.total_lotus), coherence, maxScore, em.gold_link)
			for c in em.candidates:
				if c.score>0.5*em.sys_link.score and c.subject!=em.sys_link.subject: # If there is any chance that this candidate will win
					coherence=compute_coherence(c.subject, lastN)
					#score=coherence
					score=coherence*c.ss_score*(c.lotus_score/em.total_lotus)*pow(c.pr_score/em.total_pr,1) #entity_mentions[max(current-10, 0):current])
					print("***************** REBUTTAL *******************")
					print(c.subject, c.ss_score,(c.lotus_score/em.total_lotus), coherence, score)
					if score>maxScore:
						maxScore=score
						maxCandidate=c
			if em.sys_link!=maxCandidate:
				print("########### Best candidate changed to", maxCandidate)
			em.sys_link=maxCandidate
			em.sys_link.score=maxScore
		current+=1
	return entity_mentions
############# Disambiguate first time ###########

def disambiguate_mentions(entity_mentions):
	current=0
	for em in entity_mentions:
		em.anchor_mention=utils.setAnchorMention(em.mention, entity_mentions[:current])
		#ones=0
		if em.anchor_mention:
		#	ones+=1
			try:
				maxScore=em.anchor_mention.sys_link.score 
			except:
				maxScore=1.0
			maxCandidate=em.anchor_mention.sys_link
		else:
			maxScore=0.01
			maxCandidate=None
		for c in em.candidates:
			#if c.ss_score<0.9:
			#       continue
#			try:
#				c.score=c.ss_score*(c.tp_score/em.total_tp)*(c.pr_score/em.total_pr)*(c.lotus_score/em.total_lotus)
#			except:
			if em.total_pr>0:
				c.score=c.ss_score*pow(c.pr_score/em.total_pr,1)*(c.lotus_score/em.total_lotus)
			else:
				c.score=c.ss_score*(c.lotus_score/em.total_lotus)
		#	except:
		#		if em.total_pr==0:
		#			c.score=c.ss_score*math.sqrt(c.lotus_score/em.total_lotus)
		#		elif em.total_lotus==0:
		#			c.score=c.ss_score*math.sqrt(c.pr_score/em.total_pr)
			#ones+=1
			if c.score>maxScore:
				maxScore=c.score
				maxCandidate=c
		em.sys_link=maxCandidate
		current+=1
	return entity_mentions


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

"""
def getMostCoherentCandidates(candidates, lastN, N):
	candScores={}
	for candidate in candidates:
		score=computeCoherence(candidate, lastN, N)
		candScores[candidate]=score

	return utils.sortAndReturnKeys(candScores)
"""

def compute_coherence(candidate, lastN):
	total=0.0
	N=0
	for entity_mention in lastN:
		if entity_mention.sys_link:
			total+=computeShortestPathCoherence(entity_mention.sys_link.subject, candidate)
			N+=1
	if N==0:
		return 1.0
	return total/N

def computeShortestPathCoherence(m1, m2):
	if m1==m2:
		return 1.0
	
	fromCache=rds.get("%s:%s" % (m1, m2))
	if fromCache:
		return float(fromCache)
	else:
		path=utils.neo4jPath([m1, m2])
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
