#!/bin/env python

import sys
from os import path
sys.path.append('.')
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import arrow
from connections import switch_customer, redis_connection, current_customer
import settings
from models import *
from main import create_app
import json

app = create_app(schedule_events=False)
app.app_context().push()
pat_template = 'virtumedix+loadtests_patient_{}@gmail.com'
doc_template = 'virtumedix+loadtests_clinician_{}@gmail.com'
BAT_CNT = 1000

consult_json = json.loads('{"method_of_contact":"video","chief_complaint":"CCCCC","phone_contact":'
                '{"country_code":"1","number":"3123334444"},"location":"CA","payment":'
                '{"transaction_id":"tok_19E44f2eZvKYlo2CYrevgaZX","vendor":"stripe","option":"full"},'
                '"patient":"55a4050002b9d7543bbda08b", "clinician": "55a4050002b9d7543bbda08b"}')

def create_consults(count):
    docs = Clinician.objects(email__istartswith='virtumedix+loadtests_clinician_').no_dereference().values_list('id')
    pats = Patient.objects(email__istartswith='virtumedix+loadtests_patient_').no_dereference().values_list('id')
    consults = []
    doc_len = len(docs)
    pat_len = len(pats)
    for i in range(count/10 + 1):
        con = Consultation(**consult_json)
        con.patient = str(pats[i % pat_len])
        con.clinician = str(docs[i % doc_len])
        con.chief_complaint = 'upload test complaint {}'.format(i)
        con.state = 'consultation_complete'
        consults.append(con)
    for i in range(10):
        Consultation.objects.insert(consults, load_bulk=False)
        print 'created {} consults'.format(count/10 + 1)


if __name__ == '__main__':
    customer = sys.argv[1]
    action = sys.argv[2]
    if action not in ('consult', 'account'):
        print 'usage: python accounts_setup.py customer consult|account'
        sys.exit(0)

    try:
        switch_customer(customer)
        if action == 'consult':
            create_consults(200000)
            sys.exit(0)
        PWD = Account.generate_password('Password123')
        # clean all existing accounts and consults.
        cli_ids = Clinician.objects(email__istartswith='virtumedix+loadtests_clinician_').no_dereference().values_list('id')
        Consultation.objects(clinician__in=cli_ids).delete()
        print('removed consults for all load test clinicians')
        Patient.objects(email__istartswith='virtumedix+loadtests_patient').delete()
        print('removed all load test patients')
        Clinician.objects(email__istartswith='virtumedix+loadtests_clinician').delete()
        print('removed all load test clinicians')
        Admin.objects(email__istartswith='virtumedix+loadtests_admin').delete()
        print('removed all load test admins')

        ph = Phone()
        ph.number = '9496667777'
        ph.country_code = '1'

        for role in ('system', 'admin_clinician', 'admin_callrep'):
            admin = Admin()
            admin.enabled = True
            admin.email_verified = True
            admin.first_name = 'AdminFirst'
            admin.last_name = 'AdminLast'
            admin.last_name_norm = admin.last_name.lower()
            admin.phone_number = '9496667777'
            admin.phone = ph
            admin.locale = 'en-us'
            admin.password = PWD
            admin.email = 'virtumedix+loadtests_admin_{}@gmail.com'.format(role)
            admin.role = role
            admin.save()

        # Create new accounts.
        pats = []
        for ii in range(1, 200001):
            pat = Patient()
            pat.first_name = 'PatFirstName_{}'.format(ii)
            pat.last_name = 'PatLastName_{}'.format(ii)
            pat.email = pat_template.format(ii)
            pat.last_name_norm = pat.last_name.lower()
            pat.phone_number = '9496667777'
            pat.phone = ph
            pat.password = PWD
            pat.gender = 'male'
            pat.timezone = 'US/Eastern'
            pat.birthdate = arrow.get().replace(years=-28).naive
            pat.enabled = True
            pat.email_verified = True
            pat.locale = 'en_US'
            pats.append(pat)
            if len(pats) > BAT_CNT * 10:
                Patient.objects.insert(pats, load_bulk=False)
                print('created {} patients'.format(BAT_CNT * 10))
                pats = []
        if pats:
            Patient.objects.insert(pats, load_bulk=False)
        print('created all patients')
        docs = []
        for ii in range(1, 5001):
            doc = Clinician()
            doc.first_name = 'DocFirstName_{}'.format(ii)
            doc.last_name = 'DocLastName_{}'.format(ii)
            doc.email = doc_template.format(ii)
            doc.last_name_norm = doc.last_name.lower()
            doc.phone_number = '9496667777'
            doc.phone = ph
            doc.password = PWD
            doc.gender = 'female'
            doc.timezone = 'US/Eastern'
            doc.birthdate = arrow.get().replace(years=-32).naive
            doc.enabled = True
            doc.state = 'tertiary'
            doc.email_verified = True
            doc.locale = 'en_US'
            doc.notification_preference = 'push'
            docs.append(doc)
            if len(docs) > BAT_CNT:
                Clinician.objects.insert(docs, load_bulk=False)
                print('created {} clinicians'.format(BAT_CNT))
                docs = []
        if docs:
            Clinician.objects.insert(docs, load_bulk=False)
        print('created all clinicians')
    except:
        raise
        print("unhandled_exception")
        sys.exit(1)

