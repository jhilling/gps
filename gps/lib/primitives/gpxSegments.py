#!/usr/bin/env python

from __future__ import print_function
from gps.lib.primitives.gpxBounds import Bounds
from gps.lib.primitives.points import Point
from gps.lib.gpxXml import Xml
from gps.lib.logWriter import LogWriter
import gps.lib.gpxUtil
import os


jxml = Xml()

log = LogWriter()

###############################################################################


class Segment(object):

    """A segment holds an unordered bunch of points"""

    def __init__(self):
        self.points = []
        self.bounds = Bounds()

    def addPoint(self, point):

        if point is None:
            return

        self.points.append(point)
        self.bounds.registerPoint(point)

    def __iter__(self):
        for point in self.points:
            yield point

    def count(self):
        return len(self.points)

    def __str__(self):
        return "%d points, %s" % (self.count(), self.bounds)

###############################################################################


# Maybe this should ensure that trackpoints are stored in chronalogical order?
class TrackSegment(Segment):

    def __init__(self):
        super(TrackSegment, self).__init__()

    def gpxType(self):
        return "trkseg"

    def gpx(self):
        s = jxml.ele(self.gpxType(), None, None, False) + "\n"
        for tp in self.points:
            s += tp.gpx() + "\n"
        s += jxml.ee(self.gpxType()) + "\n"
        return s

    def pointsInterpolated(self, lower_limit, upper_limit):

        if not self.points:
            return

        if len(self.points) < 2:
            self.points[0].type = "real"
            yield self.points[0]
        else:
            last = None
            i = 0
            for point in self.points:
                if last:
                    for p_inter in last.interpolate(point, lower_limit, upper_limit, include_self=(i==0)):
                        yield p_inter
                    i += 1
                last = point

###############################################################################


# This assumes no ordering with respect to the points it holds.
# TODO we could add a qtree alongside this

class Segments(object):
    """Hold a bunch of segments and aggregate values"""

    def __init__(self, maxPoints=None):
        self.point_count = 0
        self.name = None
        self.segments = []
        self.currentSegment = None

        self.elevation_min = None
        self.elevation_max = 0
        
        self.log = LogWriter()

        self.maxPoints = maxPoints

    def newSegment(self):
        return Segment()
    
    def startSegment(self):
        self.currentSegment = self.newSegment()
        self.segments.append(self.currentSegment)

    def endSegment(self):
        # not guarenteed to be called
        #self.bounds.registerBounds(self.currentSegment.bounds)
        self.currentSegment = None
        
    def getBounds(self):
        bounds = Bounds()
        for segment in self.segments:
            bounds.registerBounds(segment.bounds)
        return bounds
    
    def addPoint(self, point, startSegment=False):
        if point is None:
            return None

        if self.currentSegment is None or startSegment or \
           self.maxPoints and self.currentSegment.count() > self.maxPoints:
            self.startSegment()
        
        self.point_count += 1
        
        self.currentSegment.addPoint(point)

        return point 

    def countSegments(self):
        """return the number of segments"""
        return len(self.segments)

    def countPoints(self):
        """return the total number of points"""
        count = 0
        for segment in self.segments:
            count += segment.count()
        # TODO james.. you have point_count you know

        return count

    def firstPoint(self):
        """Slightly fiddly because we can have empty segments"""
        for segment in self.segments:
            if segment.points:
                return segment.points[0] 
        return None

    def lastPoint(self):
        for segment in reversed(self.segments):
            if segment.points:
                return segment.points[-1] 
        return None

    def __iter__(self):
        for segment in self.segments:
            yield segment

    def points(self):
        for segment in self.segments:
            for point in segment:
                yield point

    def __str__(self):
        s = "%d segments, %d points, bounds: %s " % (self.countSegments(), self.countPoints(), self.getBounds()) 
        return s

###############################################################################


