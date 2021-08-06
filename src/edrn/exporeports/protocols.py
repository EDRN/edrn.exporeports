# encoding: utf-8

'''EDRN Protocol Reports — Main'''

from .utils import (
    getStatements, DC_TITLE_URI, CANCER_DATA_EXPO_BASE_URL, BIOMARKER_STUDY_RDF_URL, ECAS_RDF_URL
)
import sys, argparse, rdflib, logging, ssl, csv

# Work around edrn.jpl.nasa.gov's weird certificate:
ssl._create_default_https_context = ssl._create_unverified_context


# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s')


_biomarkerReferencesURI = rdflib.term.URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#referencesStudy')
_ecasReferencesURI = rdflib.term.URIRef('http://edrn.nci.nih.gov/rdf/schema.rdf#protocol')


def main():
    '''Generate CSV report of special protocols, where 'special' means
    protocols that have no biomarkers but do have science data.
    '''
    parser = argparse.ArgumentParser(
        description="Generates CSV report of special protocols, where 'special' means protocols that have no"
        " biomarkers but do have science data."
    )
    args = parser.parse_args()
    del args  # Turns out we're not using any
    s = getStatements(CANCER_DATA_EXPO_BASE_URL + '/rdf-data/protocols/@@rdf')
    protocols = {}
    for subject, predicates in s.items():
        try:
            title = str(predicates.get(DC_TITLE_URI)[0])
        except (KeyError, IndexError, TypeError):
            title = 'UNKNOWN'
        protocols[subject] = title
    s = getStatements(BIOMARKER_STUDY_RDF_URL)
    for subject, predicates in s.items():
        try:
            protocolURI = predicates[_biomarkerReferencesURI][0]
            del protocols[protocolURI]
        except (KeyError, IndexError):
            pass
    s = getStatements(ECAS_RDF_URL)
    withData = {}
    for subject, predicates in s.items():
        try:
            protocolURI = predicates[_ecasReferencesURI][0]
            withData[protocolURI] = protocols[protocolURI]
        except (KeyError, IndexError):
            pass
    withData = sorted(withData.items(), key=lambda x: x[1])
    with open('protocols-without-biomarkers-but-with-science-data.csv', 'w') as output:
        writer = csv.writer(output)
        writer.writerow(('Protocol URI', 'Title'))
        writer.writerows(withData)
    return 0


if __name__ == '__main__':
    sys.exit(main())
