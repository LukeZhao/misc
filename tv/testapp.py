from manage import app
from video_twilio import new_twilio_video_tokens

from flask import (Blueprint, request, jsonify, json)
import random
from settings import get_logger
from connections import (LocalProxy, default_api_key,
                         switch_customer,
                         redis_connection, current_customer)
rds = redis_connection
api_nv1 = Blueprint('api_nv1', __name__, url_prefix='/tv')
log = get_logger('api')

@api_nv1.route('/tokens', methods=['GET'])
def get_tokens():
    log.info('get_tokens called')
    switch_customer('tcs')
    session = request.args.get('session', 0)
    response = None
    if int(session) != 0:
        response = rds.get(str(session))
    if response:
        return response, 200
    rand = random.Random()
    session = rand.randint(1, 1000)
    while rds.get(str(session)):
        session = rand.randint(1, 1000)
    log.info('session = [{}]'.format(session))
    toks = new_twilio_video_tokens()
    response = ('{"session": "' + str(session) + '",' +
                '"patient_id": "' + toks.get('twilio_video_id_patient', '') + '",' +
                '"patient_token": "' + toks.get('twilio_video_token_patient', '') + '",' +
                '"clinician_id": "' + toks.get('twilio_video_id_clinician', '') + '",' +
                '"clinician_token": "' + toks.get('twilio_video_token_clinician', '') + '"}')
    rds.set(str(session), response)
    rds.expire(str(session), 7200)
    log.info('response = {}'.format(response))
    return jsonify(json.loads(response)), 200

@api_nv1.route('/strip', methods=['POST'])
def get_strip():
    import re
    data1 = request.get_json()
    data = data1.get('val', 'no value')
    log.info('AAAAA type = {}'.format(type(data)))
    log.debug(u'AAAAAA: {}'.format(data).encode('utf8'))
    _reg_non_alpha = re.compile('[\W_]', re.UNICODE)
    str = data
    ret = _reg_non_alpha.sub('', str)
    log.info(u'AAAAA ret = {}'.format(ret).encode('utf8'))
    return jsonify({'ret': ret}), 200

app.register_blueprint(api_nv1, subdomain=app.config['API_SUBDOMAIN'])

