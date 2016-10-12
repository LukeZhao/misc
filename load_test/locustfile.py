from __future__ import absolute_import
from locust import HttpLocust, TaskSet, clients, task, events
from datetime import datetime, timedelta

clients.requests.packages.urllib3.disable_warnings()

TCS_API_KEY = "tcs.virtumedix.web.3.xGZTElmkstoLdKWpM-Q67_D6p5w"


class AdminTasks(TaskSet):

    last_login = None

    @property
    def common_headers(self):
        return {
            "X-API-KEY": TCS_API_KEY,
            "Authorization": "Bearer {}".format(self.auth_token)
        }

    def log_in(self):
        dd = datetime.now()
        if dd.microsecond % 3 == 0:
            r = self.client.post("account/login",
                             name='Sign in',
                             json={
                                "username": "admin@ad.min",
                                "password": "AdmiN"
                             }, headers={
                                "X-API-KEY": TCS_API_KEY,
                             })
        elif dd.microsecond % 3 == 1:
            r = self.client.post("account/login",
                             name='Sign in',
                             json={
                                "username": "luke_doc_admin@google.com",
                                "password": "AdmiN"
                             }, headers={
                                "X-API-KEY": TCS_API_KEY,
                             })
        else:
            r = self.client.post("account/login",
                             name='Sign in',
                             json={
                                "username": "luke_callrep_admin@google.com",
                                "password": "AdmiN"
                             }, headers={
                                "X-API-KEY": TCS_API_KEY,
                             })
        data = r.json()
        self.client_id = data['account_id']
        self.auth_token = data['access_token']

    def ensure_login(self):
        if ((not self.last_login or self.last_login + timedelta(minutes=58)
             < datetime.now())):
            self.log_in()
            self.last_login = datetime.now()

    def on_start(self):
        self.ensure_login()

    @task
    def profile(self):
        self.ensure_login()
        self.client.get("v1/admins/{}".format(self.client_id),
                        name="Get Admin Profile",
                        headers=self.common_headers)

    @task
    def shared_config(self):
        self.ensure_login()
        self.client.get("config/shared",
                        name="Download Shared Configuration",
                        headers=self.common_headers)

    @task
    def patients(self):
        self.ensure_login()
        self.client.get("v3/patients?count=15&fields=account_id,enabled,"
                        "first_name,%2Blast_name,email,group_id,phone_number,"
                        "email_verified,dependents,master_id&master_id=null"
                        "&page_number=1",
                        name="List Patients",
                        headers=self.common_headers)

    @task
    def clinicians(self):
        self.ensure_login()
        self.client.get("v3/clinicians?count=15&fields=account_id,enabled,"
                        "first_name,%2Blast_name,email,phone_number,"
                        "email_verified&page_number=1",
                        name="List Clinicians",
                        headers=self.common_headers)

    @task
    def callreps(self):
        self.ensure_login()
        self.client.get("v3/callreps?count=15&fields=account_id,enabled,"
                        "first_name,%2Blast_name,email,phone_number,"
                        "email_verified&page_number=1",
                        name="List Callreps",
                        headers=self.common_headers)

    @task
    def admins(self):
        self.ensure_login()
        self.client.get("v3/admins?count=15&fields=account_id,enabled,"
                        "first_name,%2Blast_name,email,phone_number,"
                        "email_verified,role&page_number=1",
                        name="List Admins",
                        headers=self.common_headers)


def failure_handler(**kw):
    try:
        for key, val in kw.viewitems():
            print key, unicode(val)
    except Exception as e:
        print e.message


events.request_failure += failure_handler

class AdminUser(HttpLocust):
    task_set = AdminTasks
    min_wait = 3000
    max_wait = 7000

