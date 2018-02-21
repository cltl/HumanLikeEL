from collections import Counter, OrderedDict
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from numpy import median
from scipy.stats import linregress
from collections import defaultdict
import random
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from scipy.stats import pearsonr, spearmanr
import seaborn as sns
import pandas as pd

def calculate_slope(cnt):
	y = OrderedDict(cnt.most_common())
	v=np.log(list(y.values()))
	k=np.log(np.arange(1,len(v)+1,1))
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

def get_pageranks(articles, skip_zeros=False):

	pageranks = {}
	pagerank_frequency=defaultdict(int)

	pr_uniq_sets=defaultdict(set)
	for article in articles:
		for mention in article.entity_mentions:
			h=int(mention.gold_pr/1)
			if not skip_zeros or h!=0:
				pagerank_frequency[h]+=1
				pr_uniq_sets[h].add(mention.gold_link)
			pageranks[mention.gold_link]=h
	pr_uniq=defaultdict(int)
	for k,v in pr_uniq_sets.items():
		pr_uniq[k]=len(v)
	return pagerank_frequency, pr_uniq, pageranks

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

def compute_accuracy_by_form(articles, skip_nils=True):
    forms_acc = defaultdict(int)
    
    correct_by_form = defaultdict(int)
    total_by_form = defaultdict(int)

    forms_by_count=defaultdict(set)
    
    for article in articles:
        for entity in article.entity_mentions:
            if entity.sys_link and (not skip_nils or entity.gold_link!='--NME--'):
                if entity.sys_link==entity.gold_link:
                    correct_by_form[entity.mention]+=1
                total_by_form[entity.mention]+=1

    for form, count in total_by_form.items():
        forms_by_count[count].add(form)
        forms_acc[form]=correct_by_form[form]*100.0/count
    
    return forms_acc, forms_by_count

def compute_accuracy_by_uri(articles, skip_nils=True):
	uris_acc = defaultdict(int)
	correct_by_uri = defaultdict(int)
	total_by_uri = defaultdict(int)

	uris_by_count = defaultdict(set)

	for article in articles:
		for entity in article.entity_mentions:
			if entity.sys_link and (not skip_nils or entity.gold_link!='--NME--'):
				if entity.sys_link==entity.gold_link:
					correct_by_uri[entity.gold_link]+=1
				total_by_uri[entity.gold_link]+=1
	for uri, count in total_by_uri.items():
		uris_by_count[count].add(uri)
		uris_acc[uri]=correct_by_uri[uri]*100.0/count

	return uris_acc, uris_by_count

def prepare_scatter_plot(dist1, dist2):
	x_dist = []
	y_dist = []
	for i, freq in dist1.items():
		if i not in dist2:
			continue
		x_dist.append(freq)
		y_dist.append(dist2[i])
	x_dist=np.array(x_dist)
	y_dist=np.array(y_dist)
	return x_dist, y_dist

def scatter_plot(dist1, dist2, x_axis='', y_axis='', title='', save=False, limit=100000, degree=1, labels=None):
	#colors = ['teal', 'yellowgreen', 'gold', 'red', 'blue']
	lw=2

	#dist1=dist1[:limit]
	#dist2=dist2[:limit]

	fig = plt.figure()

	plt.scatter(dist1, dist2, color='navy', marker='o', label="training points")
	X = dist1[:, np.newaxis]
	model = make_pipeline(PolynomialFeatures(degree), Ridge())
	model.fit(X, dist2)
	y_plot = model.predict(X)
	plt.plot(dist1, y_plot, color='teal', linewidth=lw,
	     label="Regression fit degree %d" % degree)

	plt.xlabel(x_axis)
	plt.ylabel(y_axis)
	plt.title(title)

	if labels:
		for i in range(0, len(dist2)):
			xy=(dist1[i], dist2[i])
			plt.annotate(labels[i], xy,
				xytext=(-20, 20),
				textcoords='offset points', ha='right', va='bottom',
				bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
				arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))

	legend = plt.legend(loc='upper left', frameon=1)
	frame = legend.get_frame()
	frame.set_edgecolor('gray')
	plt.show()

	if save:
		if title:
			fig.savefig('img/%s.png' % title.lower().replace(' ', '_'), bbox_inches='tight')
		else:
			fig.savefig('img/%d.png' % random.randint(0,1000000), bbox_inches='tight')

