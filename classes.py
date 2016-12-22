class Candidate:
	"""
	class containing information about an entity candidate
	"""

	def __init__(self, subject, predicate="", string="", the_type=None, 
		lotus_score=0.0, tp_score=0.0, pr_score=0.0, ss_score=0.0):
		self.subject = subject		 # e.g. John_Smith 
		self.predicate = predicate 	 # e.g. dbo:label
		self.string = string             # e.g. "John Smith" -> the mention of an entity as found in text
		self.the_type = the_type         # e.g. "Person" | "http://dbpedia.org/ontology/Person"
		self.lotus_score = lotus_score	 # rank according to lotus (e.g. 3)
		self.tp_score = tp_score 	 # score according on temporal popularity
		self.pr_score = pr_score	 # score according to pagerank
		self.ss_score = ss_score		 # string similarity to the entity mention

class EntityMention:
    """
    class containing information about an entity mention
    """

    def __init__(self, mention, 
                 begin_index, end_index,
                 gold_link=None,
		 the_type=None, sentence=None, sys_link=None): #, exact_match=False):
        self.sentence = sentence         # e.g. 4 -> which sentence is the entity mentioned in
        self.mention = mention           # e.g. "John Smith" -> the mention of an entity as found in text
        self.the_type = the_type         # e.g. "Person" | "http://dbpedia.org/ontology/Person"
        self.begin_index = begin_index   # e.g. 15 -> begin offset
        self.end_index = end_index       # e.g. 25 -> end offset
        self.gold_link = gold_link	 # gold link if existing
        self.candidates = set()		 # candidates from LOTUS
        self.sys_link = sys_link	 # final system link
        self.previous_mentions = set() 	 # previous coreferential mentions of the same entity

class NewsItem:
    """
    class containing information about a news item
    """
    def __init__(self, identifier, content="", collection=None,
                 dct=None, publisher=None, 
                 domain=None):
        self.identifier = identifier  # string, the original document name in the dataset
        self.collection = collection  # which collection does it come from (one of ECB+, SignalMedia, or some WSD dataset)
        self.dct = dct                # e.g. "2005-05-14T02:00:00.000+02:00" -> document creation time
        self.publisher = publisher    # e.g. "Reuters" -> Who is the publisher of the document (e.g. Reuters)
        self.domain = domain          # e.g. "crime"  -> one of the topics/domains (we could also use URI identifiers for these if we want to keep more information)
        self.content = content	      # the text of the news article
        self.entity_mentions = []  # set of instances of EntityMention class


class Publisher:
    """
    class containing information about a publisher
    """
    def __init__(self, name, dbpedia_uri, homepage, location_dbpedia_uri):
        self.name = name
        self.dbpedia_uri = dbpedia_uri
        self.homepage = homepage
        self.location_dbpedia_uri = location_dbpedia_uri
