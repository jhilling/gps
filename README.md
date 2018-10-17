
# James Hilling's GPS/GPX data project

*This file is in markdown format and is best viewed in something that can render it nicely.* 

Tested with Python 2.7.15rc1 on Ubuntu 18.04

Under the test directory is unit test file for each script. See gentests.sh for generating
a placeholder unit test for any new python scripts.  Many of the tests under here are 
still placeholders, I'm working on converting to useful tests!

They can be run with `make test` or `python -m unittest discover -v`

# The scripts
Various scripts for manipulating GPS data in GPX file (see sample-data).

##gpx2txt.py

This script will "describe" a gps route in plain text, describing various 
landmarks passed with the time/distance.  It also calls out any stops en-route and where they were near.  
It automatically pull down landmarks from openstreetmap and caches the data locally.

For example:
 ```
 gps/gpx2txt.py -- "sample-data/trk 2018-09-05 18-04-59-1 - ACTIVE LOG.GPX"
 ```

*Note the leading -- in the command line.   Any files supplied before the -- are treated as 
custom waypoint input files.   If we don't supply any waypoint file then the defaults are used.*

Sample output for the above:

```
Track: trk 2018-09-05 19-11-17-0 - ACTIVE LOG.GPX
Fetching POI
Track bounds are: B:51.375837224 L:-0.987403365	T:51.475270400 R:-0.863137376
Track bounded area is: 152.8 square kms (13.8 kms x 11.1 kms)
TRACK: trk 2018-09-05 19-11-17-0 - ACTIVE LOG.GPX|ACTIVE LOG
Wed Sep  5 19:11:17 2018	0.0 km|0.0 mi	Track start
Wed Sep  5 19:11:17 2018	0.0 km|0.0 mi	Charvil
Wed Sep  5 19:27:06 2018	5.5 km|3.4 mi	Horseshoe Bridge
Wed Sep  5 19:35:36 2018	8.0 km|5.0 mi	Fountain
Wed Sep  5 19:36:01 2018	8.2 km|5.1 mi	6.1 minutes STOPPED at Fountain 
Wed Sep  5 19:49:55 2018	9.9 km|6.1 mi	The Alehouse
Wed Sep  5 19:51:23 2018	10.2 km|6.3 mi	Oracle, The
Wed Sep  5 21:34:05 2018	36.7 km|22.8 mi	The Wheelwright's Arms
Wed Sep  5 21:35:01 2018	36.9 km|22.9 mi	115.7 minutes STOPPED at The Wheelwright's Arms 
Wed Sep  5 23:38:10 2018	39.2 km|24.3 mi	Bader
Wed Sep  5 23:39:35 2018	39.5 km|24.6 mi	Sandford lane
Wed Sep  5 23:47:56 2018	42.2 km|26.2 mi	Charvil/EPFD
Wed Sep  5 23:48:14 2018	42.3 km|26.3 mi	Charvil/EPFD/Home
Wed Sep  5 23:48:46 2018	42.4 km|26.4 mi	Charvil/EPFD
Wed Sep  5 23:49:02 2018	42.5 km|26.4 mi	Charvil
Wed Sep  5 23:50:23 2018	42.9 km|26.7 mi	Charvil/Alpars Kebab Van
Wed Sep  5 23:50:23 2018	43.0 km|26.7 mi	7.0 minutes STOPPED at Alpars Kebab Van 
Wed Sep  5 23:58:16 2018	43.3 km|26.9 mi	Charvil
Wed Sep  5 23:58:29 2018	43.3 km|26.9 mi	Track stop
Trackpoints hit 77, missed 1005 (7.1% waypoint hit rate)
Moving time 40.5% - 116.2 minutes out of 171.0 minutes
81 stops over 43.3 km|26.9 mi
```

##gpxRestFlask.py

gpx2txt functionality can optionally be run as a webserver and process requests via REST using gpxRestFlask.py.

Additionally the server can be run in docker, and multiple servers can be scaled up 
and down using docker swarm with a haproxy load balancer on the front.

This provides the ability to handle many requests in a dynamically scalable way.   

To start a simple webserver directly on the host run `gps/gpxRestFlask.py`
and send gpx files to it for example like this:

```curl -X GET -H "accept: text" -H "Content-Type: application/xml" --data "@sample-data/trk 2018-09-05 18-04-59-1 - ACTIVE LOG.GPX" "http://0.0.0.0:5000/text"```

This will produce the same output as the example given for gpx2txt.py
but we used a server to handle the request rather than a one-shot process.

See gpsserver.sh.

##gpsserver.sh

gpsserver.sh provides some abstractions to setup and control the server with docker.

Ensure the docker image is built (only need to do this once)
```
./gpsserver.sh build
``` 

###Individual server
Start a server
```
./gpsserver.sh start
```

Determine available ports for the server:
```
./gpsserver.sh port
```

Submit a test curl request to the server. NNN is the port (from above command) to send the server to:
```
./gpsserver.sh curl NNN
```

Stop all servers
```
./gpsserver.sh stop
```

###Swarm of servers

Initialize a swarm called hello.  Will standup several server instances and a load balancer on port 80.
```
./gpsserver.sh swarm hello
```

See the servers running:
```
./gpsserver.sh status
```

Make a request to the load-balancer, and have the request serviced by a member of the swarm.
```
./gpsserver.sh curl 80
```

Re-scale the swarm to 3 workers. 
```
./gpsserver.sh swarm-scale hello 3
```


##tools/gpxSplitter.gpx

This utility will split a gpx tracks into smaller gpx files.

Splits an individual track when large time or distance gap is found between trackpoints.


##tools/...

There are various other little gpx utility scripts under gps/tools. One day they will be documented here.


# Dependencies

Please see requirements.txt for the list of dependencies.

Run:

`pip install -r requirements.txt` 

or 

`make init`

to automatically install them.