def plot_line_with_whiskers(x, y, xl='', yl='', title='Correlation', estimators=['mean', 'median'], xlim=None, save=False):
    for est in estimators:
        fig = plt.figure()

        amb_data = {xl: x, 
                    yl: y}

        df = pd.DataFrame(amb_data)

        if est=='mean': # mean
            ax = sns.pointplot(x=xl, y=yl, data=df)
        else: # median
            ax = sns.pointplot(x=xl, y=yl, data=df, estimator=median)

        plt_title='%s (estimator=%s)' % (title, est)
        plt.title(plt_title)

        if xlim:
                ax.set(xlim=(xlim[0], xlim[1]))
        ax.set(ylim=(0, None))

        plt.show()

        if save:
            fig.savefig('img/%s.png' % plt_title)

def prepare_box_plot(x,y):
	i=0
	agg_freq_per_amb = defaultdict(list)
	while i<len(x):
		amb=x[i]
		freq=y[i]
		agg_freq_per_amb[amb].append(freq)
		#    print(amb,freq)
		i+=1
	bp_data = []
	for amb in range(1, max(x)+1):
		bp_data.append(agg_freq_per_amb[amb])
	return bp_data

def box_plot(dists, x_axis='', y_axis='', title='', y_lim=-1, save=False):
	fig=plt.figure(1, figsize=(9, 6))

	ax = fig.add_subplot(111)
	
	bp = ax.boxplot(dists)
	ax.set_xlabel(x_axis)
	ax.set_ylabel(y_axis)
	ax.set_title(title)

	if y_lim!=-1:
		ax.set_ylim([0, y_lim])

	if save:
		if title:
			fig.savefig('img/%s.png' % title.lower().replace(' ', '_'), bbox_inches='tight')
		else:
			fig.savefig('img/%d.png' % random.randint(0,1000000), bbox_inches='tight')

def annotated_heatmap(x_labels, y_labels, values, x_lbl='levels'):

    x=[]
    y=[]
    vals=[]
    i=0
    for x_val in x_labels:
        for y_val in y_labels:
            x.append(x_val)
            y.append(y_val)
            vals.append(values[i])
            i+=1
    print(x, y, vals)

    data={}
    data['dataset']=x
    data[x_lbl]=y
    data['values']=vals
    
    fig, ax = plt.subplots(figsize=(len(y_labels)+3,0.75*len(x_labels)))         # Sample figsize in inches
    
    df = pd.DataFrame.from_dict(data)
    
    result = df.pivot(index='dataset', columns=x_lbl, values='values')

    print(result)
    ax = sns.heatmap(data=result, annot=True, fmt="d", cmap='cubehelix', )
    
    fig.savefig('img/%s.png' % x_lbl)

def autolabelh(rects, ax):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        width = rect.get_width()
        ax.text(1.05*width, rect.get_y() + rect.get_height()/2.,
                int(width),
               va='center')

def autolabel(rects, ax):
	"""
	Attach a text label above each bar displaying its height
	"""
	for rect in rects:
		height = rect.get_height()
		print(height)
		ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
			round(height,2), fontsize=10,
			ha='center', va='bottom')

def plot_scores(scores, title=''):
	dpoints = np.array(scores)

	plt.gray()
	fig = plt.figure()
	ax = fig.add_subplot(111)

	space = 0.3

	evals = np.unique(dpoints[:,0])
	systems = np.unique(dpoints[:,1])

	evals=['overall', 'ambiguous forms', 'forms with nils & non-nils' ]
	colors=['#222222', '#666666', '#aaaaaa']
	print(evals)
	print(systems)

	n = len(evals)

	width = (1 - space) / (len(evals))
	print("width:", width)

	indeces = range(1, len(systems)+1)

	for i,cond in enumerate(evals):
		print("evaluation:", cond)

		vals = dpoints[dpoints[:,0] == cond][:,2].astype(np.float)
		pos = [j - (1 - space) / 2. + i * width for j in range(1,len(systems)+1)]
		br = ax.bar(pos, vals, width=width, label=cond, color=colors[i]) #cm.Accent(float(i) / n))
		autolabel(br, ax)
	    
	ax.set_xticks(indeces)
	ax.set_xticklabels(systems)
	plt.setp(plt.xticks()[1], rotation=0)    

	ax.set_ylim(ymax=1.1)
	ax.set_ylabel("F1-score")

	handles, labels = ax.get_legend_handles_labels()
	legend = ax.legend(handles[::1], labels[::1], loc='upper center', bbox_to_anchor=(0.22, 1.02),  shadow=True, ncol=1, frameon=1)
	frame = legend.get_frame()
	frame.set_edgecolor('gray')
	plt.show()

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

