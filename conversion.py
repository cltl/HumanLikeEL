#!/usr/bin/python
# Filip Ilievski
# December 2016

import classes
from rdflib import Graph, URIRef
import utils

def load_article_from_nif_file(nif_file):
	g=Graph()
	g.parse(nif_file, format="n3")

	news_items=set()

	articles = g.query(
	""" SELECT ?articleid ?date ?string
	WHERE {
		?articleid nif:isString ?string .
		OPTIONAL { ?articleid dc:date ?date . }
	}
	""")
	for article in articles:
		news_item_obj=classes.NewsItem(
			content=article['string'],
			identifier=article['articleid'], #"http://yovisto.com/resource/dataset/iswc2015/doc/281#char=0,4239",
			dct=article['date'],
			collection='wes2015'
		)
		query=""" SELECT ?id ?mention ?start ?end ?gold
		WHERE {
			?id nif:anchorOf ?mention ;
			nif:beginIndex ?start ;
			nif:endIndex ?end ;
			nif:referenceContext <""" + str(article['articleid']) + """> .
			OPTIONAL { ?id itsrdf:taIdentRef ?gold . }
		} ORDER BY ?start"""
		qres_entities = g.query(query)
		for entity in qres_entities:
			entity_obj = classes.EntityMention(
				begin_index=int(entity['start']),
				end_index=int(entity['end']),
				mention=str(entity['mention']),
				gold_link=utils.getLinkRedirect(str(entity['gold']))
			)
			news_item_obj.entity_mentions.add(entity_obj)
		news_items.add(news_item_obj)
	return news_items

def load_article_from_conll_file(conll_file):
	lines=open(conll_file, 'r')
	news_items=set()

	current_file=''
	current_topic=''
	for line in lines:
		if line.startswith('-DOCSTART-'):
			current_offset=0
			if current_file!="":
				news_items.add(news_item_obj)
			# change current file
			current_file, current_topic=line.lstrip('-DOCSTART-').strip().split('\t')
			if 'testa' in current_file:
				collection='aidatesta'
			elif 'testb' in current_file:
				collection='aidatestb'
			else:
				collection='aidatrain'
			news_item_obj = classes.NewsItem(
				identifier=current_file,
				domain=current_topic,
				collection=collection
			)
		else:
			elements=line.split('\t')
			word=elements[0]
			if len(elements)>3 and elements[1]=='B':
				mention=elements[2]
				gold=elements[3]
				entity_obj = classes.EntityMention(
                         		begin_index=current_offset,
                                	end_index=current_offset + len(mention),
                                	mention=mention,
                                	gold_link=gold
                        	)
				news_item_obj.entity_mentions.add(entity_obj)
			current_offset+=len(word)+1
	news_items.add(news_item_obj)
	return news_items
