# encoding: utf-8

u'''EDRN Expo Reports — Main'''

import sys, argparse, rdflib, csv, cStringIO, codecs, logging

# Where's the Cancer Data Expo?
_cancerDataExpoBaseURL = u'https://edrn.jpl.nasa.gov/cancerdataexpo/rdf-data'

# Some common URIs for biomarker-related objects
_biomarkerURI = rdflib.term.URIRef(u'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Biomarker')
_biomarkerStudyDataURI = rdflib.term.URIRef(u'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#BiomarkerStudyData')
_biomarkerOrganData = rdflib.term.URIRef(u'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#BiomarkerOrganData')
_biomarkerOrganStudyData = rdflib.term.URIRef(u'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#BiomarkerOrganStudyData')
_sensitivityData = rdflib.term.URIRef(u'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#SensitivityData')

# Set up logging
logging.basicConfig(level=logging.DEBUG, format=u'%(asctime)s %(levelname)-8s %(message)s')


class _UnicodeCSVWriter(object):
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


def _getStatements(url):
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


def _dumpBodySystems():
    s = _getStatements(_cancerDataExpoBaseURL + u'/rdf-data/body-systems/@@rdf')
    _dumpTable(s, 'organs.csv')


def _dumpDiseases():
    s = _getStatements(_cancerDataExpoBaseURL + u'/rdf-data/diseases/@@rdf')
    _dumpTable(s, 'diseases.csv')


def _dumpPublications():
    dmcc = _getStatements(_cancerDataExpoBaseURL + u'/rdf-data/publications/@@rdf')
    bmdb = _getStatements(u'https://edrn.jpl.nasa.gov/bmdb/rdf/publications')
    bmdb.update(dmcc)
    _dumpTable(bmdb, 'publications.csv')


def _dumpSites():
    s = _getStatements(_cancerDataExpoBaseURL + u'/rdf-data/sites/@@rdf')
    _dumpTable(s, 'sites.csv')


def _dumpPeople():
    s = _getStatements(_cancerDataExpoBaseURL + u'/rdf-data/registered-person/@@rdf')
    _dumpTable(s, 'people.csv')


def _dumpCommittees():
    s = _getStatements(_cancerDataExpoBaseURL + u'/rdf-data/committees/@@rdf')
    _dumpTable(s, 'committees.csv')


def _dumpProtocols():
    s = _getStatements(_cancerDataExpoBaseURL + u'/rdf-data/protocols/@@rdf')
    _dumpTable(s, 'protocols.csv')


def _dumpBiomarkers():
    statements = _getStatements(u'https://edrn.jpl.nasa.gov/bmdb/rdf/biomarkers')
    moreStatements = _getStatements(u'https://edrn.jpl.nasa.gov/bmdb/rdf/biomarkerorgans')
    statements.update(moreStatements)
    bags, biomarkers, bmosd, bmos, senses, studies = {}, {}, {}, {}, {}, {}
    for subjectURI, predicates in statements.iteritems():
        objectType = predicates[rdflib.RDF.type][0]
        if objectType == rdflib.RDF.Bag:
            # the predicates (aside from type) are all of the form
            # http://www.w3.org/1999/02/22-rdf-syntax-ns#_1
            # http://www.w3.org/1999/02/22-rdf-syntax-ns#_2
            # etc.
            # and the values for those predicates are single-item sequences for URIs to other objects
            linkedItems = []
            for predicate, objects in predicates.iteritems():
                if predicate == rdflib.RDF.type: continue
                linkedItems.append(objects[0])
            bags[subjectURI] = linkedItems
        elif objectType == _biomarkerURI:
            biomarkers[subjectURI] = predicates
        elif objectType == _biomarkerOrganStudyData:
            bmosd[subjectURI] = predicates
        elif objectType == _biomarkerOrganData:
            bmos[subjectURI] = predicates
        elif objectType == _sensitivityData:
            senses[subjectURI] = predicates
        elif objectType == _biomarkerStudyDataURI:
            studies[subjectURI] = predicates
        else:
            raise KeyError('Unknown RDF object type "{}"'.format(objectType))
    _dumpTable(biomarkers, 'biomarkers.csv')
    _dumpTable(bmosd, 'biomarker-organ-study-data.csv')
    _dumpTable(bmos, 'biomarker-organ-data.csv')
    _dumpTable(senses, 'sensitivity-data.csv')
    _dumpTable(studies, 'biomarker-studies.csv')
    with open('collections.csv', 'wb') as output:
        writer = _UnicodeCSVWriter(output)
        writer.writerow([u'Collection ID', u'Members'])
        for subjectURI, members in bags.iteritems():
            writer.writerow((subjectURI, u', '.join([unicode(i) for i in members])))


def main():
    parser = argparse.ArgumentParser(description=u"Generates CSV reports of EDRN's CancerDataExpo")
    args = parser.parse_args()
    del args  # Turns out we're not using any
    _dumpBodySystems()
    _dumpDiseases()
    _dumpPublications()
    _dumpSites()
    _dumpPeople()
    _dumpCommittees()
    _dumpProtocols()
    _dumpBiomarkers()
    return 0


if __name__ == '__main__':
    sys.exit(main())
