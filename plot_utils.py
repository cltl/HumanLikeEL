from collections import Counter, OrderedDict
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
from collections import defaultdict
import random


def calculate_slope(cnt):
	y = OrderedDict(cnt.most_common())
	v=list(y.values())
	k=np.arange(0,len(v),1)
	return linregress(k,v)

def get_mention_counts(articles, skip_nils=True):
	gold_forms=[]
	gold_links=[]
	for example_article in articles:
		for entity in example_article.entity_mentions:
			mention=entity.mention
			meaning=entity.gold_link
			if not skip_nils or meaning!='--NME--':
				gold_forms.append(mention)
				gold_links.append(meaning)
	cnt_instances=Counter(gold_links)
	cnt_forms=Counter(gold_forms)
	return cnt_instances, cnt_forms

def get_pagerank_distribution(articles, skip_zeros=False):

	pagerank_frequency=defaultdict(int)

	pr_uniq_sets=defaultdict(set)
	for article in articles:
		for mention in article.entity_mentions:
			h=int(mention.gold_pr/1)
			if not skip_zeros or h!=0:
				pagerank_frequency[h]+=1
				pr_uniq_sets[h].add(mention.gold_link)
	pr_uniq=defaultdict(int)
	for k,v in pr_uniq_sets.items():
		pr_uniq[k]=len(v)
	return pagerank_frequency, pr_uniq

def get_interpretations_and_references(articles, skip_nils=True):
	interpretations=defaultdict(set)
	references = defaultdict(set)
	for article in articles:
		for mention in article.entity_mentions:
			form=mention.mention
			meaning=mention.gold_link
			if not skip_nils or meaning!='--NME--':
		    		interpretations[form].add(meaning)
			if meaning!='--NME--':
		    		references[meaning].add(form)
	return interpretations, references

def get_instance_distribution(articles, instance):
        references = defaultdict(int)
        for article in articles:
                for mention in article.entity_mentions:
                        form=mention.mention
                        meaning=mention.gold_link
                        if meaning==instance:
                                references[form]+=1
        return sorted(references.items(), key=lambda x: x[1], reverse=True)

def get_form_distribution(articles, the_form):
	instances = get_inst_with_counts(articles, the_form)
	return sorted(instances.items(), key=lambda x: x[1], reverse=True)

def get_inst_with_counts(articles, the_form):
        instances = defaultdict(int)
        for article in articles:
                for mention in article.entity_mentions:
                        form=mention.mention
                        meaning=mention.gold_link
                        if form==the_form and meaning!='--NME--':
                                instances[meaning]+=1
        return instances

def get_form_counts(articles, the_form):
	instances = get_inst_with_counts(articles, the_form)
	return instances.values()

def prepare_scatter_plot(dist1, dist2):
	x_dist = []
	y_dist = []
	for i, freq in dist1.items():
		x_dist.append(freq)
		y_dist.append(dist2[i])
	x_dist=np.array(x_dist)
	y_dist=np.array(y_dist)
	return x_dist, y_dist

def scatter_plot(dist1, dist2, x_axis='', y_axis='', title='', save=False):

	fig, ax = plt.subplots()
	fit = np.polyfit(dist1, dist2, deg=1)
	ax.plot(dist1, fit[0] * dist1 + fit[1], color='red')
	ax.scatter(dist1, dist2)

	ax.set_xlabel(x_axis)
	ax.set_ylabel(y_axis)
	ax.set_title(title)

	fig.show()

	if save:
		if title:
			fig.savefig('img/%s.png' % title.lower().replace(' ', '_'), bbox_inches='tight')
		else:
			fig.savefig('img/%d.png' % random.randint(0,1000000), bbox_inches='tight')

