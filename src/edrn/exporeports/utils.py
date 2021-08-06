# encoding: utf-8

'''EDRN Expo Reports — Main'''

import rdflib, logging

# Where's the Cancer Data Expo?
CANCER_DATA_EXPO_BASE_URL = 'https://edrn.jpl.nasa.gov/cancerdataexpo/rdf-data'

# And where do we get biomarker data?
BIOMARKER_RDF_URL = 'https://bmdb.jpl.nasa.gov/rdf/biomarkers'
BIOMARKER_STUDY_RDF_URL = 'https://bmdb.jpl.nasa.gov/rdf/biomarker-organs'

# How about science data?
ECAS_RDF_URL = 'https://edrn.jpl.nasa.gov/cancerdataexpo/rdf-data/labcas/@@rdf'

# Some common URIs for biomarker-related objects
BIOMARKER_URI = rdflib.term.URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Biomarker')
BIOMARKER_STUDY_DATA_URI = rdflib.term.URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#BiomarkerStudyData')
DC_TITLE_URI = rdflib.term.URIRef('http://purl.org/dc/terms/title')

_biomarkerStudyDataURI = rdflib.term.URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#BiomarkerStudyData')
_biomarkerOrganData = rdflib.term.URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#BiomarkerOrganData')
_biomarkerOrganStudyData = rdflib.term.URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#BiomarkerOrganStudyData')
_sensitivityData = rdflib.term.URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#SensitivityData')

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s')


def _parseRDF(graph):
    '''Convert an RDF graph into a mapping of {s→{p→[o]}} where s is a subject
    URI, p is a predicate URI, and o is a list of objects which may be literals
    or URI references.
    '''
    statements = {}
    for s, p, o in graph:
        predicates = statements.get(s, {})
        statements[s] = predicates
        objects = predicates.get(p, [])
        predicates[p] = objects
        objects.append(o)
    return statements


def getStatements(url):
    '''Return a mapping of statements to predicates to objects for the RDF at url.'''
    g = rdflib.Graph()
    g.load(url)
    return _parseRDF(g)
