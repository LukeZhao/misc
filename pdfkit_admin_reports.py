#!/bin/env python
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import create_app
# pip install cairosvg==1.0.14
# pip install wkhtmltopdf //wkhtmltopdf-0.2
import arrow
import json
import math
from collections import OrderedDict, defaultdict
from connections import current_customer, get_logo_url
from weasyprint import HTML, CSS
import pdfkit

from flask import render_template

from models import DCI
from settings import live_config, get_logger

log = get_logger('tasks')


app = create_app(schedule_events=False)
app.app_context().push()


def create_admin_report(locale, header, result, title):
    template = '{}/{}/admin_report.html'.format(current_customer, locale)
    html_str = render_template(template,
                               **{'logo': get_logo_url(),
                                  'header': header,
                                  'result': result,
                                  'title': title})
    css = CSS('templates/{}/{}/admin_report.css'.format(current_customer,
                                                        locale))
    doc = HTML(string=html_str).render(stylesheets=[css])
    pages = [page for page in doc.pages]
    if pages:
        pdf = doc.copy(pages).write_pdf()
        f = open('/home/lzhao/weasypdf_admin_login_report.pdf', 'w')
        f.write(pdf)
        f.close()


def create_admin_report_pdfkit(locale, header, result, title):
    template = '{}/{}/admin_report.html'.format(current_customer, locale)
    html_str = render_template(template,
                               **{'logo': get_logo_url(),
                                  'header': header,
                                  'result': result,
                                  'title': title})
    css = 'templates/{}/{}/admin_report.css'.format(current_customer, locale)

    output = '/home/lzhao/pdfkit_admin_login_report.pdf'
    pdfkit.from_string(html_str, output, css=css)


def main():
    locale = 'en_US'
    header = [[u'Start Date', '2/27/2017'], [u'End Date', '3/5/2017'], [u'Number of Unique Users', 3]]
    result = [[u'Row #', u'Date', u'Time', u'Account Name', u'Account Type', u'Action'],
              [1, '3/2/2017', '09:53:26', u'Luke Zhao', 'Doctor', u'Login'],
              [2, '3/2/2017', '09:52:37', u'Luke Zhao', 'Patient', u'Login'],
              [3, '2/27/2017', '09:44:30', u'System Admin', 'Admin', u'Login'],
              [4, '2/27/2017', '09:24:10', u'Luke Zhao', 'Patient', u'Login']]
    title = 'Logins'

    create_admin_report(locale, header, result, title)
    create_admin_report_pdfkit(locale, header, result, title)

if __name__ == '__main__':
    main()
    exit()
