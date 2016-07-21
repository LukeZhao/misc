import sys
import flask
from os import path, getcwd
#sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(getcwd())
#import IPython
import arrow
from connections import redis_connection, switch_customer, local
from main import exit, create_app
rds = redis_connection
from sockets import decode_token
from models import Account, Admin
import traceback
from settings import active_config, live_config

app = create_app(schedule_events=False)
app.app_context().push()
client = app.test_client()
config = active_config()

if __name__ == '__main__':
    customer = sys.argv[1] if len(sys.argv) > 1 else 'weppa'
    print '-'*20, '\nCUSTOMER: {}\n'.format(customer), '-'*20
    switch_customer(customer) or exit()

    print '>> creating admin account....'
    try:
        admin = Admin.objects(email='admin@ad.min').first()
        if not admin:
            admin = Admin()
            admin.enabled = True
            admin.first_name = 'Luke'
            admin.last_name = 'Zhao'
            admin.last_name_norm = 'Zhao'
            admin.locale = 'en-us'
            admin.password = Account.generate_password('AdmiN')
            admin.email = 'admin@ad.min'
            admin.role = 'system'
            admin.save()
        else:
            admin.password = Account.generate_password('AdmiN')
            admin.save()
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
        traceback.print_exc(file=sys.stdout)
        print e.message
    exit()
