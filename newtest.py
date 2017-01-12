
#!/usr/bin/env python

import dataparser
import systemparser
import candidates
import ranking
import globals
import utils

import pickle
import sys
import time
import math
from collections import defaultdict

NILS=['--NME--', '*null*', None]

# for precision@k
maxK=5
N=10
month='200712'

globals.pkl=pickle.load(open(month + '_agg.p', 'rb'))

def evaluate(articles, collection, system):
	all_correct=0
	any_correct=0
	coref_correct=0
	coref_wrong=0
	nonNils=0
	nils=0
	found=0
	correct=0
	correctJSON={'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
	t1=time.time()
	toWrite=""
	totalCandidates=0
	howManyOnes=defaultdict(int)
	howManyCorrect=defaultdict(int)
	for article in articles:
		if article.collection!=collection:
			continue
		if system!='spotlight':
			entity_mentions=candidates.parallelizeCandidateGeneration(article.entity_mentions)
			article.entity_mentions=entity_mentions
			current=0
			for em in article.entity_mentions:
				em.anchor_mention=utils.setAnchorMention(em.mention, article.entity_mentions[:current-1])
				if em.anchor_mention:
					ones=-1
					em.sys_link=em.anchor_mention.sys_link
				else:
					ones=0
					maxScore=0.0
					maxCandidate=None
					for c in em.candidates:
						c.score=c.lotus_score*c.ss_score*math.sqrt(c.pr_score)
						if c.ss_score<0.9:
							continue
						ones+=1
						#print(c.subject, c.score, c.string, c.tp_score, c.pr_score, c.lotus_score, c.ss_score)
						if c.score>maxScore:
							maxScore=c.score
							maxCandidate=c.subject
					em.sys_link=maxCandidate
				if ones==0:
					print("################### VERDICT ####################")
					print(em.mention, em.gold_link, em.sys_link)
					for c in em.candidates:
						print(c.subject, c.ss_score)
					print("################################################")
					print()
				current+=1
				if em.gold_link not in NILS:
					nonNils+=1
					if em.gold_link==em.sys_link:
						correct+=1
						howManyCorrect[ones]+=1
				else:
					nils+=1
					if em.sys_link is None:
						correct+=1
						howManyCorrect[ones]+=1
				howManyOnes[ones]+=1
				ones=0
	t2=time.time()
	print(t2-t1)
	print("CORRECT ALL", correct/(nils+nonNils))
	print("SS>0.9", howManyOnes)
	print("SS>0.9, correct", howManyCorrect)
	return article.entity_mentions

def run(collection='msnbc', system='our'):
        path="data/"

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

        return evaluate(articles, collection, system)

if __name__=="__main__":
        if len(sys.argv)>=3:
                collection=sys.argv[1]
                system=sys.argv[2]
        else:
                sys.exit(-1)
        run(collection, system)
