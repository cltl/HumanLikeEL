#!/usr/bin/env python

import dataparser
import systemparser
import utils
import ranking
import globals

import pickle
import sys
import time


NILS=['--NME--', '*null*']

# for precision@k
maxK=5
N=10
month='200712'

globals.pkl=pickle.load(open(month + '_agg.p', 'rb'))

def evaluate(articles, system):
	all_correct=0
	any_correct=0
	coref_correct=0
	coref_wrong=0
	nonNils=0
	nils=0
	found=0
	correct={'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
	t1=time.time()
	toWrite=""
	totalCandidates=0
	for article in articles:
		if article.collection!=collection:
			continue
		if system!='spotlight':
			allCands=utils.parallelizeCandidateGeneration(article.entity_mentions)
		current=0
		for m in article.entity_mentions:
			if system=='spotlight':
				cands=systemparser.getSpotlightCandidates(m.mention)
			else:
				cands=allCands[m.mention]

				# Try to generate extra local candidates
				if current>0:
					for m2 in article.entity_mentions[:current-1]:
						if utils.isSubstring(m.mention, m2.mention) or utils.isAbbreviation(m.mention, m2.mention) and not m.exact_match:
							m.sys_link=m2.sys_link
							#if m2.candidates:
							#	cands |= m2.candidates
				# End of local candidates generation
			m.candidates=cands
			# LOTUS original
			orderedLinksLOTUS=list(cands)
			# TempPop
			orderedLinksTempop=ranking.getMostTemporallyPopularCandidates(set(m.candidates), timePickle)
			# PageRank
			orderedLinksPrank=ranking.getMostPopularCandidates(m.candidates)
			# Coherence
			#lastN=article.entity_mentions[max(0,current-N-1):current-1]
			#orderedLinks=ranking.getMostCoherentCandidates(orderedLinks[:10], lastN, N)
			totalCandidates+=len(orderedLinksLOTUS)
			if len(orderedLinksLOTUS):
				m.sys_link=orderedLinksLOTUS[0] #.pop(last=False)
			else:
				m.sys_link='NIL'
			if all([m.gold_link not in NILS, ranking.getPageRank(m.gold_link)]):# NILS=['--NME--', '*null*']
				if m.gold_link in m.candidates:  #, m.gold_link, m.candidates)
					found+=1
					if m.sys_link:
						if m.sys_link==m.gold_link:
							coref_correct+=1
						else:
							coref_wrong+=1
					else:
						try:
							golden_rank_lotus=orderedLinksLOTUS.index(m.gold_link)+1
							golden_rank_tp=orderedLinksTempop.index(m.gold_link)+1
							golden_rank_pr=orderedLinksPrank.index(m.gold_link)+1
							print("Mention, Gold link: ", m.mention, m.gold_link)
							print("LOTUS best: ", orderedLinksLOTUS[0], "Rank of golden:", golden_rank_lotus)
							print("TP best: ", orderedLinksTempop[0], "Rank of golden:", golden_rank_tp)
							print("PR best: ", orderedLinksPrank[0], "Rank of golden:", golden_rank_pr)
							if all([golden_rank_lotus==1, golden_rank_tp==1, golden_rank_pr==1]):
								all_correct+=1
							if any([golden_rank_lotus==1, golden_rank_tp==1, golden_rank_pr==1]):
								any_correct+=1
	#						for k in correct:
	#							if golden_rank<=int(k):
	#								correct[k]+=1
						except:
							print("The gold link %s had no entry in the pagerank data" % m.gold_link)
				else:
					toWrite+="%s\t%s\t%s\n" % (m.mention, m.gold_link, m.candidates)
				nonNils+=1
			else:
				nils+=1
			current+=1
	if system!='spotlight':
		with open('%s_misses.tsv' % collection, 'w') as w:
			w.write(toWrite)

	print("GENERAL STATS: Articles", len(articles), "non-Nils", nonNils, "Nils", nils)
	print("CANDIDATE GENERATION STATS: Recal of candidates", found, "%recall of candidates", found/nonNils, "Recall including Nils", found+nils, "%recall including nils", (found+nils)/(nonNils+nils))
	print("Average candidates", totalCandidates/(nils+nonNils))
	print("coref correct", coref_correct, "coref wrong", coref_wrong)
	print("all correct", all_correct/nonNils, "any correct", any_correct/nonNils)
#	print("PAGERANK STATS (nonNils): Precision@1", correct['1']/nonNils, "Precision@2", correct['2']/nonNils, "Precision@3", correct['3']/nonNils, "Precision@4", correct['4']/nonNils, "Precision@5", correct['5']/nonNils)
	t2=time.time()
	print("Took %f seconds" % (t2-t1))



if __name__=="__main__":
	path="data/"

	if len(sys.argv)>=3:
		collection=sys.argv[1]
		system=sys.argv[2]
	else:
		sys.exit(-1)

	if collection in ['aidatesta', 'aidatestb']:
		test_file="AIDA-YAGO2-dataset_topicsLowlevel.tsv"
		articles=dataparser.load_article_from_conll_file(path + test_file)
	elif collection=='wes2015':
		test_file='wes2015-dataset-nif-1.2.rdf'
		articles=dataparser.load_article_from_nif_file(path + test_file)
	else:
		if collection=='msnbc':
			test_file='WikificationACL2011Data/MSNBC/Problems/*'
		elif collection=='ace2004':
			test_file='WikificationACL2011Data/ACE2004_Coref_Turking/Dev/ProblemsNoTranscripts/*'
		else:		
			sys.exit(-1)
		articles=dataparser.load_article_from_xml_files(path + test_file, collection)

	print()
	print(collection, system)

	evaluate(articles, system)




"""
example_article=articles.pop()

print("OLD WAY")

import time
t1=time.time()
print(example_article.identifier)
for entity in example_article.entity_mentions:
    mention=entity.mention
    c=utils.generateCandidatesWithLOTUS(mention, 20, 50)
#    print(mention,c)
t2=time.time()
print(t2-t1)

print("NEW WAY")

t1=time.time()
print(example_article.identifier)
candidates=utils.parallelizeCandidateGeneration(example_article.entity_mentions)
print(candidates)
t2=time.time()
print(t2-t1)
print(len(candidates), len(example_article.entity_mentions))
"""


