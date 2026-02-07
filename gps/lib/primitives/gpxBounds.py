#!/usr/bin/env python



from gps.lib.gpxXml import Xml
from gps.lib.primitives.points import Point

jxml = Xml()


# TODO gpx supports the bounds type. Change this so can write self out to gpx.
# Can the container types to writer their bounds out? is that valid gpx? 
class Bounds(object):

    """Store the extreme top, bottom, left, right of the points
    registered.  Stores references to the points passed in, so the type
    of the extremes will be whatever was passed in"""

    def __init__(self):
        self.leftObj = self.rightObj = self.topObj = self.bottomObj = None

    def registerPoint(self, point):

        if point is None:
            return

        # Latitude is the Y axis, longitude is the X axis
        # Lat: north of equator +ve
        # Lon: east/right of Grenwich +ve

        if self.leftObj is None or float(point.lon) < float(self.leftObj.lon):
#            print("L was", self.leftObj)
            self.leftObj = point
#            print("L is now", self.leftObj)
#            print()
            
        if self.rightObj is None or float(point.lon) > float(self.rightObj.lon):
            self.rightObj = point
        if self.topObj is None or float(point.lat) > float(self.topObj.lat):
            self.topObj = point
        if self.bottomObj is None or float(point.lat) < float(self.bottomObj.lat):
            self.bottomObj = point

    def registerBounds(self, bounds):
        self.registerPoint(bounds.leftObj)
        self.registerPoint(bounds.rightObj)
        self.registerPoint(bounds.topObj)
        self.registerPoint(bounds.bottomObj)


    def left(self):
        """
        Return the leftmost point
        """
        return self.leftObj
    def right(self):
        return self.rightObj
    def top(self):
        return self.topObj
    def bottom(self):
        return self.bottomObj

    def BLTR(self):
        """
        Return the co-ords of the bottom, left, top, right
        """
        return float(self.bottomObj.lat), float(self.leftObj.lon), float(self.topObj.lat), float(self.rightObj.lon)

    def BLTR_grow(self, lat, lon):
        """
        Grow the bound to the nearest lat/long
        """

        b, l, t, r = self.BLTR()
        
        blower = b - (b % lat) 
        tupper = t - (t % lat) + lat

        llower = l - (l % lon)
        rupper = r - (r % lon) + lon

        return blower, llower, tupper, rupper

    def split(self, lat = 0.25, long = 0.5):
        """Return sets of co-ordinates of the the bigger boundary"""
        B, L, T, R = self.BLTR_grow(lat, long)

        b = B
        while b < T:
            t = b + lat

            l = L
            while l < R:
                r = l + long
                yield b, l, t, r
                l += long
            b += lat

    def area(self):
        """Get the area of the bounds in square square metre"""
        return self.width() * self.height()

    def width(self):
        """Get width in metres"""
        if self.leftObj is None or self.rightObj is None:
            return 0
        wl = Point(0, self.leftObj.lon)
        wr = Point(0, self.rightObj.lon)
        return wl.distance(wr)

    def height(self):
        """Get height in metres"""
        if self.topObj is None or self.bottomObj is None:
            return 0
        ht = Point(self.topObj.lat, 0)
        hb = Point(self.bottomObj.lat, 0)
        return ht.distance(hb)

    def overlaps(self, other):
        """Test if one Bounds overlaps another"""
        # TODO why are these stored as strings!!
        # TODO this wants some checking......
        # TODO this might need >= treatment like "contains"

        if float(self.rightObj.lon) > float(other.leftObj.lon) and float(self.leftObj.lon) < float(other.rightObj.lon):
            if float(self.topObj.lat) > float(other.bottomObj.lat) and float(self.bottomObj.lat) < float(other.topObj.lat):
                return True

        return False

    def contains(self, point):
        """Test if a point falls within the bounds"""
        
        if not (point and self.leftObj and self.rightObj and self.topObj and self.bottomObj):
            return False

        if float(point.lon) >= float(self.leftObj.lon) and float(point.lon) < float(self.rightObj.lon):
            if float(point.lat) < float(self.topObj.lat) and float(point.lat) >= float(self.bottomObj.lat):
                return True

        return False

    def gpxType(self):
        return "metadata"

    def gpxWrite(self, fout):

        attrs = [ ("minlat", self.bottom().lat), ("minlon", self.left().lon), ("maxlat", self.top().lat), ("maxlon", self.right().lon) ]

        fout.write(jxml.ele(self.gpxType(), None, end=False) + "\n")
        fout.write(jxml.ele("bounds", None, attrs) + "\n")
        fout.write(jxml.ee(self.gpxType()) + "\n")

    def __repr__(self):
        
        L = R = T = B = "-"
        
        if self.bottomObj:
            B = self.bottomObj.lat
            
        if self.leftObj:
            L =  self.leftObj.lon

        if self.topObj:
            T = self.topObj.lat
           
        if self.rightObj: 
            R = self.rightObj.lon

        s = "B:%s L:%s\tT:%s R:%s" % (B, L, T, R)
        return s


def test():

    from gps.lib.primitives.points import WayPoint

    L = WayPoint()

    b = Bounds()

    p1 = Point(51.360795, -1.170731)
    p2 = Point(51.612207, -0.673599)

    b = Bounds()
    b.registerPoint(p1)
    b.registerPoint(p2)

    print(b)
    for x in b.split():
        print(x)


if __name__ == "__main__":
    test()

