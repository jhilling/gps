#!/usr/bin/env python3

from __future__ import print_function

from gps.lib.gpxWaypointGatherer import WayPointGatherer
from gps.lib.primitives.gpxBounds import Bounds
from gps.lib.gpsObserver import GpxObserverPrint
from gps.lib.primitives.points import Point
from gps.lib.formats.gpxWriter import gpxWriter
from gps.lib.logWriter import LogWriter

import sys
import os

log = LogWriter()


class gpxFilter(GpxObserverPrint):
    """
    Filter out waypoints that are very near those already
    in the passed in qtree
    """

    def __init__(self, qtree, distanceThreshold=50):
        super(gpxFilter, self).__init__()
        self.qtree = qtree
        self.distanceThreshold = distanceThreshold
        self.gpx = None

    def start(self):
        self.gpx = gpxWriter()

    def nextTrack(self, track):
        super(gpxFilter, self).nextTrack(track)
        self.gpx.writeItem(track)

    def nextWayPoint(self, point):
        super(gpxFilter, self).nextWayPoint(point)

        # Similar code lifted from gpxMatcher/matchAlgo2. Maybe a method can be provided to help with this.
        TL = Point(copyFrom=point)
        BR = Point(copyFrom=point)

        d = self.distanceThreshold / 2
        BR.move(d, -d)
        TL.move(-d, d)
    
        bounds = Bounds()
        bounds.registerPoint(TL);
        bounds.registerPoint(BR);
        
        near_points = self.qtree.queryRange(bounds)

        # are found and near points going to be the same?
        found = point.findNearest3(near_points)

        if not found or not found[0]:
            # Add ourselves to the qtree meaning subsequent points
            # might get filtered out by this one
            point.distanceThreshold = self.distanceThreshold
            self.qtree.addPoint(point)

            self.gpx.writeItem(point)
        else:
            # TODO may want to apply some sort of policy to which one is dropped
            log.i("Filtered this one out: %s" % point)  
            log.i("as near: %s" % found[0])
            log.i("distance: %s" % found[1])

    def nextRoute(self, route):
        super(gpxFilter, self).nextRoute(route)
        self.gpx.writeItem(route)

    def nextRoutePoint(self, routePoint):
        pass

    def nextTrackPoint(self, trackPoint):
        pass

    def end(self):
        self.gpx.close()


def parseCL():
    # TODO yet more CL parsing code

    wpFilters = []
    wpFiltersStat = []
    inputFiles = []

    dthres = 50
    max_match_threshold_metres = dthres
    needOptValue = optValue = None
    onInputFiles = False

    for f in sys.argv[1:]:

        if f in ['-d']:
            if needOptValue:
                print("Need opt for", needOptValue, "but got", f)
                sys.exit(1)
            else:
                needOptValue = f
        elif f in ['--',]:
            onInputFiles = True
        elif needOptValue:
            optValue = f

            # deal with that OPT/VALUE pair
            if needOptValue == "-d":
#                log.i("Setting distance threshold to %s" % f)
                dthres = int(optValue)
                if dthres > max_match_threshold_metres:
                    max_match_threshold_metres = dthres
            elif needOptValue == '-o':
                outputFormat = optValue
            else:
                print("didn't do anything with that")
                sys.exit(1)

            needOptValue = optValue = None

        elif onInputFiles:
            inputFiles.append(f)
        else:
            statThis = os.stat(f)
            for have in wpFiltersStat:
                if have == statThis:
#                    log.i("Ignoring duplicate specification of: %s" % f)
                    break
            else:
                wpFiltersStat.append(statThis)
                wpFilters.append( (f, dthres) )

    if not wpFilters:
        print("Have no filter files")
        sys.exit(1)

    if not inputFiles:
        print("Have no input files")
        sys.exit(1)

    return wpFilters, inputFiles


if __name__ == "__main__":

    # Separate the files which are used for waypoints and tracks with a --

    wpFilters, inputFiles = parseCL()

    # First gather up the fb waypoints into qtree
    fb = WayPointGatherer() 

    for f, d in wpFilters:
        fb.Parse(f, d)

    # Add those waypoints here
    filter = gpxFilter(fb.qtree)

    # Now process more gpx. Any waypoints that appear that are near
    # ones already loaded will be filtered out
    filter.Parse(inputFiles)


