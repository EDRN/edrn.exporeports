# encoding: utf-8
# Copyright 2016 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from setuptools import setup, find_packages
import os.path

# Package data
# ------------

_name            = 'edrn.exporeports'
_version         = '0.0.0'
_description     = 'Reports for the Cancer Data Expo'
_author          = 'Sean Kelly'
_authorEmail     = 'sean.kelly@jpl.nasa.gov'
_maintainer      = 'Sean Kelly'
_maintainerEmail = 'sean.kelly@jpl.nasa.gov'
_license         = 'ALv2'
_namespaces      = ['edrn']
_zipSafe         = False
_keywords        = 'rdf cancer data reports'
_testSuite       = 'edrn.exporeports.tests.test_suite'
_extras          = {}
_requirements    = ['setuptools', 'rdflib']
_entryPoints     = {
    'console_scripts': [
        'csv=edrn.exporeports.csvreports:main',
        'special-protocols=edrn.exporeports.protocols:main'
    ]
}
_classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
]

# Setup Metadata
# --------------
#
# Nothing below here should require updating.


def _read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

_header = '*' * len(_name) + '\n' + _name + '\n' + '*' * len(_name)
_longDescription = _header + '\n\n' + _read('README.rst') + '\n\n' + _read('docs', 'INSTALL.rst') + '\n\n' \
    + _read('docs', 'HISTORY.rst')
open('doc.txt', 'w').write(_longDescription)

setup(
    author=_author,
    author_email=_authorEmail,
    classifiers=_classifiers,
    description=_description,
    entry_points=_entryPoints,
    extras_require=_extras,
    include_package_data=True,
    install_requires=_requirements,
    keywords=_keywords,
    license=_license,
    long_description=_longDescription,
    maintainer=_maintainer,
    maintainer_email=_maintainerEmail,
    name=_name,
    namespace_packages=_namespaces,
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['ez_setup', 'bootstrap']),
    test_suite=_testSuite,
    url='https://github.com/EDRN/' + _name,
    version=_version,
    zip_safe=_zipSafe,
)
