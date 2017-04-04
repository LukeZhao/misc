import sys
sys.path.append('/usr/local/virtumedix')
sys.path.append('lib')
sys.path.append('.')
import arrow
import io
import string
import json
from connections import (redis_connection, current_customer,
                         switch_customer)
from models import AuditLog
import proto_models
from settings import active_config, live_config
from main import create_app
app = create_app(schedule_events=False)
app.app_context().push()
aconfig = active_config()

def get_stat(cust, tt):
    switch_customer(cust)
    dev = {}
    for c in AuditLog.objects(method='Login', time__gt=tt):
        d = c.arguments.get('device', None)
        v = c.arguments.get('version', None)
        if not v:
            v = 'None'
        if d:
            if d.startswith('iP'):
                d = 'ios'
            else:
                d = 'android'
            n = dev.get(d, None)
            if n:
                vc = n.get(v, None)
                if vc:
                    n[v] = vc + 1
                else:
                    n[v] = 1
            else:
                dev[d] = {v: 1}
    return dev


if __name__ == '__main__':

    tt = arrow.get().replace(days=-365).naive
    for cust in aconfig['CUSTOMERS']:
        stats = get_stat(cust, tt)
        print('customer: {}'.format(cust))
        for k in stats.keys():
            print('  platform: {}'.format(k))
            vers = stats.get(k)
            vk = sorted(vers.keys())
            for v in vk:
                print ('    {}\t{}'.format(v, vers.get(v)))

    tt = arrow.get().replace(hours=-12).naive
    for cust in aconfig['CUSTOMERS']:
        stats = get_stat(cust, tt)
        print('customer: {}'.format(cust))
        for k in stats.keys():
            print('  platform: {}'.format(k))
            vers = stats.get(k)
            vk = sorted(vers.keys())
            for v in vk:
                print ('    {}\t{}'.format(v, vers.get(v)))
