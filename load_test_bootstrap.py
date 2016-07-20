import sys
from os import path, getcwd
#sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(getcwd())
#import IPython
import arrow
from connections import redis_connection, switch_customer
from main import exit
rds = redis_connection
from sockets import decode_token
from models import Account, Admin

if __name__ == '__main__':
    customer = sys.argv[1] if len(sys.argv) > 1 else 'weppa'
    print '-'*20, '\nCUSTOMER: {}\n'.format(customer), '-'*20
    switch_customer(customer) or exit()

    print '>> creating admin accound....'
    try:
        admin = Admin.objects(email='luke_doc_admin@google.com').first()
        if not admin:
            admin = Admin()
            admin.enabled = True
            admin.first_name = 'Luke'
            admin.last_name = 'Zhao'
            admin.last_name_norm = 'Zhao'
            admin.locale = 'en-us'
            admin.password = Account.generate_password('AdmiN')
            admin.email = 'luke_doc_admin@google.com'
            admin.role = 'admin_clinician'
            admin.save()
        admin = Admin.objects(email='luke_callrep_admin@google.com').first()
        if not admin:
            admin = Admin()
            admin.enabled = True
            admin.first_name = 'Luke'
            admin.last_name = 'Zhao'
            admin.last_name_norm = 'Zhao'
            admin.locale = 'en-us'
            admin.password = Account.generate_password('AdmiN')
            admin.email = 'luke_callrep_admin@google.com'
            admin.role = 'admin_callrep'
            admin.save()
    except Exception as e:
        print e.message
    exit()
