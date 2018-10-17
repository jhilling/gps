#!/usr/bin/env python

from __future__ import print_function

from gps.lib.gpxUtil import interpolate_thres_lower_metres
from gps.lib.gpxUtil import interpolate_thres_upper_metres
from gps.lib.primitives.points import Point
from gps.lib.primitives.gpxBounds import Bounds
 
 
class Matcher(object):

    def __init__(self, logger, match_threshold_metres=70):
        self.log = logger
        self.match_threshold_metres = match_threshold_metres

    def prePoint(self, trackpoint, found):
        pass

    def foundPoint(self, trackpoint, found):

        pt_match, distance = found[0]

        if distance < self.match_threshold_metres:
            print(pt_match)
            self.log.o(pt_match)

    # TODO this cannot differentiate multiple passes over the same point (e.g. laps)
    def matchAlgo(self, specialOne, segments):  # segments might be our qtree

        bs = specialOne.getBounds()
        bt = segments.getBounds()

        if not bs.overlaps(bt):
            self.log.i("No overlap, skipping")
            return (0, 0, 0)

        hit = miss = 0
        waypoints = []

        # Walk through the match track looking for the nearest point in other the track
        for point in specialOne.points_virtual(interpolate_thres_lower_metres, interpolate_thres_upper_metres):

            # TODO Here, we may as well do a query on segments to get a list of ones that are candidates, 
            # rather than searching the entire world.

            pt, d = point.findNearest(segments)

#             if pt:
#                 self.foundPoint(point, pt, d)

            if not d is None and d < self.match_threshold_metres:
                hit += 1
##                waypoints.append(WayPoint(copyFrom=pt, name="hit %d" % hit, sym="Dot"))
            else:
                miss += 1
##                waypoints.append(WayPoint(copyFrom=pt, name="miss %d" % miss, sym="Anchor"))

##        self.gpx.writeItem(track)
##        for wp in waypoints:
##            self.gpx.writeItem(wp)

        match_pct = hit/float(hit+miss)*100

        return (hit, miss, match_pct)


    def matchAlgo2(self, specialOne, qtree):

        bs = specialOne.getBounds()

        TL = Point(lon=bs.leftObj.lon, lat=bs.topObj.lat)
        BR = Point(lon=bs.rightObj.lon, lat=bs.bottomObj.lat) 

        # Now shift the points by the threshold
        d = self.match_threshold_metres
        TL.move(-d, d)
        BR.move(d, -d)

        bs_ex = Bounds()
        bs_ex.registerPoint(TL);
        bs_ex.registerPoint(BR);

#        if not bs.overlaps(bt):
#            self.log.i("No overlap, skipping")
#            return (0, 0, 0)

        # Do a query on the qtree for all points in the range of the track
#        qtreeSub = qtree.queryRangeDebug(bs_ex)
        qtreeSub = qtree.queryRange(bs_ex)

        hit = miss = 0
        waypoints = []

        # Walk through the match track looking for the nearest point in other the track
        for point in specialOne.points_virtual(interpolate_thres_lower_metres, interpolate_thres_upper_metres):

            # min is the nearest waypoint, but may be be way of range
            min, found = point.findNearest4(qtreeSub)

            self.prePoint(point, found or min)

            d, wp = (None, None)

            # Make sure the point really is in range before calling foundPoint.
            # findNearest4 will always return something even if it is miles away
            if found:
                self.foundPoint(point, found)
                d, wp = found[0]

            if d and d < self.match_threshold_metres:
                hit += 1
##                waypoints.append(WayPoint(copyFrom=pt, name="hit %d" % hit, sym="Dot"))
            else:
                miss += 1
##                waypoints.append(WayPoint(copyFrom=pt, name="miss %d" % miss, sym="Anchor"))

##        self.gpx.writeItem(track)
##        for wp in waypoints:
##            self.gpx.writeItem(wp)

        match_pct = hit/float(hit+miss)*100

        return (hit, miss, match_pct)
    
if __name__ == "__main__":
    import sys
    print("%s: I don't do anything standalone" % sys.argv[0])