def frequency_correlation(freq_dist, other_dist, min_frequency=0, title=None, x_label='', y_label='', xlim=None, save=False):

	fig = plt.figure()


	other_per_frequency = defaultdict(int)
	count_per_frequency = defaultdict(int)
	for form,frequency in freq_dist.items():
		if frequency>min_frequency:
			if form in other_dist:
				count_per_frequency[frequency]+=1
				other_per_frequency[frequency]+=other_dist[form]

	x=[]
	y=[]
	for frequency in sorted(count_per_frequency):
#    		print(frequency, other_per_frequency[frequency]/count_per_frequency[frequency])
    		x.append(frequency)
    		y.append(other_per_frequency[frequency]/count_per_frequency[frequency])
	plt.plot(x,y, marker='o')
	plt.ylabel(y_label)
	plt.xlabel(x_label)
	if xlim:
		plt.xlim(xlim[0], xlim[1])
	plt.ylim(ymin=0)
	if title:
		plt.title(title)
	plt.show()

	if save:
		if title:
			fig.savefig('img/%s.png' % title.lower().replace(' ', '_'), bbox_inches='tight')
		else:
			fig.savefig('img/%d.png' % random.randint(0,1000000), bbox_inches='tight')

################# SYSTEM UTILS #####################

def overall_performance_prf(articles, skip_nils=True, skip_nonnils=False):
	tp=0
	fn=0
	fp=0
	for article in articles:
		for entity in article.entity_mentions:
			if skip_nils and entity.gold_link=='--NME--':
		    		continue
			if skip_nonnils and entity.gold_link!='--NME--':
				continue
			if entity.gold_link==entity.sys_link:
		    		tp+=1
			else: 
				if entity.sys_link!='--NME--':
					fp+=1
				if entity.gold_link!='--NME--':
					fn+=1
	print(tp, fp, fn)
	p=tp/(tp+fp)
	r=tp/(tp+fn)
	f1=2*p*r/(p+r)
	print(p,r,f1)
	return f1


def overall_performance(articles, skip_nils=True, skip_nonnils=False):
	correct=0
	total=0
	for article in articles:
		for entity in article.entity_mentions:
			if skip_nils and entity.gold_link=='--NME--':
		    		continue
			if skip_nonnils and entity.gold_link!='--NME--':
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
        if sum(data.values())<=min_frequency:
            continue
        elif min_frequency>0:
            print(form)
        sorted_by_rank=sorted(data.items(), key=lambda x:x[1], reverse=True)
        rank=1
        for ranked_URI, freq in sorted_by_rank:
            correct_per_rank[rank]+=correct_per_form[form][ranked_URI]
            total_per_rank[rank]+=freq
            rank+=1
    return correct_per_rank, total_per_rank

def plot_ranks(correct_per_rank, total_per_rank, title='', save=False):

    fig = plt.figure()

    acc_per_rank=defaultdict(float)
    for rank, total in total_per_rank.items():
        acc_per_rank[rank]=correct_per_rank[rank]/total
    print(acc_per_rank)
    
    dist1=list(acc_per_rank.keys())
    dist2=list(acc_per_rank.values())

    plt.plot(dist1, dist2, 'b-o')
    plt.title(title)
    plt.xlabel("Rank")
    plt.ylabel("Accuracy")
    plt.show()

    if save:
        if title:
            fig.savefig('img/%s.png' % title.lower().replace(' ', '_'), bbox_inches='tight')
        else:
            fig.savefig('img/%d.png' % random.randint(0,1000000), bbox_inches='tight')

    correlation, significance = spearmanr(dist1, dist2)
    print('The Spearman correlation between X and Y is:', correlation, '. Significance: ', significance)


