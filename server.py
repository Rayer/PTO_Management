import CalMain
import json
from db_access import sensitive_data
from db_access import member_access
import Configuration
from datetime import datetime
from datetime import timedelta
from pprint import pprint
from flask import Flask
from flask import request
from flask import Response
import requests
import _thread
import urllib.parse

from enum import Enum

app = Flask(__name__)
cal = CalMain.CalMain()

with sensitive_data() as sd:
    SLACK_TOKEN = sd.get('slack_api_token')

if SLACK_TOKEN is None:
    SLACK_TOKEN = Configuration.SLACK_API_TOKEN

acceptable_datetime_fmt = '%Y%m%d'
acceptable_datetime_fmt_alt = '%Y-%m-%d'


PTO_Form_Requirements = {
    'type': '1015037157',
    'innova_id': '2037176764',
    'chc_id': '1299006122',
    'name': '1823578907',
    'innova_email': '645853825',
    'chc_email': '1132405825',
    'dept': '1840028477',
    'start_m': '921047429_month',
    'start_d': '921047429_day',
    'start_y': '921047429_year',
    'start_hour': '1522291402',
    'end_m': '420978657_month',
    'end_d': '420978657_day',
    'end_y': '420978657_year',
    'end_hour': '1925858911'
}

innova_form_template = 'https://docs.google.com/forms/d/e/1FAIpQLSd64_uB_Is9bnw-2UExckHxQgKyZz-STTPh8EUiY2I6ELdrbw' \
                       '/viewform?'


def create_innova_prefill_form(info):
    ret = {}
    for key, value in PTO_Form_Requirements.items():
        data = info[key]
        ret.update({'entry.{}'.format(value): data})

    return innova_form_template + urllib.parse.urlencode(ret)


def create_inno_datasheet():
    return dict.fromkeys(PTO_Form_Requirements, '')


def get_user_profile(userid):
    profile = json.loads(
        requests.get('https://slack.com/api/users.info?token={0}&user={1}'.format(SLACK_TOKEN, userid)).content)
    return profile['user']['real_name']


def get_datetime_from_input(str_datetime):
    try:
        dt = datetime.strptime(str_datetime, acceptable_datetime_fmt)
    except:
        dt = datetime.strptime(str_datetime, acceptable_datetime_fmt_alt)

    return dt


@app.before_request
def before_request():
    # Log the request
    print('Incoming {0}'.format(request.method))
    if 'payload' in request.form:
        pprint(json.loads(request.form['payload']))
    else:
        pprint(request.form)


@app.route('/pto/slack/list', methods=['POST', 'GET'])
def pto_handle():
    return json.dumps(cal.get_incoming_dayoffs())


def attach_vacation_detail(type, name, start, end):
    return '{0}/{1}/{2}/{3}'.format(type, name, start, end)


@app.route('/pto/slack', methods=['POST'])
def handle_apply():
    date_list = request.form['text'].split(' ')
    user_id = request.form['user_id']
    user_name = get_user_profile(user_id)
    try:
        start = date_list.pop(0)
        end = date_list.pop(0) if date_list else start
        start_dt = get_datetime_from_input(start)  # Check start format
        end_dt = get_datetime_from_input(end)
        start = start_dt.strftime(acceptable_datetime_fmt_alt)
        end = end_dt.strftime(acceptable_datetime_fmt_alt)
    except:
        return 'Invalid date format, please at least provide start day!'

    ret_ui = {
        'text': 'Day-Off Application System -- Welcome {0}'.format(user_name),
        'attachments': [
            {
                'callback_id': 'pto_init',
                'actions': [
                    {
                        'name': 'vacation',
                        'type': 'button',
                        'text': 'Annual Paid Leave',
                        'value': attach_vacation_detail('Annual Paid Leave', user_name, start, end)
                    }, {
                        'name': 'vacation',
                        'type': 'button',
                        'text': 'Work From Home',
                        'value': attach_vacation_detail('Work From Home', user_name, start, end)
                    }, {
                        'name': 'vacation',
                        'type': 'button',
                        'text': 'Personal Leave',
                        'value': attach_vacation_detail('Personal Leave', user_name, start, end)
                    }, {
                        'name': 'vacation',
                        'type': 'button',
                        'text': 'Sick Leave',
                        'value': attach_vacation_detail('Sick Leave', user_name, start, end)
                    }
                ]
            }
        ]
    }
    return Response(json.dumps(ret_ui), mimetype='application/json')


