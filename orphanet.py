#!/usr/bin/env python

"""

"""

__author__ = 'Orion Buske'

import os
import sys
import re
import logging

from collections import defaultdict
import xml.etree.ElementTree as ET


class Orphanet:
    def __init__(self, lookup_filename, prevalence_filename):
        self.lookup = self.parse_lookup(lookup_filename)
        self.prevalence = self.parse_prevalence(prevalence_filename, 
                                                lookup=self.lookup)

    def average_frequency(self):
        return sum(self.prevalence.values()) / len(self.prevalence)

    @classmethod
    def parse_lookup(cls, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        lookup = {}  # orphanet -> omim
        for disorder in root.findall('.//Disorder'):
            orphanum = disorder.find('OrphaNumber').text
            for ref in disorder.findall('./ExternalReferenceList/ExternalReference'):
                if ref.find('Source').text == 'OMIM':
                    omim = ref.find('Reference').text
                    break

            assert orphanum not in lookup
            lookup[orphanum] = omim

        logging.info('Found {:d} Orphanet->OMIM entries'.format(len(lookup)))
        return lookup

    @classmethod
    def parse_prevalence(cls, filename, lookup=None):
        tree = ET.parse(filename)
        root = tree.getroot()
        prevalence = {}  # id -> prevalence

        prevalence_ids = {
            '12330': 2.5 / 1000,
            '12336': 7.5 / 10000,
            '12342': 2.5 / 10000,
            '12348': 5   / 100000,
            '12354': 5   / 1000000,
            '12360': 0.5 / 1000000,
            '12372': None,
            '12366': None
            }

        n_total = 0
        for disorder in root.findall('.//Disorder'):
            orphanum = disorder.find('OrphaNumber').text
            n_total += 1
            if lookup:
                try:
                    id = lookup[orphanum]
                except KeyError:
                    continue
            else:
                id = orphanum

            prevcls = disorder.find('ClassOfPrevalence')
            if not prevcls:
                continue

            previd = prevcls.get('id')
            prev = prevalence_ids[previd]
            if prev is None:
                continue

            prevalence[id] = prev

        logging.info('Found {:d} prevalences ({:d} dropped)'.format(len(prevalence), n_total - len(prevalence)))
        return prevalence


def script(lookup_filename, prevalence_filename):
    Orphanet(lookup_filename, prevalence_filename)

def parse_args(args):
    from argparse import ArgumentParser
    description = __doc__.strip()
    
    parser = ArgumentParser(description=description)
    parser.add_argument('lookup_filename')
    parser.add_argument('prevalence_filename')
    return parser.parse_args()

def main(args=sys.argv[1:]):
    args = parse_args(args)
    script(**vars(args))

if __name__ == '__main__':
    sys.exit(main())