#!/bin/env python

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connections import switch_customer
from models import Consultation
from main import create_app
customer = sys.argv[1] if len(sys.argv) > 1 else 'weppa'

app = create_app(schedule_events=False)
app.app_context().push()
switch_customer(customer) or exit()
print 'first_name\tlast_name\temail'
for con in Consultation.objects(state='pre_queue'):
    print '{}\t{}\t{}'.format(con.patient.first_name,
                              con.patient.last_name,
                              con.patient.email)

