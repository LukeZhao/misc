#!/bin/env python
import sys
from os import path
import datetime
sys.path.append('.')
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import arrow
from connections import switch_customer, redis_connection, current_customer
import settings
import events
from models import *
from main import create_app
from elasticsearch import Elasticsearch
import elasticsearch_dsl as edsl
config = active_config()
hosts = tuple(config['EVENTS_HOSTS'])
search_connection = Elasticsearch(hosts)
edsl.connections.connections.add_connection('default', search_connection)

app = create_app(schedule_events=False)
app.app_context().push()


def search(query='*', types=[], fields=[],
           start=arrow.get().naive, end=arrow.get().naive,
           sort_by='created'):
    events.Event.__subclasses__
    s = events.Event.search().sort(sort_by)
    f = edsl.F('range', created={'gte': start, 'lt': end})
    if types:
        if isinstance(types, basestring):
            types = [types]
        ff = edsl.F('term', type='dummy')
        for t in types:
            ff |= edsl.F('term', type=t)
        f &= ff
    s = s.filter(f)
    if fields:
        s = s.fields(fields)
    ss = s.query('query_string', query=query)
    ss = ss.execute()
    total_time = 0
    net_time = 0
    total_request = 0
    by_ends = {}
    t_size = ss.hits.total
    page = 1
    per_page = 1000
    while t_size > 0:
        ss = s.query('query_string', query=query)
        ss = ss[(page-1)*per_page:page*per_page].execute()
        for r in ss.hits.hits:
            sss = r.get('_source')
            total_request = total_request + 1
            total_time = total_time + sss.get('total_time')
            net_time = net_time + sss.get('func_time')
            key = '{}_{}'.format(sss.get('func'), sss.get('method'))
            rec = by_ends.get(key, None)
            if rec is None:
                by_ends[key] = {'c':0, 't': 0, 'n': 0, 'k': key}
                rec = by_ends.get(key)
            rec['c'] = rec['c'] + 1
            rec['t'] = rec['t'] + sss.get('total_time')
            rec['n'] = rec['n'] + sss.get('func_time')
        t_size = t_size - per_page
        page = page + 1
    return (total_request, total_time, net_time, by_ends)

def page(*args, **kwargs):
    return search(*args, **kwargs)

if __name__ == '__main__':
    customer = sys.argv[1] if len(sys.argv) > 1 else 'weppa'
    ss = sys.argv[2].split(':')
    ee = sys.argv[3].split(':')
    start = arrow.get().replace(hours=-int(ss[0]), minutes=-int(ss[1])).naive
    end = arrow.get().replace(hours=-int(ee[0]), minutes=-int(ee[1])).naive
    try:
        # find RT and websocket message.
        switch_customer(customer)
        (cnt, total, net, ends) = page(types=['request'], start=start, end=end)
        recs = ends.values()
        for rec in recs:
            rec['a'] = rec['t']/rec['c']
        recs.sort(key=lambda x: x['a'], reverse=True)
        print('Cnt: {}, Total: {}, Net: {}, Avg: {}'.format(cnt, "%.2f" % total, "%.2f" % net, "%.2f" % (total/cnt)))
        for rec in recs:
            print rec['k'].rjust(40), repr(rec['c']).rjust(10), ("%.2f" % rec['t']).rjust(10), ("%.2f" % rec['n']).rjust(10), ("%.2f" % rec['a']).rjust(5)
    except:
        raise
        print("unhandled_exception")
        sys.exit(1)
