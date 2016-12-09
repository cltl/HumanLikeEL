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
	""" SELECT ?date ?string
	WHERE {
		<http://yovisto.com/resource/dataset/iswc2015/doc/281#char=0,4239> nif:isString ?string .
		OPTIONAL { <http://yovisto.com/resource/dataset/iswc2015/doc/281#char=0,4239> dc:date ?date . }
	} LIMIT 1
	""")
	for article in articles:
		news_item_obj=classes.NewsItem(
			content=article['string'],
			identifier="http://yovisto.com/resource/dataset/iswc2015/doc/281#char=0,4239",
			dct=article['date']
		)
		query=""" SELECT ?id ?mention ?start ?end ?gold
		WHERE {
			?id nif:anchorOf ?mention ;
			nif:beginIndex ?start ;
			nif:endIndex ?end ;
			nif:referenceContext <http://yovisto.com/resource/dataset/iswc2015/doc/281#char=0,4239> .
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
