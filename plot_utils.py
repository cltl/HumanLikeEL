from collections import Counter, OrderedDict
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress

def calculate_slope(cnt):
	y = OrderedDict(cnt.most_common())
	v=list(y.values())
	k=np.arange(0,len(v),1)
	return linregress(k,v)

def get_mention_counts(articles):
	gold_links=[]
	for example_article in articles:
		for entity in example_article.entity_mentions:
			mention=entity.mention
	    #   	 print(entity.gold_link)
			gold_links.append(entity.gold_link)
	cnt=Counter(gold_links)
	return cnt

def plot_freq_dist(cnt, title=None, loglog=False, b=2):
	y = OrderedDict(cnt.most_common())
	v=list(y.values())
	k=np.arange(0,len(v),1)
	if loglog:
		plt.loglog(k,v, basex=b)
	else:
		plt.plot(k,v)
	plt.ylabel('Frequency')
	plt.xlabel('Entity mentions')
	if title:
		plt.title('Distribution of %s' % title)
	plt.show()