class TrackSegments(Segments):
    """
    Hold a bunch of segments and aggregate values. 
    Assumes ordering in the points, unlike the base class which
    assumes a random collection of points
    """

    def __init__(self):
        super(TrackSegments, self).__init__()

        self.elevation_gain = self.elevation_loss = 0
        self.time_first = self.time_last = None
        self.distance = 0
        self.last_tp = None
        #self.bounds = Bounds()

    def newSegment(self):
        return TrackSegment()
    
    def addPoint(self, pointp, startSegment=False):

        point = super(TrackSegments, self).addPoint(pointp, startSegment)

        if point is None:
            return

        if self.last_tp:

            self.distance += point.setDistance(self.last_tp)

            # Simplistic/naive calculation of height loss/gain
            if point.elevation and self.last_tp.elevation:
                new_elevation = point.elevation
                old_elevation = self.last_tp.elevation

                if new_elevation > old_elevation:
                    self.elevation_gain += (new_elevation - old_elevation)
                else:
                    self.elevation_loss += (old_elevation - new_elevation)

            s = point.setSpeed(self.last_tp)

        else:
            point.d = 0

        if point.time_obj is None:
            pass
        elif self.time_first is None:
            self.time_first = self.time_last = point.time_obj
        else:
            if point.time_obj < self.time_first:
                # this is a bit rash. I have seen tracks where the times
                # are all over the place in terms of order. use a time or
                # distance threshold to determine a split in the track

                # I have seen a track have multiple blocks, not necessarily
                # in chronological order. this probably means we need to split the track                
                self.log.i("WARNING:TRACKPOINTS OUT OF ORDER, case a %s %s" % (point, self.time_first))
                #return False
                self.time_first = point.time_obj
                
            elif point.time_obj > self.time_last:
                # this usually gets updated on each TP, as the TPS progress in time
                self.time_last = point.time_obj
            else:
                # somewhere between the two extremes of times
                # if we have jumped back we may get a lot of these, so check the last
                # value and if it's less than that, print

                if point.time_d(self.last_tp) < 0:
                    self.log.i("WARNING:TRACKPOINTS OUT OF ORDER, case b %s %s" % (point, self.time_last))

        if not point.elevation is None: 
            if (self.elevation_min is None or point.elevation < self.elevation_min):
                self.elevation_min = point.elevation
            if point.elevation > self.elevation_max:
                self.elevation_max = point.elevation

        self.last_tp = point

        if point.cad or point.hr:
            self.hasExtensions = True

    def checkTime(self, trackpoint, split_track_threshold_secs):
        if self.last_tp and trackpoint.time_obj and self.last_tp.time_obj:

            seconds = trackpoint.time_d(self.last_tp)

            if abs(seconds) > split_track_threshold_secs:
                self.log.i("Large time gap found between waypoints: %d hours" %  (seconds / (60*60)))
                #self.log.i("LTP %s, %s" % (self.last_tp, self.last_tp.time_obj))
                #self.log.i("TP %s, %s" % (trackpoint, trackpoint.time_obj))

                return False

        return True

    def checkDistance(self, trackpoint, dist_thres_metres):
        if self.last_tp:
            d_m = trackpoint.distance(self.last_tp)
            if d_m > dist_thres_metres:
                self.log.i("Large distance found between waypoints: %d metres" % d_m)
                return False

        return True

    def split(self, time_gap_thres_seconds, dist_gap_thres_metres):
        """split the track when there are gaps larger than the threshold..
        Returns a list of tracks"""

        tracks_return = []
        newTrack = None

        # Loop, check gaps, create new Track object, and add to return list
        for segment in self.segments:
            if newTrack is None:
                newTrack = self.newOneOfMe()

            newTrack.startSegment()

            for tp in segment.points:
                if not newTrack.checkTime(tp, time_gap_thres_seconds): # or not newTrack.checkDistance(tp, dist_gap_thres_metres):
                    newTrack.endSegment()
                    tracks_return.append(newTrack)
                    newTrack = self.newOneOfMe()
                    newTrack.name = self.name

                newTrack.addPoint(tp)

        if newTrack is None:
            newTrack = self.newOneOfMe()
        else:
            newTrack.endSegment()

        tracks_return.append(newTrack)

        return tracks_return

    def duration(self):
        """Return duration in seconds"""
    
        if self.time_last and  self.time_first:
            td = self.time_last - self.time_first
            return td.total_seconds()

        return 0

    def PrintStats(self, writef=print):

        # Aggregate the bounds of each segment
        bounds = self.getBounds()

        if self.time_first:
            writef("Time first : %s" % (self.time_first))
            writef("Time last  : %s" % (self.time_last))
            # duration?
            writef("Duration   : %s" % (self.time_last - self.time_first))


        # Some of these might be None if we didn't read any elevations
        if self.elevation_min and self.elevation_max and self.elevation_gain and self.elevation_loss:
            writef("Elevation min  : %s" % gps.lib.gpxUtil.elevation(self.elevation_min))
            writef("Elevation max  : %s" % gps.lib.gpxUtil.elevation(self.elevation_max))
            writef("Elevation gain : %s" % gps.lib.gpxUtil.elevation(self.elevation_gain))
            writef("Elevation loss : %s" % gps.lib.gpxUtil.elevation(self.elevation_loss))

        writef("Distance    : %s" % gps.lib.gpxUtil.distance(self.distance))
        writef("Trackpoints : %d" % self.point_count)

        if self.point_count:
            writef("Average distance per point: %dm" % (self.distance / self.point_count))

        if False:

            wp_l = WayPoint(copyFrom=bounds.left(),   name="left")
            wp_r = WayPoint(copyFrom=bounds.right(),  name="right")
            wp_t = WayPoint(copyFrom=bounds.top(),    name="top")
            wp_b = WayPoint(copyFrom=bounds.bottom(), name="bottom")

            writef("Left: %s" % wp_l)
            writef("Right: %s" % wp_r)
            writef("Top: %s" % wp_t)
            writef("Bottom: %s" % wp_b)

            gpx = gpxWriter()
            if gpx.open("boundingboxtest.gpx", overwrite=True):
                for i in [wp_l, wp_r, wp_t, wp_b]:
                    gpx.writeItem(i)
                gpx.close()

        writef("")

    def removeBadFilenameChars(self, name):
        name = name.replace(os.path.sep, "-")
        name = name.replace(">", "-")
        name = name.replace("<", "-")
        name = name.replace(":", "-")
        return name

    def gpxWrite(self, fout):
        fout.write(jxml.ele(self.gpxType(), None, end=False) + "\n")
        fout.write(jxml.ele("name", self.name, cdata=True) + "\n")
        fout.write(jxml.ele("type", self.gpxTypeInfo(), cdata=True) + "\n")

        for seg in self.segments:
            fout.write(seg.gpx())

        fout.write(jxml.ee(self.gpxType()) + "\n")

    # Return "virtual" points from this if the distance between real points is too large
    # Note this does not interpolate between points between segments ("working as coded")
    def points_virtual(self, lower_limit, upper_limit):
        
        last = None
        for segment in self.segments:
            for point in segment.pointsInterpolated(lower_limit, upper_limit):
                yield point

        #self.log.i("too far=%d, too close=%d, ok=%d" % (over, under, ok))

    def centre(self):
        lat = 0.0
        lon = 0.0
        count = 0
        for segment in self.segments:
            for point in segment:
                lat += point.latf()
                lon += point.lonf()
                count += 1

        return Point(lat/count, lon/count, name = "Centre of " + self.name)

