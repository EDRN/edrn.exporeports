# encoding: utf-8

u'''EDRN Protocol Reports — Main'''

from .utils import (
    UnicodeCSVWriter, getStatements, DC_TITLE_URI, CANCER_DATA_EXPO_BASE_URL, BIOMARKER_STUDY_RDF_URL, ECAS_RDF_URL
)
import sys, argparse, rdflib, csv, cStringIO, codecs, logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format=u'%(asctime)s %(levelname)-8s %(message)s')


_biomarkerReferencesURI = rdflib.term.URIRef(u'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#referencesStudy')
_ecasReferencesURI = rdflib.term.URIRef(u'http://edrn.nci.nih.gov/rdf/schema.rdf#protocol')


def main():
    parser = argparse.ArgumentParser(
        description=u"Generates CSV report of special protocols, where 'special' means protocols that have no"
        u" biomarkers but do have science data."
    )
    args = parser.parse_args()
    del args  # Turns out we're not using any
    s = getStatements(CANCER_DATA_EXPO_BASE_URL + u'/rdf-data/protocols/@@rdf')
    protocols = {}
    for subject, predicates in s.iteritems():
        try:
            title = unicode(predicates.get(DC_TITLE_URI)[0])
        except (KeyError, IndexError, TypeError):
            title = u'UNKNOWN'
        protocols[subject] = title
    s = getStatements(BIOMARKER_STUDY_RDF_URL)
    for subject, predicates in s.iteritems():
        try:
            protocolURI = predicates[_biomarkerReferencesURI][0]
            del protocols[protocolURI]
        except (KeyError, IndexError):
            pass
    s = getStatements(ECAS_RDF_URL)
    withData = {}
    for subject, predicates in s.iteritems():
        try:
            protocolURI = predicates[_ecasReferencesURI][0]
            withData[protocolURI] = protocols[protocolURI]
        except (KeyError, IndexError):
            pass
    withData = withData.items()
    withData.sort(lambda a, b: cmp(a[1], b[1]))
    with open('protocols-without-biomarkers-but-with-science-data.csv', 'wb') as output:
        writer = UnicodeCSVWriter(output)
        writer.writerow((u'Protocol URI', u'Title'))
        writer.writerows(withData)
    return 0


if __name__ == '__main__':
    sys.exit(main())
