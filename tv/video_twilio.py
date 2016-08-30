# Copyright (C) 2016 Comtech TCS. All rights reserved.
#
# The information contained herein is confidential and proprietary to
# Comtech TCS and is considered a trade secret as
# defined in section 499C of the California Penal Code. Use of this
# information by anyone other than authorized employees of
# Comtech TCS is granted only under a written non-disclosure agreement
# expressly prescribing the scope and manner of such use.
#

import os
from uuid import uuid4
from twilio.access_token import AccessToken, ConversationsGrant
from settings import live_config

def new_twilio_video_tokens():

    # get credentials from config
    account_sid = 'AC6fbff77992d10662d2d14d9facc494c3' # live_config('TWILIO_ACCOUNT_SID')
    api_key = 'SK66c0077df076e009565295cd006c0925' #live_config('TWILIO_API_KEY')
    api_secret = '73w1nYUgPH0sI2KZtgp7qFlSGDGjgn8n' #live_config('TWILIO_API_SECRET')
    profile_id = 'VSace2c5699219999e4edfcd4b94d7be85' #live_config('TWILIO_CONFIGURATION_SID')
    id_patient = str(uuid4())
    id_clinician = str(uuid4())

    # Create an Access Tokens
    token_patient = AccessToken(account_sid, api_key, api_secret)
    token_patient.identity = id_patient
    token_clinician = AccessToken(account_sid, api_key, api_secret)
    token_clinician.identity = id_clinician

    # Grant access to Conversations
    grant = ConversationsGrant()
    grant.configuration_profile_sid = profile_id
    token_patient.add_grant(grant)
    token_clinician.add_grant(grant)

    # Return token info
    # we will use the same fields as opentok assuming we will have
    # only one video provider for a given consult.
    return {
        # patient will make the connection so we only keep the clinician id.
        'twilio_video_id_clinician': token_clinician.identity,
        'twilio_video_token_clinician': token_clinician.to_jwt(),
        'twilio_video_id_patient':  token_patient.identity,
        'twilio_video_token_patient': token_patient.to_jwt(),
        'video_provider': 'twilio',
    }
