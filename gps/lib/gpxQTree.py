#!/usr/bin/env python3



from gps.lib.logWriter import LogWriter
from gps.lib.primitives.gpxBounds import Bounds
from gps.lib.primitives.gpxSegments import Segment

from gps.lib.primitives.points import Point

from gps.lib.gpxXml import Xml

jxml = Xml()

log = LogWriter()

###############################################################################


class SegmentsQTree(object):

    """This interface should be similar enough to be used in place of Segments hopefully..""" 

    def __init__(self, bounds, size=5): # no idea what makes good max size before split
        self.northWest = self.northEast = self.southWest = self.southEast = None
        self.bounds = bounds # This acts like a filter. Only points within this range are allowed
    
        # OPT could also store the bounds that the points actually cover, as opposed to the total size of the box we are covering.
        # Each segment keeps track of the bounds of the points it contains
        self.bounds_of_my_points = Bounds()

        self.size = size

        self.segment = self.newSegment()
        
        # TODO can we hold our segment plus the other 4 in a Segments? Or will this just be too confusing...
        # it would help compatibility?
        
        self.isSplit = False

    def __str__(self):
        return "self: %s" % ( self.bounds.__str__() )

    def newSegment(self):
        """Maybe this can be overriden to use a segment of a different type"""
        return Segment()
     
    def getBounds(self):
         return self.bounds
     
    def addPoint(self, point):
        
#        log.i("%s" % self)
#        log.i("Trying to addPoint: %s" % point)
        if not self.bounds.contains(point):
#            log.i("out of bounds")    
            # Out of bounds
            return False

        reallocate = False

        self.bounds_of_my_points.registerPoint(point)

        if not self.isSplit: 
#            log.i("have %d items already" % self.segment.count())
            if self.segment.count() < self.size:
#                log.i("adding point to the quad")
                self.segment.addPoint(point)
                return True
#           log.i("quad is full")
            self.isSplit = self.subDivide()

#            reallocate = True

#        log.i("addPoint into subquad")
        ok = self.northWest.addPoint(point) or self.northEast.addPoint(point) or \
            self.southWest.addPoint(point) or self.southEast.addPoint(point)

        if not ok:
            # This can't happen
            log.i("Failed to addPoint: %s" % point)
            log.i("%s" % self)

            log.i("NW: %s\nNE: %s\nSW: %s\nSE: %s" % (self.northWest,
                                                    self.northEast,
                                                    self.southWest,
                                                    self.southEast))
        
        assert(ok)
        
        # This optimisation makes it 4x slower according to my benchmark
        # If doing lots of queries maybe it would be worth it.
#        # Now reallocate the ones at this level into the children.
#        if reallocate:
#            for point in self.segment:
#                self.addPoint(point)
#
#                # Clear the points of this segment. Have all be reallocated in the children.
#                self.segment.points = []

        return ok

    def subDivide(self):
        """Divide this region into four equal parts."""

        log.dbg("/")

        L = self.bounds.left().lon
        R = self.bounds.right().lon
        T = self.bounds.top().lat
        B = self.bounds.bottom().lat

        MID=Point((R-L)/float(2), (T-B)/float(2))

        # NW
        bounds = Bounds()
        bounds.registerPoint( MID )
        bounds.registerPoint( Point(L, T) )
        self.northWest = SegmentsQTree(bounds, self.size)

        # NE
        bounds = Bounds()                
        bounds.registerPoint( MID )
        bounds.registerPoint( Point(R, T) )
        self.northEast = SegmentsQTree(bounds, self.size)

        # SW
        bounds = Bounds()
        bounds.registerPoint( MID )
        bounds.registerPoint( Point(L, B) )
        self.southWest = SegmentsQTree(bounds, self.size)        
        
        # SE
        bounds = Bounds()
        bounds.registerPoint( MID )
        bounds.registerPoint( Point(R, B) )
        self.southEast = SegmentsQTree(bounds, self.size)

        # We don't bother reallocating the ones at this level into the children.
        # we just have to search current level before children 
        
        return True

    # Would be nice if this could be an iterator, but don't think you can 
    # have a recursive iterator
    # TODO Shouldn't this return a Segment type? Or even a qtree type?
    # it seems awful primitive to be doing linear searches on the results
    # perhaps we could sort the result of a query for faster searching.
    # or sort on own values on demand. for fast lookups, or something. 
    def queryRange(self, bounds):

        ret_list = []
        
        if not self.bounds.overlaps(bounds):
            return ret_list

        # Check points in this quad (not children)
        for point in self.segment:
            if bounds.contains(point):
                ret_list.append(point)

        # Recursively check children
        if self.isSplit:
            ret_list += self.northWest.queryRange(bounds)
            ret_list += self.northEast.queryRange(bounds)
            ret_list += self.southWest.queryRange(bounds)
            ret_list += self.southEast.queryRange(bounds)

        return ret_list
    
    def queryRangeDebug(self, bounds):
        log.i("Querying points in bounds:%s" % bounds)
        lst = self.queryRange(bounds)
        log.i("Found %d points" % len(lst))
        for l in lst:
            print(l)
        return lst

    def queryRangeDebugPrint(self, p1, p2):
        bounds = Bounds()
        bounds.registerPoint(p1)
        bounds.registerPoint(p2)
        return self.queryRangeDebug(bounds)

    def queryPoint(self, p, distance_metres=10):
        """
        Query the points around a given point
        """
        bounds = Bounds()
    
        p1 = Point(copyFrom=p)
        p2 = Point(copyFrom=p)
        
        # Top right
        p1.move(distance_metres,distance_metres)
        
        # Bottom left
        p2.move(-distance_metres,-distance_metres)

        bounds.registerPoint(p1)
        bounds.registerPoint(p2)

        return self.queryRange(bounds)


if __name__ == "__main__":
    """Just some test code to test the QTree"""

    # Cover the world
    bounds = Bounds()
#    bounds.registerPoint(Point(-90,-90))
#    bounds.registerPoint(Point(90, 90))
    bounds.registerPoint(Point(0,0))
    bounds.registerPoint(Point(10, 10))

    sqt = SegmentsQTree(bounds, 5)

    for i in range(0, 10):
        p = Point(i,i)
        sqt.addPoint(p)

    # Add a duplicate point
    sqt.addPoint(Point(5,5))

    sqt.queryRangeDebugPrint(Point(0,0), Point(20, 20))

    sqt.queryRangeDebugPrint(Point(0,0), Point(100, 100))

    sqt.queryRangeDebugPrint(Point(10, 10), Point(20,20))
    
    sqt.queryRangeDebugPrint(Point(9, 9), Point(20,20))

    # This won't work with the qtree.

    #this would work better sqt.findNearest(point)
    # which is very similar to queryRange
#    point.findNearest2(sqt)

    # Get the points 10 meters around a given point

    print("Found these points")
    for p in sqt.queryPoint(Point(5, 5)):
        print(p)
