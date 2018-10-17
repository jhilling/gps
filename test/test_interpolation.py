#!/usr/bin/env python
import pathhack
import unittest

# from gps import gpxQTree

from gps.lib.primitives.points import Point
from gps.lib.primitives.gpxSegments import TrackSegment


class Test2(unittest.TestCase):
    p1 = Point(lat=50, lon=50)
    p1.setTime("2012-07-23T12:00:00Z")

    p2 = Point(lat=50.05, lon=50)
    p2.setTime("2012-07-23T13:00:00Z")

    p3 = Point(lat=50.10, lon=50)
    p3.setTime("2012-07-23T14:00:00Z")

    expected = [
            {
                "distance": 0,
                "lat": 50,
                "lon": 50,
                "type": "real"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.00090909090909,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.00181818181818,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.00272727272727,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.00363636363636,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.086296950297,
                "lat": 50.00454545454546,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.00545454545455,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.00636363636364,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.00727272727273,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.00818181818182,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.00909090909091,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.01,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.01090909090909,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.01181818181818,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.086296950297,
                "lat": 50.012727272727275,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.013636363636365,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.014545454545456,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.015454545454546,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.016363636363636,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.017272727272726,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.018181818181816,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.019090909090906,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.019999999999996,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.086296950297,
                "lat": 50.02090909090909,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.02181818181818,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.02272727272727,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.02363636363636,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.02454545454545,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.025454545454544,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.026363636363634,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.027272727272724,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.028181818181814,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.029090909090904,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.086296950297,
                "lat": 50.03,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.03090909090909,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.03181818181818,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.03272727272727,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.03363636363636,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.03454545454545,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.03545454545454,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.03636363636363,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.03727272727272,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.086296950297,
                "lat": 50.03818181818182,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.03909090909091,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.04,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.04090909090909,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.04181818181818,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.04272727272727,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.04363636363636,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.04454545454545,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.04545454545454,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.086296950297,
                "lat": 50.04636363636364,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.04727272727273,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.04818181818182,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.04909090909091,
                "lon": 50.0,
                "type": "virtual"
            },
            {
                "distance": 101.08629694950692,
                "lat": 50.05,
                "lon": 50,
                "type": "real"
            }
        ]

    def test_interpolation(self):
        """Test point interpolation against known data"""

        i = 0
        last = None

        for p in Test2.p1.interpolate(Test2.p2, 50, 100):

            ex = Test2.expected[i]

            self.assertEquals(p.lat, ex["lat"])
            self.assertEquals(p.lon, ex["lon"])

            if not last:
                last = p

            self.assertEquals(p.distance(last), ex["distance"])
            self.assertEquals(p.type, ex["type"])

            last = p
            i += 1

        self.assertEquals(i, 56)

    def test_segint2(self):
        seg = TrackSegment()
        seg.addPoint(Test2.p1)
        seg.addPoint(Test2.p2)

        data = list(seg.pointsInterpolated(5000, 20000))

        self.assertEquals(data[0].lat, 50)
        self.assertEquals(data[0].lon, 50)

        self.assertEquals(data[1].lat, 50.05)
        self.assertEquals(data[1].lon, 50)

    def test_segint3(self):
        seg = TrackSegment()
        seg.addPoint(Test2.p1)
        seg.addPoint(Test2.p2)
        seg.addPoint(Test2.p3)

        data = list(seg.pointsInterpolated(5000, 20000))

        self.assertEquals(data[0].lat, 50)
        self.assertEquals(data[0].lon, 50)

        self.assertEquals(data[1].lat, 50.05)
        self.assertEquals(data[1].lon, 50)

        self.assertEquals(data[2].lat, 50.10)
        self.assertEquals(data[2].lon, 50)


if __name__ == '__main__':
    unittest.main()
