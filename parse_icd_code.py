# Copyright (C) 2014-2016 TeleCommunications Systems, Inc. All rights reserved.
#
# The information contained herein is confidential and proprietary to
# Networks In Motion, Inc., and is considered a trade secret as
# defined in section 499C of the California Penal Code. Use of this
# information by anyone other than authorized employees of Networks
# In Motion is granted only under a written non-disclosure agreement
# expressly prescribing the scope and manner of such use.
#

import csv
from collections import OrderedDict
import gevent
from itertools import chain, combinations, ifilterfalse, permutations
import os.path
import re
import string
import sys
from xml.dom import minidom
from elasticsearch import TransportError
from elasticsearch.helpers import bulk, scan

from connections import current_customer, redis_connection, search_connection
from settings import live_config, get_logger

log = get_logger(__name__)

rds = redis_connection
es = search_connection

# Blacklist - one time
# filter(lambda x: x not in ['lower', 'injury', 'congenital', 'disease',
#                            'degree', 'right', 'left', 'nec'],
#        dict(Counter(e for rec in rds.zrange('icd', 0, -1)
#                     for e in rec.partition('::')[0].strip().split())
#             .most_common(20)).keys())
BLACK_LIST = ['and', 'type', 'of', 'in', 'unspecified', 'due', 'by', 'to',
              'other', 'specified', 'with', 'or', 'than']

filtered = lambda words: ifilterfalse(lambda x: x in BLACK_LIST, words)

# We need to escape special characters in suggestion lookups before we
# send the search term to elasticsearch.
SPECIAL_CHARS = '+-!(){}:[]^"~*?\\&|'
ESCAPE_RE = re.compile(r'([{}])'.format(re.escape(SPECIAL_CHARS)))
escaped = lambda term: ESCAPE_RE.sub(r'\\\1', term)

def process_icd_index_es():
    print 'Parsing indxe XML...'
    xml1 = minidom.parse('/home/lzhao/lcd10i.xml')
    xml2 = minidom.parse('/home/lzhao/lcd9i.xml')
    code_tags1 = xml1.getElementsByTagName('code')
    code_tags2 = xml2.getElementsByTagName('code')

    map1_a = {}
    map1_b = {}
    map2_a = {}
    map2_b = {}
    for idx, c in enumerate(code_tags1):
        code = c.firstChild.data
        # print 'Code:', code
        tt = []
        node = c
        while True:
            parent = node.parentNode
            try:
                title_tag = parent.getElementsByTagName('title')[0]
                tt.append(' '.join(t.data for t in title_tag.childNodes
                                   if t.nodeType == t.TEXT_NODE))
            except Exception as e:
                print code, tt, e
            if parent.tagName == 'mainTerm':
                break
            node = parent
        desc = ' '.join(reversed(tt))
        # terms = ' '.join(filter(lambda x: x not in string.punctuation,
        #                         desc.lower()).split())
        terms = ' '.join([code.lower()] + desc.lower().split())
        map1_a[code] = desc
        map1_b[code] = terms
    for idx, c in enumerate(code_tags2):
        code = c.firstChild.data
        # print 'Code:', code
        tt = []
        node = c
        while True:
            parent = node.parentNode
            try:
                title_tag = parent.getElementsByTagName('title')[0]
                tt.append(' '.join(t.data for t in title_tag.childNodes
                                   if t.nodeType == t.TEXT_NODE))
            except Exception as e:
                print code, tt, e
            if parent.tagName == 'mainTerm':
                break
            node = parent
        desc = ' '.join(reversed(tt))
        # terms = ' '.join(filter(lambda x: x not in string.punctuation,
        #                         desc.lower()).split())
        terms = ' '.join([code.lower()] + desc.lower().split())
        map2_a[code] = desc
        map2_b[code] = terms
    common = open('/home/lzhao/icdcommon_i.txt', 'w')
    onlyin10 = open('/home/lzhao/only10_i.txt', 'w')
    onlyin9 = open('/home/lzhao/only9_i.txt', 'w')

    for idx, d in map1_a.viewitems():
        if not map2_a.get(idx):
            onlyin10.write(u'{} / {} / {}\r\n'.format(idx, d, map1_b.get(idx)).encode('utf8'))
        else:
            common.write(u'{} / {} / {}\r\n'.format(idx, d, map1_b.get(idx)).encode('utf8'))
    for idx, d in map2_a.viewitems():
        if not map1_a.get(idx):
            onlyin9.write(u'{} / {} / {}\r\n'.format(idx, d, map2_b.get(idx)).encode('utf8'))
    common.close()
    onlyin10.close()
    onlyin9.close()


def process_icd_tabular_es():
    print 'Parsing tabular XML...',
    xml1 = minidom.parse('/home/lzhao/lcd10.xml')
    xml2 = minidom.parse('/home/lzhao/lcd9.xml')
    diag_tags1 = xml1.getElementsByTagName('diag')
    diag_tags2 = xml2.getElementsByTagName('diag')

    map1_a = {}
    map1_b = {}
    map2_a = {}
    map2_b = {}
    for idx, d in enumerate(diag_tags1):
        code = d.getElementsByTagName('name')[0].firstChild.data
        desc = d.getElementsByTagName('desc')[0].firstChild.data
        terms = ' '.join([code.lower()] + desc.lower().split())
        map1_a[code] = desc
        map1_b[code] = terms
    for idx, d in enumerate(diag_tags2):
        code = d.getElementsByTagName('name')[0].firstChild.data
        desc = d.getElementsByTagName('desc')[0].firstChild.data
        terms = ' '.join([code.lower()] + desc.lower().split())
        map2_a[code] = desc
        map2_b[code] = terms

    common = open('/home/lzhao/icdcommon.txt', 'w')
    onlyin10 = open('/home/lzhao/only10.txt', 'w')
    onlyin9 = open('/home/lzhao/only9.txt', 'w')

    for idx, d in map1_a.viewitems():
        if not map2_a.get(idx):
            onlyin10.write(u'{} / {} / {}\r\n'.format(idx, d, map1_b.get(idx)).encode('utf8'))
        else:
            common.write(u'{} / {} / {}\r\n'.format(idx, d, map1_b.get(idx)).encode('utf8'))
    for idx, d in map2_a.viewitems():
        if not map1_a.get(idx):
            onlyin9.write(u'{} / {} / {}\r\n'.format(idx, d, map2_b.get(idx)).encode('utf8'))
    common.close()
    onlyin10.close()
    onlyin9.close()


process_icd_tabular_es()
process_icd_index_es()
