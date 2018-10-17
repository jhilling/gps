#!/usr/bin/env python

"""

Reference: http://en.wikipedia.org/wiki/ISO_8601#Time_zone_designators

To install dateutil on ubuntu do this:
sudo apt-get install python-dateutil

"""

from __future__ import print_function

import sys
import math

from gps.lib.logWriter import LogWriter
from gps.lib.gpxXml import Xml
from gps.lib.gpxUtil import SafeVal

import dateutil.parser
import dateutil.tz

from gps.lib.gpxUtil import utf8

###############################################################################

jxml = Xml()
tz_local_host = dateutil.tz.tzlocal()

###############################################################################


class Point(object):
    """
    An abstract-ish class that trackpoint, routepoint, waypoint are derived from.
    Supports elevation, time, speed, and distance from another Point
    """

    def __init__(self, lat=None, lon=None, copyFrom=None, name=None):

        self.lat = lat
        self.lon = lon

        self.name = name # waypoint?
        self.time_obj = self.elevation = None
        self._distance = 0
        self._speed = 0
        self.log = LogWriter()
        self.cad = self.hr = None # should this not go under trackpoint?

        if copyFrom:
            self.copy(copyFrom)
            if not lat is None:
                self.lat = lat
            if not lon is None:
                self.lon = lon
            if not name is None:
                self.name = name

    # Not sure why these are being stored as strings, but hack these methods in for now
    def latf(self):
        return float(self.lat)

    def lonf(self):
        return float(self.lon)

    def __repr__(self):
        s = "%s\t%s\tT:%s\tLat:%s\tLon:%s\tE:%s" % (utf8(self.name), self.gpxType(), SafeVal(self.timeStr()), SafeVal(self.lat), SafeVal(self.lon), SafeVal(self.elevation))
        #s = "%s\t%s\tT:%s\tLat:%s\tLon:%s\tE:%s" % (self.name, self.gpxType(), SafeVal(None), SafeVal(self.lat), SafeVal(self.lon), SafeVal(self.elevation))
        
        s += self._safeFloat(self._distance)
        s += self._safeFloat(self._speed)
        s += self._safeFloat( self._speed_kmh(self._speed) ) # Convert from m/s to km/h
        return s

    def copy(self, other):
        self.lat  = other.lat
        self.lon  = other.lon
        self.name = "Copy of %s" % other.name
        self.elevation = other.elevation
        #self.time = 
        #self.time_obj =

    def gpx(self):
        s = jxml.ele(self.gpxType(), "", (("lat", self.lat),("lon", self.lon)), False)
        s += jxml.ele("ele", self.elevation, only_when_value=True)
        s += jxml.ele("time", self.timeStr(), only_when_value=True)
        s += jxml.ee(self.gpxType())
        return s

    def gpxType(self):
        return "pt"

    # Distance between 2 lat/longs
    # http://www.movable-type.co.uk/scripts/latlong.html
    def distance(self, point):
        """
        Return the distance between the 2 points in metres
        """

        # radius of the earth in km
        R = 6371

        lat1 = float(self.lat)
        lat2 = float(point.lat)

        lon1 = float(self.lon)
        lon2 = float(point.lon)

        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)

        # Convert to radians
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)

        a = math.sin(dLat/2) * math.sin(dLat/2) + \
            math.cos(lat1) * math.cos(lat2) * math.sin(dLon/2) * math.sin(dLon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = R * c

        return d * 1000
    
    def move(self, xmove, ymove):
        """
        move the point by the given distance in METRES
        1 degree is approx (111.111 km) 
        """
        C=111194.93

        if xmove:
            lond = xmove/C
            self.lon = float(self.lon) + lond
        
        if ymove:
            latd = ymove/C
            self.lat = float(self.lat) + latd

    def _safeFloat(self, val):
        s = "\t"
        if val is None:
            s += "-"
        else:
            s += "%.1f" % val
        return s

    def _speed_kmh(self, speed_ms):
        if speed_ms is None:
            return None
        else:
            speed_kmh = (self._speed * 60 * 60) / 1000
            return speed_kmh

        return s        

    # See also module iso8601.. try import iso8601, iso8601.parse_date(t_string) 
    def setTime(self, t_string):
        if not t_string:
            return False

        # Use dateutil to parse the date. This is a 3rd party library. Install with: apt-get install python-dateutil
        self.time_obj = dateutil.parser.parse(t_string)
        return True

    def timeStr(self):
        if not self.time_obj:
            return None

        # Return the date as the local timezone
        return self.time_obj.astimezone(tz_local_host).isoformat()

    def timeStr_short(self):
        if not self.time_obj:
            return None

        # Return the date as the local timezone
        return self.time_obj.astimezone(tz_local_host).ctime()

    def time_d(self, other):

        if not self.time_obj or not other.time_obj:
            return None

        td = self.time_obj - other.time_obj

        if td.days < 0:
            td = other.time_obj - self.time_obj
            return -td.seconds

        #td.seconds + td.days * 24 * 60 * 60
        return  td.total_seconds()

    def speed(self, other):
        distance_m = self.distance(other)
        time_s = self.time_d(other)

        if time_s is None:
            return None

        if time_s == 0:
            # This means the trackpoint has the same time as the other one
            print("WARNING: 0 time_d?", file=sys.stderr)
            print("This:", self, file=sys.stderr)
            print("Other:", other, file=sys.stderr)
            return None

        speed_m_per_s = distance_m / float(time_s)

        return speed_m_per_s

    def setDistance(self, point):
        """store distance internally"""

        self._distance = self.distance(point)
        return self._distance

    def setSpeed(self, point):
        """store speed internally"""

        speed = self.speed(point)
        if not speed is None:
            self._speed = speed

        return self._speed

    def findNearest(self, segments):
        nearest = None
        ptReturn = None

#        self.log.dbg("have %d segments" % segments.countSegments())

        for segment in segments:
            # TODO Can check the bounds of the segment here
            if not segment.bounds.contains(self):
#                self.log.dbg("skipping segment as point not in it, as determined from bounds check")
                continue
            
            point, d = self.findNearest2(segment)
            
            if nearest is None or d < nearest:
                nearest = d
                ptReturn = point
            
        return (ptReturn, nearest)

    def findNearest2(self, segment):
        # TODO the method should just be "points" and whether it is a derived Track one
        # should determine if it is interpolated or not.
#        for point in segment.points_virtual(interpolate_thres_lower_metres, interpolate_thres_upper_metres):
        ptReturn = nearest = None
        for point in segment:
            d = self.distance(point)
            if nearest is None or d < nearest:
                nearest = d
                ptReturn = point

        return (ptReturn, nearest)

    def findNearest3(self, segment):
        """
        This one takes account of a threshold on the point, which allows
        you to essentially draw an imaginary circle around the waypoint
        for which it has effect in the search.
        """

        ptReturn = nearest = None
        for point in segment:
            d = self.distance(point)

            # This point is nearer, BUT are we close enough for it to count. 
            # Some types of point you want to be quite close to for it to count.

            # Possibly reject if the wp has a threshold on it.
            if d > point.distanceThreshold: # TODO perhaps radius would be a better name
                continue

            if nearest is None or d < nearest:
                nearest = d
                ptReturn = point

        return (ptReturn, nearest)

    def findNearest4(self, segment):
        """
        This one takes account of a threshold on the point, which allows
        you to essentially draw an imaginary circle around the waypoint
        for which it has effect in the search.
        
        Returns an ordered LIST of nearest waypoints, not just the nearest, like version 3 
        """

        found = []

        min = (None, None)

        for point in segment:
            d = self.distance(point)

            # This point is nearer, BUT are we close enough for it to count. 
            # Some types of point you want to be quite close to for it to count.

            # Possibly reject if the wp has a threshold on it.

            if min[0] is None or d < min[0]:
                # make sure we have SOMETHING gets added even if it is miles away
                min = (d, point)

            if d > point.distanceThreshold: # TODO perhaps radius would be a better name
                continue

            found.append( (d, point) )

        found.sort()

        return [min], found

    def interpolate(self, other, lower_limit, upper_limit, include_self=True):

        # This works from self to other
        self.type = "real"

        if include_self:        
            yield self

        if other:

            other.type = "real"

            d = self.distance(other)

            if d > upper_limit:
                required_vpoints = int(d / upper_limit)

                # Make sure the points have timestamps before trying to 
                # interpolate the time 
                if other.time_obj and self.time_obj:
                    td = other.time_obj - self.time_obj
                    ti = td / required_vpoints
                    t_inc = ti
                else:
                    t_inc = None

                #self.log.i("need to insert %d vpoints" % required_vpoints)
                lon_inc = (other.lonf() - self.lonf()) / required_vpoints
                lat_inc = (other.latf() - self.latf()) / required_vpoints


                for i in range(1, required_vpoints):

                    lon = self.lonf() + lon_inc * i
                    lat = self.latf() + lat_inc * i

                    #self.log.i("%d: have lon=%g, lat=%g" % (i, lon, lat))
                    pt = Trackpoint(lat=lat, lon=lon, copyFrom=self)

                    if t_inc:
                        pt.time_obj = self.time_obj + t_inc
                        t_inc += ti

                    pt.type = "virtual"
                    yield pt

            yield other


###############################################################################
## implementations of basic gpx types
###############################################################################    
class Trackpoint(Point):

    def __init__(self, lat=None, lon=None, copyFrom=None, name=None, sym=None):
        super(Trackpoint, self).__init__(lat, lon, copyFrom, name)

    def gpx(self):
#        super(Trackpoint, self).__init__()
        s = jxml.ele(self.gpxType(), "", (("lat", self.lat),("lon", self.lon)), False)
        s += jxml.ele("ele", self.elevation, only_when_value=True)
        s += jxml.ele("time", self.timeStr(), only_when_value=True)

        # Add hr and cad. TODO Need this in the header
        if self.hr or self.cad:
            s += jxml.ele("extensions", "", end=False)
            s += jxml.ele("gpxtpx:TrackPointExtension", "", end=False)
            s += jxml.ele("gpxtpx:hr", self.hr, only_when_value=True)
            s += jxml.ele("gpxtpx:cad", self.cad, only_when_value=True)
            s += jxml.ee("gpxtpx:TrackPointExtension")
            s += jxml.ee("extensions")

        s += jxml.ee(self.gpxType())

        return s

    def gpxType(self):
        return "trkpt"


class WayPoint(Point):

    def __init__(self, lat=None, lon=None, copyFrom=None, name=None, sym=None, cmt=None):
        super(WayPoint, self).__init__(lat, lon, copyFrom, name)
        self.sym = sym
        self.cmt= cmt

    def gpxType(self):
        return "wpt"

    def gpx(self):

        s = jxml.ele(self.gpxType(), "", (("lat", self.lat),("lon", self.lon)), False)
        s += jxml.ele("name", self.name)
        s += jxml.ele("sym", self.sym, only_when_value=True)
        s += jxml.ele("cmt", self.cmt, only_when_value=True)
        s += jxml.ee(self.gpxType())

        return s

    # a way point doesn't need a route/track container
    def gpxWrite(self, fout):
        fout.write(self.gpx() + "\n")


# need to support sym, type
class RoutePoint(Point):

    def __init__(self, lat=None, lon=None):    
        super(RoutePoint, self).__init__(lat, lon)
        self.sym = self.type = None

    def gpxType(self):
        return "rtept"

    def gpx(self):
        s = jxml.ele(self.gpxType(), "", (("lat", self.lat),("lon", self.lon)), False)
        s += jxml.ele("sym", self.sym)
        s += jxml.ele("type", self.type)
        s += jxml.ee(self.gpxType())
        return s

###############################################################################

if __name__ == "__main__":
    # A degree is approx (111.111 km) 
    
#    p1 = Point(lat=0, lon=0)
#    p2 = Point(lat=0, lon=1)
#    
#    d1 = p1.distance(p2)
#    print("distance is", d1)
#
#    p3 = Point(lat=0, lon=0)
#    p3.move(d1, 0)
#
#    d2 = p1.distance(p3)
#    print("distance is", d2)

    p1 = Point(lat=0, lon=0)
    p2 = Point(lat=1, lon=0)
    d1 = p1.distance(p2)
    print("distance is", d1)

    p3 = Point(lat=0, lon=0)
    p3.move(0, d1)

    d2 = p1.distance(p3)
    print("distance is", d2)

    print("P1: %s" % p1)
    print("P2: %s" % p2)
    print("P3: %s" % p3)
    
    d3 = p2.distance(p3)
    print("Error in meters is", d3)

    p4 = Point(lat=1, lon=0)

    # This date is really 7:32 pm in the uk due to the dst flag.  We want to see 7:32 not 6:32 printed
    t='2012-07-11T18:32:23.000Z'
    print("Setting time with this string:", t)
    p4.setTime(t)
    print(p4.time_obj)
    print(p4.timeStr())

