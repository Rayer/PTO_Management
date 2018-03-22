import CalMain
import json
from datetime import datetime
from datetime import timedelta
from pprint import pprint
from flask import Flask
from flask import request
from flask import Response
import requests

app = Flask(__name__)
cal = CalMain.CalMain()

token = 'xoxp-261545166194-262631279447-335103442198-5fb9e3a70bd2c7297ce259461c3be7a1'


def get_user_profile(userid):
    profile = json.loads(requests.get('https://slack.com/api/users.info?token={0}&user={1}'.format(token, userid)).content)
    return profile['user']['real_name']


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
    consume_fmt = '%Y-%m-%d'
    try:
        start = date_list.pop(0)
        end = date_list.pop(0) if date_list else start
        datetime.strptime(start, consume_fmt)  # Check start format
        end_dt = datetime.strptime(end, consume_fmt)
        end_dt += timedelta(days=1)
        end2 = end_dt.strftime(consume_fmt)
    except:
        return 'Invalid date format, please at least provide start day!'

    ret_ui = {
        'text': 'Day-Off Application System -- Welcome {0}'.format(user_name),
        'attachments': [
            {
                'callback_id': 'pto_init',
                'start': start,
                'end': end2,
                'name': user_name,
                'actions': [
                    {
                        'name': 'vacation',
                        'type': 'button',
                        'text': 'Paid Time Off(PTO)',
                        'value': attach_vacation_detail('Paid Time Off(PTO)', user_name, start, end2)
                    }, {
                        'name': 'vacation',
                        'type': 'button',
                        'text': 'Work From Home(WFH)',
                        'value': attach_vacation_detail('Work From Home(WFH)', user_name, start, end2)
                    }, {
                        'name': 'vacation',
                        'type': 'button',
                        'text': 'Personal Leave',
                        'value': attach_vacation_detail('Personal Leave', user_name, start, end2)
                    }, {
                        'name': 'vacation',
                        'type': 'button',
                        'text': 'Sick Leave',
                        'value': attach_vacation_detail('Sick Leave', user_name, start, end2)
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
        end_dt += timedelta(days=1)

        # In google cal, 2018-10-22 to 2018-10-24 means start from 10/22 end to 10/23 23:59:59
        end2 = end_dt.strftime('%Y-%m-%d')
        cal.create_dayoff_event(name, start, end2, description)
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
        type = value_list.pop(0)
        name = value_list.pop(0)
        start = value_list.pop(0)
        end = value_list.pop(0)
        cal.create_dayoff_event(name, start, end, type)

        ret = {
            'text': 'Successfully submitted vacation, {0}! Press button to open calendar'.format(name)
        }

        return Response(json.dumps(ret), mimetype='application/json')

    return '....!!?'


@app.route('/pto/slack/interactive_load', methods=['POST'])
def interactive_load():
    return '.....!!!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1200)
