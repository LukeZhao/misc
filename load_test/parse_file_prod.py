#!/bin/env python
import sys
from os import path
import datetime
sys.path.append('.')
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import arrow

if __name__ == '__main__':
    customer = sys.argv[1] if len(sys.argv) > 1 else 'weppa'
    ss = sys.argv[2].split(':')
    ee = sys.argv[3].split(':')
    start = arrow.get().replace(hours=-int(ss[0]), minutes=-int(ss[1])).naive
    end = arrow.get().replace(hours=-int(ee[0]), minutes=-int(ee[1])).naive
    tt_seconds = int((end - start).total_seconds())
    try:
        # parse log file.
        apilog = open('/var/log/nginx/api.virtumedix.com_access.log')
        api_calls = {}
        api_response_time = 0
        for line in apilog:
            fs = line.split(' ')
            if fs[6][1:] == 'OPTIONS':
                continue
            tt = datetime.datetime.strptime(fs[3][1:], '%d/%b/%Y:%H:%M:%S')
            if tt < start:
                continue
            if tt > end:
                break
            cc = fs[-1][1:]
            cc = cc.split('.')[0]
            if cc != customer:
                continue
            url = fs[6].split('?')[0]
            api_response_time = api_response_time + float(fs[10])
            if api_calls.get(url):
                api_calls[url] = api_calls[url] + 1
            else:
                api_calls[url] = 1
        total_calls = 1;
        for url in api_calls.keys():
            total_calls = total_calls + api_calls[url]
            print('{} - {}'.format(api_calls[url], url))
        print('Total calls: {}'.format(total_calls))
        print('Total response time: {}'.format(api_response_time))
        api_response_time = api_response_time + 1
        print('Average: {} s/api call'.format(api_response_time/total_calls))
        print('Request rate: {}/s'.format(float(total_calls)/tt_seconds))

    except:
        raise
        print("unhandled_exception")
        sys.exit(1)