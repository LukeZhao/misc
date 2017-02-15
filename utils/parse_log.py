from os import path
from os import listdir
import sys
sys.path.append('/usr/local/virtumedix')

import re
import commands
import imp
import arrow
from main import create_app, exit
from settings import active_config, environment

aconfig = active_config()
app = None
cur_server_ver = None

#re_err = re.compile('(Feb.{10,40}?) api.{1,300}?ultations/(\w{24}).{1,5}?PUT(.{1,900}?)clinician": "(\w{24})".{1,1200}?opentok session', re.DOTALL)
re_err = re.compile('(Feb.{10,40}?) api.{1,300}?ultations/(\w{24}).{1,5}?PUT(.{1,900}?)"([^"]*)", "clinician": "(\w{24})"(.{1,1200}?)"Validation error"', re.DOTALL)
re_cust = re.compile('X-Api-Key: (\w+)', re.DOTALL)
re_reason = re.compile('"description": "([^"]*)"', re.DOTALL)

def main(args=None):

    for ff in listdir('/home/lzhao/test/'):
        f_log = open('/home/lzhao/test/' + ff, 'r')
        cont = f_log.read()
        f_log.close()
        all = re_err.findall(cont)
        for a in all:
            ccc = a[2]
            cu_match = re_cust.search(ccc)
            customer = 'not found'
            if cu_match:
                customer = cu_match.groups()[0]
            reason = 'none'
            rea_match = re_reason.search(a[5])
            if rea_match:
                reason = rea_match.groups()[0]
            print ('{}\t{}\t{}\t{}\t{}\t"{}"'.format(a[0], a[1], a[4], a[3], customer, reason))

if __name__ == '__main__':
     main()
