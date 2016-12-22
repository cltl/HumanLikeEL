#!/usr/bin/env python

import dataparser
import systemparser
import utils
import ranking

import sys
import time


test_file=sys.argv[1]
collection='sm'
article=dataparser.load_article_from_naf_file(test_file, collection)

NILS=['--NME--', '*null*']

current=0
allCands=utils.parallelizeCandidateGeneration(article.entity_mentions)
for m in article.entity_mentions:
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
	if len(orderedLinks):
		m.sys_link=orderedLinks[0]
	else:
		m.sys_link='NIL'
	current+=1

print(test_file + ' done')