###############################################################################


class RouteSegment(TrackSegment):
    def gpx(self):
        s = ""
        for tp in self.points:
            s += tp.gpx() + "\n"
        return s


class Route(TrackSegments):

    """A GPX Route"""

    def __init__(self):
        super(Route, self).__init__()
        self.type = None

    def gpxType(self):
        return "rte"
    
    def gpxTypeInfo(self):
        return "Route"
    
    def idStr(self):
        return "ROUTE"

    def newSegment(self):
        return RouteSegment()

    def filename(self, index=0, ext=True):
        name = "%s %d %s" % (self.gpxType(), index, self.name)
        name = self.removeBadFilenameChars(name)
        if ext:
            name += ".GPX"
        return name

    def newOneOfMe(self): # probably a more pythonesque way of doing this
        obj = Route()
        obj.name = self.name
        return obj

    def __repr__(self):
        return "%s: %s", (self.idStr(), self.name)

###############################################################################


class Track(TrackSegments):

    def gpxType(self):
        return "trk"

    def gpxTypeInfo(self):
        return "Track"

    def idStr(self):
        return "TRACK"

    def filename(self, index=0, ext=True):
        
        # Format the date by hand because we don't want utc offsets in there
        time = self.time_first.strftime("%Y-%m-%d %H-%M-%S")
        name = "%s %s-%d - %s" % (self.gpxType(), time, index, self.name)
        name = self.removeBadFilenameChars(name)
        if ext:
            name += ".GPX"
        return name

    def newOneOfMe(self): # probably a more pythonesque way of doing this
        obj = Track()
        obj.name = self.name
        return obj

    def newSegment(self):
        return TrackSegment()

###############################################################################

if __name__ == "__main__":
    print("I don't do anything stand-alone")
