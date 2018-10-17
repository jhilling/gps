#!/usr/bin/env python

"""
Convert data from the world cities db to waypoints in gpx format.
"""

# 32 seconds to read/write the file

from __future__ import print_function

import pathhack

import sys
from gps.lib.primitives.points import WayPoint
from gps.lib.formats.gpxWriter import gpxWriter
from gps.lib.primitives.gpxSegments import Segments


class WorldCitiesEntry(object):
    def __init__(self, country, city, accentcity, region, population, latitude, longitude):
        self.country = country
        self.city = city
        self.accentcity = accentcity
        self.region = region
        self.population = population
        self.latitude = float(latitude)
        self.longitude = float(longitude)

    def asTuple(self):
        return (self.country,
                self.city,
                self.accentcity,
                self.region,
                self.population,
                self.latitude,
                self.longitude)

    def __str__(self):
        return "%s:%s:%s:%s:%s:%f:%f" % self.asTuple() 


def parseLine(line):
    fields = line.split(",")
#     print(fields)
    
    try:
        wc = WorldCitiesEntry(*fields)
    except ValueError:
        print("ERROR: converting", line, file=sys.stderr)
        wc = None

    return wc 


def doOne(gpx, input):

    segments = Segments()

    lastWC = None
    for raw in input:
        wc = parseLine(raw.strip())
        if wc:
            # Turn this into a Waypoint
            wp = WayPoint(wc.latitude, wc.longitude, copyFrom=None, name="%s, %s" % (wc.city, wc.country), sym=None)

            gpx.writeItem(wp)

            startSeg = (not lastWC or wc.country != lastWC.country)

            segments.addPoint(wp, startSeg)

            lastWC = wc

    return segments

if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        f =  """ad,aixas,Aix,06,,42.4833333,1.4666667
ad,aixirivali,Aixirivali,06,,42.4666667,1.5
ad,aixirivall,Aixirivall,06,,42.4666667,1.5""".splitlines()
    else:
        f = sys.stdin

    gpx = gpxWriter()

    segments = doOne(gpx, f)

    # For interest, these are the extreme points
#     bounds = segments.getBounds()
#     gpx.writeItem(bounds.left())
#     gpx.writeItem(bounds.right())
#     gpx.writeItem(bounds.top())
#     gpx.writeItem(bounds.bottom())

    gpx.close()

    print(segments, file=sys.stderr)


