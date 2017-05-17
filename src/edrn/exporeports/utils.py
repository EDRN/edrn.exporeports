# encoding: utf-8

u'''EDRN Expo Reports — Main'''

import sys, argparse, rdflib, csv, cStringIO, codecs, logging

# Where's the Cancer Data Expo?
CANCER_DATA_EXPO_BASE_URL = u'https://edrn.jpl.nasa.gov/cancerdataexpo/rdf-data'

# And where do we get biomarker data?
BIOMARKER_RDF_URL = u'https://edrn.jpl.nasa.gov/bmdb/rdf/biomarkers'
BIOMARKER_STUDY_RDF_URL = u'https://edrn.jpl.nasa.gov/bmdb/rdf/biomarkerorgans'

# How about science data?
ECAS_RDF_URL = u'http://edrn.jpl.nasa.gov/fmprodp3/rdf/dataset?type=ALL&baseUrl=http://edrn.jpl.nasa.gov/ecas/data/dataset'

# Some common URIs for biomarker-related objects
BIOMARKER_URI = rdflib.term.URIRef(u'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Biomarker')
BIOMARKER_STUDY_DATA_URI = rdflib.term.URIRef(u'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#BiomarkerStudyData')
DC_TITLE_URI = rdflib.term.URIRef(u'http://purl.org/dc/terms/title')

_biomarkerStudyDataURI = rdflib.term.URIRef(u'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#BiomarkerStudyData')
_biomarkerOrganData = rdflib.term.URIRef(u'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#BiomarkerOrganData')
_biomarkerOrganStudyData = rdflib.term.URIRef(u'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#BiomarkerOrganStudyData')
_sensitivityData = rdflib.term.URIRef(u'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#SensitivityData')

# Set up logging
logging.basicConfig(level=logging.DEBUG, format=u'%(asctime)s %(levelname)-8s %(message)s')


class UnicodeCSVWriter(object):
    u'''See https://docs.python.org/2.7/library/csv.html?highlight=csv#examples'''
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)
    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def _parseRDF(graph):
    u'''Convert an RDF graph into a mapping of {s→{p→[o]}} where s is a subject
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
    u'''Return a mapping of statements to predicates to objects for the RDF at url.'''
    g = rdflib.Graph()
    g.load(url)
    return _parseRDF(g)


def _dumpTable(statements, fn):
    u'''Dump statements into a flat tabular CSV file named fn.'''
    # First, figure out what our column headings will be
    columns = set()
    for predicates in statements.itervalues():
        columns.update(frozenset(predicates.keys()))
    columns.remove(rdflib.RDF.type)
    columns = list(columns)
    columns.sort()
    # Now we can dump each row
    keys = statements.keys()
    keys.sort()
    with open(fn, 'wb') as output:
        writer = _UnicodeCSVWriter(output)
        writer.writerow([u'Subject'] + columns)
        for subjectURI in keys:
            predicates = statements[subjectURI]
            objects = []
            for column in columns:
                values = predicates.get(column, [])
                values = u', '.join([unicode(i) for i in values])
                objects.append(values)
            writer.writerow([subjectURI] + objects)


