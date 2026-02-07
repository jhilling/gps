#!/usr/bin/env python3

"""

Thin veneer to handle the rest call and pass down to gpxRest.py
which does the real work

Aim is to be able to get|post a gpx file and it will return the
gpx2txt text for it.

get on /gpx/ with a file attached in the message body

Example curl command:

curl -X GET -H "accept: text" -H "Content-Type: application/xml" --data "@./trk 2018-09-05 18-04-59-1 - ACTIVE LOG.GPX" "http://0.0.0.0:5000/text"


"""

import pathhack

import sys

from io import StringIO

import werkzeug
from flask import Flask
from flask import request

from gps.lib.gpxRest import GpxRest

from gps.lib.logWriter import LogWriter


app = Flask(__name__)


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/waypoints')
def waypoints():

    # For interest, these are the extreme points
    bounds = gpx.wpg.qtree.getBounds()

    s = "L: %s" % bounds.left()
    s += "R: %s" % bounds.right()
    s += "T: %s" % bounds.top()
    s += "B: %s" % bounds.bottom()

    # ss = "%s" % gpx.wpg

    return s


class MyStringIO(StringIO):
    def __str__(self):
        return ""


def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']


def requested_format():
    if request_wants_json():
        return "json"
    return "text"


@app.route('/text')
def text():
    """
    """
    files = []

    #files.append("/home/james/GPS_Tracks/Repository/tracks/2018/trk 2018-09-05 18-04-59-1 - ACTIVE LOG.GPX")

    if not request.data:
        raise werkzeug.exceptions.BadRequest(description="Request contained no data", response=None) # 400

    files.append(MyStringIO(request.data))

    return gpx.handler(files, requested_format())


if __name__ == '__main__':
    log = LogWriter()
    gpx = GpxRest()

    is_debug = "--run" not in sys.argv

    if is_debug:
        # Accept local connection only
        listen_host = '127.0.0.1'
    else:
        # Accept any connection
        listen_host='0.0.0.0'

    app.run(debug=is_debug, host=listen_host)


