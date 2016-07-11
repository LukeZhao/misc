import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import IPython
from connections import redis_connection, switch_customer
from main import exit
rds = redis_connection
from sockets import decode_token
from models import Account

if __name__ == '__main__':
    customer = sys.argv[1] if len(sys.argv) > 1 else 'weppa'
    print '-'*20, '\nCUSTOMER: {}\n'.format(customer), '-'*20
    switch_customer(customer) or exit()

    print '>> cleaning staled sessions:uid:*....'
    cnt = 0
    for key in rds.keys('sessions:uid:*'):
        if rds.ttl(key) == -1:
            uid = key.split(':')[2]
            acc = Account.objects(id=uid).no_dereference().first()
            if ((acc and acc.id.generation_time
                 < arrow.get().replace(days=-30))):
                cnt += 1
                rds.expire(key, 0)
    print '    Done total cleaned: {}'.format(cnt)

    print '>> cleaning staled queue:session:*....'
    cnt = 0
    for key in rds.keys('queue:session:*'):
        if rds.ttl(key) == -1:
            token = key.split(':')[2]
            try:
                tok = decode_token(token)
                uid = tok.get('user_id')
                acc = Account.objects(id=uid).no_dereference().first()
                if ((acc and acc.id.generation_time
                     < arrow.get().replace(days=-30))):
                    cnt += 1
                    rds.expire(key, 0)
            except:
                cnt += 1
                rds.expire(key, 0)
    print '    Done total cleaned: {}'.format(cnt)

    print '>> cleaning staled clients tokens....'
    cnt = 0
    for token in rds.hkeys('clients'):
        try:
            tok = decode_token(token)
            uid = tok.get('user_id')
            key = 'sessions:uid:{}'.format(uid)
            if rds.ttl(key) == -2:
                cnt += 1
                rds.hdel('clients', token)
        except:
            cnt += 1
            rds.hdel('clients', token)
    print '    Done total cleaned: {}'.format(cnt)

    exit()