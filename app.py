import json
import datetime
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from llm import get_completion


app = Flask(__name__)
# CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'
# cors = CORS(app, resources={r"/process": {"origins": "http://localhost:3001"}})
CORS(app, resources={r"/process": {"origins": "http://localhost:3001"}})


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def detect_text(path):
    '''
    Detects text in the image binary
    '''
    from google.cloud import vision

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)  # type: ignore
    texts = response.text_annotations

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )

    return texts[0].description


def parse_event(texts):
    '''
    Parse the text to get the event name, date, time, and location
    '''
    date_time = datetime.datetime.now()
    prompt = f'Current time is {date_time}. If there is no time specified, mark it as all-day event. For example, closing sale on 9/15-9/18 is an all-day event because there\'s not a specific time mentioned. Parse the poster texts and output json in the format:'
    format = '''
{
name: <name>,
all_day: <true/false>,
begin: <datetime in ISO 8601>,
end: <datetime in ISO 8601>,
location: <location>,
event_desc: <descriptions>
}'''
    print(prompt)
    response = get_completion(f'{texts}\n{prompt}\n{format}')
    return json.loads(response)


def create_ical(event):
    '''Create an ical file from the event'''
    from ics import Calendar, Event
    from dateutil import parser, tz
    import pytz
    print(event)
    cal = Calendar()
    e = Event()
    e.name = event['name']

    # Parse the strings into datetime objects and convert to UTC
    begin_local = parser.parse(event['begin']).astimezone(tz.tzlocal())
    end_local = parser.parse(event['end']).astimezone(tz.tzlocal())
    e.begin = begin_local.astimezone(pytz.UTC)
    e.end = end_local.astimezone(pytz.UTC)
    if event['all_day']:  # TODO probably need to parse string to get boolean?
        e.make_all_day()

    e.location = event['location']
    e.description = event['event_desc']

    cal.events.add(e)
    print(cal.events)
    with open('my.ics', 'w') as my_file:
        my_file.writelines(cal.serialize_iter())


@app.route("/process", methods=['POST'])
def process():
    path = request.form.get('path')
    texts = detect_text(path)
    event = parse_event(texts)
    create_ical(event)
    return _corsify_actual_response(jsonify({'response': 'OK'}))
    # if request.method == "OPTIONS":  # CORS preflight
    #     return _build_cors_preflight_response()
    # elif request.method == "POST":  # The actual request following the preflight
    #     # if 'file' not in request.files:
    #     #     return jsonify({'error': 'Bad Request'}), 400
    #     path = request.form.get('path')
    #     texts = detect_text(path)
    #     event = parse_event(texts)
    #     create_ical(event)
    #     return _corsify_actual_response(jsonify({'response': 'OK'}))
    # else:
    #     raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))

    # if 'file' not in request.files:
    #     return jsonify({'error': 'Bad Request'}), 400