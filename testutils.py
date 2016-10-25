# Copyright (C) 2015-2016 TeleCommunications Systems, Inc. All rights reserved.
#
# The information contained herein is confidential and proprietary to
# Networks In Motion, Inc., and is considered a trade secret as
# defined in section 499C of the California Penal Code. Use of this
# information by anyone other than authorized employees of Networks
# In Motion is granted only under a written non-disclosure agreement
# expressly prescribing the scope and manner of such use.
#

import re
import arrow
import json
from phonenumbers import (parse, is_valid_number, region_code_for_country_code,
                          format_number, PhoneNumberFormat as PNF)
from flask import url_for, jsonify
from settings import live_config
import datetime
from mongoengine import ValidationError

reg_mdy = re.compile('(1[0-2]|0?[1-9])/(0?[1-9]|[12][0-9]|3[01])/[12]\d{3}')
reg_dmy = re.compile('(0?[1-9]|[12][0-9]|3[01])/(1[0-2]|0?[1-9])/[12]\d{3}')
reg_date = {'M/D/YYYY': reg_mdy, 'D/M/YYYY': reg_dmy}
holiday_id = '000000000000000000000000'

def get_time(d=7):
    aa = arrow.get().replace(days=d).timestamp
    bb = arrow.get().replace(days=d, minutes=30).timestamp
    return {'start': aa, 'end': bb}
    