@app.route('/pto/slack/cal', methods=['POST'])
def ret_cal_url():
    ret = {
        'text': 'Click this button to open PTO Calender',
        'attachments':
            [{
                'actions': [
                    {
                        "type": "button",
                        "text": "Open Calender",
                        "url": "https://calendar.google.com/calendar/embed?src=22opmonkdpao2o2grfgev4fvss%40group.calendar.google.com&ctz=Asia%2FTaipei"
                    }
                ]
            }]
    }

    return Response(json.dumps(ret), mimetype='application/json')


@app.route('/pto/slack/innova_form', methods=['POST'])
def ret_innova_form():
    ret = {
        'text': 'Click this button to open Innova PTO Form',
        'attachments':
            [{
                'actions': [
                    {
                        "type": "button",
                        "text": "Innova PTO Form",
                        "url": "https://docs.google.com/forms/d/e/1FAIpQLSd64_uB_Is9bnw-2UExckHxQgKyZz-STTPh8EUiY2I6ELdrbw/viewform#responses"
                    }
                ]
            }]
    }

    return Response(json.dumps(ret), mimetype='application/json')


@app.route('/pto/slack/apply', methods=['POST'])
def apply_pto():
    try:
        arguments = request.form['text'].split(' ')
        name = arguments.pop(0)
        description = arguments.pop(0)
        start = arguments.pop(0)
        end = start if not arguments else arguments.pop(0)
        end_dt = datetime.strptime(end, '%Y-%m-%d')
        start_dt = datetime.strptime(start, '%Y-%m-%d')
        end = end_dt.strftime('%Y-%m-%d')

        delta = end_dt - start_dt  # timedelta

        for i in range(delta.days + 1):
            print(end_dt + timedelta(days=i))

        cal.create_single_dayoff_event(name, start, description)
        message = 'PTO Applied - Name : {0}, desciption : {1}, start : {2}, end : {3}'.format(name, description, start,
                                                                                              end)
        print(message)
        return message
    except:
        return 'Invalid format, format should be : name description start(ex. 2011-12-01) end'


@app.route('/pto/slack/interactive', methods=['POST'])
def interactive():
    payload = json.loads(request.form['payload'])
    callback_id = payload['callback_id']
    if callback_id == 'pto_init':
        value_list = payload['actions'][0]['value'].split('/')
        v_type = value_list.pop(0)
        name = value_list.pop(0)
        start = value_list.pop(0)
        end = value_list.pop(0)

        _thread.start_new_thread(create_events_async, (name, start, end, v_type))

        m = member_access()
        employee = m.employee_info(name)
        info = create_inno_datasheet()
        info.update(employee)

        info['type'] = v_type;
        start_tok = start.split('-')
        info['start_m'] = start_tok[1]
        info['start_d'] = start_tok[2]
        info['start_y'] = start_tok[0]
        info['start_hour'] = '9'
        end_tok = end.split('-')
        info['end_m'] = end_tok[1]
        info['end_d'] = end_tok[2]
        info['end_y'] = end_tok[0]
        info['end_hour'] = '18'
        info['dept'] = 'MCDS'

        url = create_innova_prefill_form(info)

        ret = {
            'text': 'Successfully submitted vacation, {0}! Here is prefilled Innova PTO form : '.format(name),
            "attachments": [
                {
                    "fallback": "Your PTO is ready",
                    "actions": [
                        {
                            "type": "button",
                            "text": "Innova Vacation Form",
                            "url": url
                        }
                    ]
                }
            ]

        }

        return Response(json.dumps(ret), mimetype='application/json')

    return '....!!?'


def create_events_async(name, start, end, v_type):
    start_dt = datetime.strptime(start, acceptable_datetime_fmt_alt)
    end_dt = datetime.strptime(end, acceptable_datetime_fmt_alt)
    delta = end_dt - start_dt
    for i in range(delta.days + 1):
        day_dt = start_dt + timedelta(days=i)
        day = day_dt.strftime(acceptable_datetime_fmt_alt)
        if day_dt.isoweekday() in range(1, 6):
            print(day_dt)
            cal.create_single_dayoff_event(name, day, v_type)


@app.route('/pto/slack/interactive_load', methods=['POST'])
def interactive_load():
    return '.....!!!'


def main():
    app.run(host='0.0.0.0', port=1200)


if __name__ == '__main__':
    main()