def plot_freq_dist(cnt, title=None, x_axis='Entity mentions', loglog=False, b=2, save=False):
	fig = plt.figure()

	y = OrderedDict(cnt.most_common())
	v=list(y.values())
	k=np.arange(0,len(v),1)
	if loglog:
		plt.loglog(k,v, basex=b)
	else:
		plt.plot(k,v)
	plt.ylabel('Frequency')
	plt.xlabel(x_axis)
	if title:
		if loglog:
			p_title = 'Distribution of %s (log-log)' % title
		else:
			p_title = 'Distribution of %s' % title
		plt.title(p_title)
	plt.show()
	if save:
		if title:		
			fig.savefig('img/%s.png' % p_title.lower().replace(' ', '_'), bbox_inches='tight')
		else:
			fig.savefig('img/%d.png' % random.randint(0,1000000), bbox_inches='tight')	

def plot_freq_noagg(data, title=None, x_axis='', loglog=False, b=2, save=False):
        fig = plt.figure()

        lists = sorted(data.items())
        x, y = zip(*lists)

        if loglog:
       	        plt.loglog(x, y, basex=b)
        else:
                plt.plot(x, y)
        plt.ylabel('Frequency')
        plt.xlabel(x_axis)
        if title:
                if loglog:
                        p_title = 'Distribution of %s (log-log)' % title
                else:
                        p_title = 'Distribution of %s' % title
                plt.title(p_title)
        plt.show()
        if save:
                if title:
                        fig.savefig('img/%s.png' % p_title.lower().replace(' ', '_'), bbox_inches='tight')
                else:
                        fig.savefig('img/%d.png' % random.randint(0,1000000), bbox_inches='tight')

def frequency_correlation(freq_dist, other_dist, min_frequency=0, title=None, x_label='', y_label='', save=False):

	fig = plt.figure()


	other_per_frequency = defaultdict(int)
	count_per_frequency = defaultdict(int)
	for form,frequency in freq_dist.items():
    		if frequency>min_frequency:
        		#print(form,frequency, ambiguity[form])
        		count_per_frequency[frequency]+=1
        		other_per_frequency[frequency]+=other_dist[form]

	x=[]
	y=[]
	for frequency in sorted(count_per_frequency):
#    		print(frequency, other_per_frequency[frequency]/count_per_frequency[frequency])
    		x.append(frequency)
    		y.append(other_per_frequency[frequency]/count_per_frequency[frequency])
	plt.plot(x,y)
	plt.ylabel(y_label)
	plt.xlabel(x_label)
	if title:
		plt.title(title)
	plt.show()

	if save:
		if title:
			fig.savefig('img/%s.png' % title.lower().replace(' ', '_'), bbox_inches='tight')
		else:
			fig.savefig('img/%d.png' % random.randint(0,1000000), bbox_inches='tight')

################# SYSTEM UTILS #####################

def overall_performance(articles, skip_nils=True):
	correct=0
	total=0
	for article in articles:
		for entity in article.entity_mentions:
			if skip_nils and entity.gold_link=='--NME--':
		    		continue
			if entity.gold_link==entity.sys_link:
		    		correct+=1
			total+=1
	print(correct, total)
	return correct/total

def prepare_ranks(correct_per_form, total_per_form, min_frequency=0):
    correct_per_rank=defaultdict(int)
    total_per_rank=defaultdict(int)    
    for form, data in total_per_form.items():
        if sum(data.values())>min_frequency:
            print(form)
        else:
            continue
        sorted_by_rank=sorted(data.items(), key=lambda x:x[1], reverse=True)
        rank=1
        for ranked_URI, freq in sorted_by_rank:
            correct_per_rank[rank]+=correct_per_form[form][ranked_URI]
            total_per_rank[rank]+=freq
            rank+=1
    return correct_per_rank, total_per_rank

def plot_ranks(correct_per_rank, total_per_rank):
    acc_per_rank=defaultdict(float)
    for rank, total in total_per_rank.items():
        acc_per_rank[rank]=correct_per_rank[rank]/total
    print(acc_per_rank)
    
    plt.plot(list(acc_per_rank.keys()), list(acc_per_rank.values()), 'b-o')
    plt.title("Accuracy per rank")
    plt.xlabel("Rank")
    plt.ylabel("Accuracy")
    plt.show()
