#!/usr/bin/env python

from __future__ import print_function

import sys
import os

from gps.lib.gpsObserver import GpxObserver
from gps.lib.formats.GpxParser import GpxParser
from gps.lib.gpxQTree import SegmentsQTree
from gps.lib.primitives.gpxBounds import Bounds
from gps.lib.primitives.points import Point
from gps.lib.logWriter import LogWriter
from gpxWaypointDB import WaypointDB

log = LogWriter()


class WayPointGatherer(GpxObserver):
    """
    As waypoints are found parsing the gpx files, add them to an internal qtree
    """

    def __init__(self):
        super(WayPointGatherer, self).__init__()

        # Note if we used smaller bounds we would automatically exclude points for countries miles away
        # TODO OPT read the tracks first, work out the (extended) bounds and use for these bounds   
        bounds = Bounds()
        bounds.registerPoint(Point(-90, -90))
        bounds.registerPoint(Point(90, 90))

        # Use a quad tree to store the points
        self.qtree = SegmentsQTree(bounds, 1000)

        self.distanceThreshold = 300

    def Parse(self, filename, dthres):
        self.distanceThreshold = dthres
        GpxParser(self).Parse([filename])

    # Overriding this allows you to write filtered subclasses
    def allowWayPoint(self, wayPoint):
        return True

    def nextWayPoint(self, wayPoint):
        super(WayPointGatherer, self).nextWayPoint(wayPoint)
        
        if self.allowWayPoint(wayPoint):
            # Add this to the waypoint
            wayPoint.distanceThreshold = self.distanceThreshold        
            self.qtree.addPoint(wayPoint)

    def __str__(self):
        return self.qtree.__str__()


# TODO yet another cl parser here. see if gpxCommandLine can't do this?
def getFilenameFromCL(argv):
    wpFiles = []
    wpFilesStat = []
    needOptValue = optValue = None
    dthres = 300

    for f in argv:
        if f in ['-d',]:
            if needOptValue:
                print("Need opt for", needOptValue, "but got", f)
                sys.exit(1)
            else:
                needOptValue = f
        elif needOptValue:
            optValue = f

            # deal with that OPT/VALUE pair
            if needOptValue == "-d":
                log.i("Setting distance threshold to %s" % f)
                dthres = int(optValue)
                if dthres > max_match_threshold_metres:
                    max_match_threshold_metres = dthres
            else:
                print("didn't do anything with that")
                sys.exit(1)

            needOptValue = optValue = None
        else:
            statThis = os.stat(f)
            for have in wpFilesStat:
                if have == statThis:
                    log.i("Ignoring duplicate specification of: %s" % f)
                    break
            else:
                wpFilesStat.append(statThis)
                wpFiles.append( (f, dthres) )

    return wpFiles


# TODO add as a method to bounds
#DUP
def printBounds(bounds):
    log.i("These are the extremities:")
    log.i("L: %s" % bounds.left())
    log.i("R: %s" % bounds.right())
    log.i("T: %s" % bounds.top())
    log.i("B: %s" % bounds.bottom())
    log.i("")


if __name__ == "__main__":

    wpg = WayPointGatherer()

    wpFiles = getFilenameFromCL(sys.argv[1:])

    if not wpFiles:
        wpFiles = list(WaypointDB().get())


    log.dbg("Waypoint files are: %s" % wpFiles)

    for filename, dthres in wpFiles:
        wpg.Parse(filename, dthres)

    # For interest, these are the extreme points
    bounds = wpg.qtree.getBounds()

    printBounds(bounds)
    log.i("%s" % wpg)
