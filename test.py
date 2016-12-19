#!/usr/bin/env python

import dataparser
import systemparser
import utils
import ranking

import sys
import time

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


NILS=['--NME--', '*null*']

# for precision@k
maxK=5

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
					if utils.isSubstring(m.mention, m2.mention) or utils.isAbbreviation(m.mention, m2.mention):
						if m2.candidates:
							cands |= m2.candidates
			# End of local candidates generation
		m.candidates=cands
		orderedLinks=ranking.getMostPopularCandidates(m.candidates)
		totalCandidates+=len(orderedLinks)
		if m.gold_link not in NILS and ranking.getPageRank(m.gold_link):# NILS=['--NME--', '*null*']

			if m.gold_link in m.candidates:  #, m.gold_link, m.candidates)
				found+=1
				try:
					golden_rank=orderedLinks.index(m.gold_link)+1
					for k in correct:
						if golden_rank<=int(k):
							correct[k]+=1
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
print("PAGERANK STATS (nonNils): Precision@1", correct['1']/nonNils, "Precision@2", correct['2']/nonNils, "Precision@3", correct['3']/nonNils, "Precision@4", correct['4']/nonNils, "Precision@5", correct['5']/nonNils)
t2=time.time()
print("Took %f seconds" % (t2-t1))

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


