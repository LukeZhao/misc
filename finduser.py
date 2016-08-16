#!/bin/env python

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connections import switch_customer
from models import Consultation
from main import create_app
from integration import aws_ses
customer = sys.argv[1] if len(sys.argv) > 1 else 'weppa'
email_list = ('sam.sager@relymd.com',
              'matthew.cox@relymd.com',
              'david.kammer@relymd.com',
              'Anthony.Araujo@comtechtel.com',
              'maggie.wu@comtechtel.com',
              'zlata.koro@comtechtel.com',
              'Bruce.Rethwisch@comtechtel.com')
app = create_app(schedule_events=False)
app.app_context().push()

def main():
    subject = 'pre_queue users for relymd'
    switch_customer(customer) or exit()
    body = 'first_name\tlast_name\temail\tcreated\n'
    for con in Consultation.objects(state='pre_queue'):
        body = body + '{}\t{}\t{}\t{}\n'.format(con.patient.first_name,
                                  con.patient.last_name,
                                  con.patient.email,
                                  con.created)
    for email in email_list:
        try:
            aws_ses.send_message(email, subject, body)
        except:
            pass

if __name__ == '__main__':
    main()
    exit()

