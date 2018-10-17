#!/usr/bin/env python

import unittest

# from gps import gpxQTree

from gps.lib.primitives.gpxBounds import Bounds
from gps.lib.gpxQTree import SegmentsQTree
from gps.lib.primitives.points import Point


class Test1(unittest.TestCase):

    def test_1(self):
        """Just some test code to test the QTree"""

        # Cover the world
        bounds = Bounds()
        #    bounds.registerPoint(Point(-90,-90))
        #    bounds.registerPoint(Point(90, 90))
        bounds.registerPoint(Point(0 ,0))
        bounds.registerPoint(Point(10, 10))

        sqt = SegmentsQTree(bounds, 5)

        for i in range(0, 10):
            p = Point(i ,i)
            sqt.addPoint(p)

        # Add a duplicate point
        sqt.addPoint(Point(5 ,5))

        sqt.queryRangeDebugPrint(Point(0 ,0), Point(20, 20))

        sqt.queryRangeDebugPrint(Point(0 ,0), Point(100, 100))

        sqt.queryRangeDebugPrint(Point(10, 10), Point(20 ,20))

        sqt.queryRangeDebugPrint(Point(9, 9), Point(20 ,20))

        # This won't work with the qtree.

        # this would work better sqt.findNearest(point)
        # which is very similar to queryRange
        #    point.findNearest2(sqt)

        # Get the points 10 meters around a given point

        print("Found these points")
        for p in sqt.queryPoint(Point(5, 5)):
            print(p)

        # TODO actually assert something

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
