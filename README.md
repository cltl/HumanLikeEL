# HumanLikeEL
Human-Like Entity Linking using Contextual knowledge

## Running

flasking.py starts a server on localhost:5000. Our current instance is running on http://flask.fii800.lod.labs.vu.nl. This accepts only POST requests with textual input as data. All additional parameters (weights, turning knowledge types ON/OFF) can be supplied as parameters in the query string. See flasking.py for supported parameters.

## Requirements

Our code is written in python 3.
Apart from python dependencies, we use several more things needed to run this system properly:
  1. Pickle JSON with temporal views for december 2007. The keys of this JSON are wikipedia/dbpedia entities, while the values are integers representing their views in this month. 
  2. A neo4j instance that contains all wikilinks, extracted using the code and following the instructions here: https://github.com/erabug/wikigraph
  3. A running Redis instance where we cache: the wikilinks seen once, the LOTUS calls, and additional computationally heavy information.
  4. (optional) Stanford CoreNLP instance - we decided to turn off this for our experiments due to efficiency and accuracy considerations. If you need it, you can use our instance at corenlp.fii800.lod.labs.vu.nl

## Contact
For any considerations, suggestions, questions, or setup troubles, contact Filip Ilievski (f.ilievski@vu.nl).
