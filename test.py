import conversion
import utils
import time
import ranking

path="data/"
#test_file="AIDA-YAGO2-dataset_topicsLowlevel.tsv"
#test_file='wes2015-dataset-nif-1.2.rdf'
#test_file='WikificationACL2011Data/MSNBC/Problems/*'
test_file='WikificationACL2011Data/ACE2004_Coref_Turking/Dev/ProblemsNoTranscripts/*'

#articles=conversion.load_article_from_conll_file(path + test_file)
#articles=conversion.load_article_from_nif_file(path + test_file)
articles=conversion.load_article_from_xml_files(path + test_file, 'ace2004')

#collection='aidatrain'
#collection='aidatestb'
#collection='wes2015'
#collection='msnbc'
collection='ace2004'

#print(utils.analyzeEntities(articles, 'aidatestb'))

print("data file loaded!")

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
		print(m.mention, cands, m.gold_link)
		if m.gold_link!='--NME--':
			if m.gold_link in m.candidates:  #, m.gold_link, m.candidates)
				found+=1
			system_link=ranking.getMostPopularCandidate(m.candidates)
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


