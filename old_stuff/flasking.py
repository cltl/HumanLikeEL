from flask import Flask, request, Response
from rdflib import Graph, URIRef
app = Flask(__name__)
import pickle
import nif_system
import json

#fullText = URIRef("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#isString")
#entityMention = URIRef("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#anchorOf")
mimetype='application/x-turtle'

w=open('flask.log', 'a')

def normalizeWeights(fw):
	total=sum(fw.values())
	for k in fw:
		fw[k]/=total
	return fw

@app.route("/", methods = ['POST'])
def run():
	global num
	num+=1
	g=Graph()
	inputRDF=request.stream.read()
	w.write(str(inputRDF) + '\n')
	g.parse(data=inputRDF, format="n3")

	#### DEFAULTS ####
	memory=1 # By default, cross-document knowledge is ON
	iterations=2 # By default, rereading is ON (2 iterations)
	factorWeights={'wc':0.525,'wss': 0.325, 'wa': 0.05, 'wr':0.05, 'wt': 0.05}
	limits={'l1':0.375, 'l2': 0.54}
	lcoref=True
	order=True
	tp=True
	month='200712'
	N=10
	#### end DEFAULTS ####

	#### PARAMETERS ####
	args=request.args
	if args.get('crossdoc'): # Check if the cross-document bool has been supplied
		memory=int(args.get('crossdoc'))
	if args.get('iter'): # Check if iterations number has been supplied
		iterations=int(args.get('iter'))
	if args.get('lcoref') and int(args.get('lcoref'))==0:
		lcoref=False
		factorWeights['wr']=0.0
	if args.get('order') and int(args.get('order'))==0:
		order=False
	if args.get('tp') and int(args.get('tp'))==0:
		tp=False
		factorWeights['wt']=0.0
	if args.get('month'):
		month=args.get('month')
	for k in factorWeights.keys(): # Check if any weight is explicitly modified
		if args.get(k):
			factorWeights[k]=args.get(k)
	factorWeights=normalizeWeights(factorWeights)
	for limit in ['l1', 'l2']:
		if args.get(limit):
			limits[limit]=args.get(limit)
	if args.get('N'):
		N=args.get('N')
	#### end PARAMETERS ####

	print("Request %d came! %d iterations, Memory: %r, Local coreference: %r, Order: %r, Time popularity: %r, scoring weights: %s, limits: %s, N: %d" % (num, iterations, memory>0, lcoref, order, tp, json.dumps(factorWeights), json.dumps(limits), N))
	#print("Normalized weights: " + factorWeights)
	if tp:
		timePickle=pickle.load(open(month + '_agg.p', 'rb'))
	else:
		timePickle={}
	global lastN
	if memory==0:
		lastN=[]
	g,lastN=nif_system.run(g, factorWeights, timePickle, iterations, lcoref, order, lastN, limits, N)

	outputRDF=g.serialize(format='turtle')
	#w.write(str(outputRDF) + '\n')
	
	return Response(outputRDF, mimetype=mimetype)

if __name__ == "__main__":
	global num
	num=0
	global lastN
	lastN=[]
	app.run()
