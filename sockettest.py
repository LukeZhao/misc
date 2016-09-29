from __future__ import absolute_import
from locust import HttpLocust, TaskSet, clients, task, events
from datetime import datetime, timedelta

clients.requests.packages.urllib3.disable_warnings()

TCS_API_KEY = "tcs.virtumedix.web.4.A9Pq0okYxe9y97crtT2MX2xslhA"

import sys
sys.path.append('lib')
import arrow
import io
import string
import websocket
import thread
import time
import json
from main import create_app
app = create_app(schedule_events=False)
app.app_context().push()

class AdminUser(HttpLocust):
    host = 'https://api-virtumedix-vm2.nimaws.com/'

admin = AdminUser()
pat_id = '560dcedd02b9d75f7e663653'
cli_id = '55e7210f02b9d75d61fbe02b'

def on_message(ws, message):
    print message

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

class PatientTasks(TaskSet):

    last_login = None

    @property
    def common_headers(self):
        return {
            "X-API-KEY": TCS_API_KEY,
            "Authorization": "Bearer {}".format(self.auth_token)
        }

    def log_in(self):
        r = self.client.post("account/login",
                            name='Sign in',
                            json={
                            "username": "virtumedix+lukepat@gmail.com",
                            "password": "Password123"
                            }, headers={
                            "X-API-KEY": TCS_API_KEY,
                            })
        data = r.json()
        self.client_id = data['account_id']
        self.auth_token = data['access_token']
        print self.auth_token

    def ensure_login(self):
        if ((not self.last_login or self.last_login + timedelta(minutes=58)
             < datetime.now())):
            self.log_in()
            self.last_login = datetime.now()


    def run_socket(self):
        self.ensure_login()
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("wss://api-virtumedix-vm2.nimaws.com/notifications/tcs.virtumedix.web.4.A9Pq0okYxe9y97crtT2MX2xslhA",
                                    on_message = on_message,
                                    on_error = on_error,
                                    on_close = on_close)
        ws.on_open = self.on_open
        ws.run_forever()
  
    def on_open(self, ws):
        print 'in on_open', ws
        def run(*args):
            print 'in run', ws
            msg = {
                'type': 'auth',
                'time': arrow.get().timestamp,
                'source': pat_id,
                'message': self.auth_token
                }
            print json.dumps(msg)
            ws.send(json.dumps(msg))
            print 'sent auth'
            time.sleep(5)
            for i in range(10):
                time.sleep(10)
                msg = {
                    'type': 'ping',
                    'time': arrow.get().timestamp,
                    'to': 'server',
                    'source': pat_id,
                    'message': 'socket ping'
                    }
                print json.dumps(msg)
                ws.send(json.dumps(msg))
                print 'sent ping {}'.format(i)
            time.sleep(1)
            ws.close()
            print "thread terminating..."
        thread.start_new_thread(run, ())
 
class ClinicianTasks(TaskSet):

    last_login = None

    @property
    def common_headers(self):
        return {
            "X-API-KEY": TCS_API_KEY,
            "Authorization": "Bearer {}".format(self.auth_token)
        }

    def log_in(self):
        r = self.client.post("account/login",
                            name='Sign in',
                            json={
                            "username": "virtumedix+lukedoc@gmail.com",
                            "password": "Password123"
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


class AdminTasks(TaskSet):
    last_login = None

    @property
    def common_headers(self):
        return {
            "X-API-KEY": TCS_API_KEY,
            "Authorization": "Bearer {}".format(self.auth_token)
        }

    def log_in(self):
        r = self.client.post("account/login",
                            name='Sign in',
                            json={
                            "username": "admin@ad.min",
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

def main():
    print 'start'
    pat = PatientTasks(admin)
    doc = ClinicianTasks(admin)
    adminuser = AdminTasks(admin)
    print 'users created'
    try:
        pat.run_socket()
    except Exception as e:
        print e.message


if __name__ == '__main__':
    main()

