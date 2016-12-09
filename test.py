import conversion
import utils

#test_file="wes2015-dataset-nif.rdf"
path="data/"
test_file="AIDA-YAGO2-dataset_topicsLowlevel.tsv"
articles=conversion.load_article_from_conll_file(path + test_file)

c=0
for article in articles:
	c+=len(article.entity_mentions)
print(c)
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


