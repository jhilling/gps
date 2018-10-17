
# See also gpxdocker.sh for controller docker containers

clean:
	@echo "Nothing to clean"

init:
	pip install -r requirements.txt

test:
	python -m unittest discover -v
	python gps/gpx2txt.py -- "sample-data/trk 2018-09-05 18-04-59-1 - ACTIVE LOG.GPX"

docker:
	docker build --no-cache --tag gps-server:latest .

.PHONY: init test
