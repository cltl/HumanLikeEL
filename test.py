import conversion
import utils
import time

#test_file="wes2015-dataset-nif.rdf"
path="data/"
test_file="AIDA-YAGO2-dataset_topicsLowlevel.tsv"
articles=conversion.load_article_from_conll_file(path + test_file)

#print(utils.analyzeEntities(articles, 'aidatestb'))

#collection='aidatrain'
collection='aidatestb'
nonNils=0
found=0
correct=0
t1=time.time()
for article in articles:
	if article.collection!=collection:
		continue
	print(article.identifier)
	allCands=utils.parallelizeCandidateGeneration(article.entity_mentions)
	for m in article.entity_mentions:
		cands=allCands[m.mention]
		m.candidates=cands
		if m.gold_link!='--NME--':
			if m.gold_link in m.candidates:  #, m.gold_link, m.candidates)
				found+=1
			system_link=utils.getMostPopularCandidate(m.candidates)
			if system_link==m.gold_link:
				correct+=1
			nonNils+=1
print("Found in candidates", found, "Correct", correct, "All non-Nils", nonNils, "%found in candidates", found/nonNils, "%correct", correct/nonNils)
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


