import CalMain
import json
from datetime import datetime
from datetime import timedelta
from pprint import pprint
from flask import Flask
from flask import request
from flask import Response
app = Flask(__name__)
cal = CalMain.CalMain()


@app.before_request
def before_request():
    # Log the request
    print('Incoming {0}'.format(request.method))
    pprint(request.form)


@app.route('/pto/slack', methods=['POST', 'GET'])
def pto_handle():
    return json.dumps(cal.get_incoming_dayoffs())


@app.route('/pto/slack/list', methods=['POST'])
def handle_list():
    name = request.form['text']
    ret = cal.get_incoming_dayoffs()
    return json.dumps(ret)


@app.route('/pto/slack/cal', methods=['POST'])
def ret_cal_url():
    ret = {
        'text': 'Click this link to open PTO Calender',
        'attachments':
            [{
                'text': 'https://calendar.google.com/calendar/embed?src=22opmonkdpao2o2grfgev4fvss%40group.calendar'
                        '.google.com&ctz=Asia%2FTaipei '
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
        message = 'PTO Applied - Name : {0}, desciption : {1}, start : {2}, end : {3}'.format(name, description, start, end)
        print(message)
        return message
    except:
        return 'Invalid format, format should be : name description start(ex. 2011-12-01) end'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1200)