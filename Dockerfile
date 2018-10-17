FROM python:2.7
MAINTAINER James Hilling

ENV GPS_HOME /root/gps
RUN mkdir "$GPS_HOME"

WORKDIR "${GPS_HOME}"

VOLUME ["/root/GPS_Tracks"]

# Note that changing requirements will(may) required a clean build to be picked up
COPY requirements.txt ${GPS_HOME}

RUN pip install -r ${GPS_HOME}/requirements.txt

COPY gps/ ${GPS_HOME}

ENV GPS_PORT 5000
EXPOSE ${GPS_PORT}

CMD ./gpxRestFlask.py --run

