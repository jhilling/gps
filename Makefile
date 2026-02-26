
# See also gpxdocker.sh for controller docker containers

clean:
	@echo "Nothing to clean"

init:
	pip3 install -r requirements.txt

test:
	python3 -m unittest discover -v
	python3 gps/gpx2txt.py -- "sample-data/trk 2018-09-05 18-04-59-1 - ACTIVE LOG.GPX"

docker:
	docker build --no-cache --tag gps-server:latest .

.PHONY: init test
