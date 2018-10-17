#!/usr/bin/env python

from gps.lib.formats.GpxParser import GpxParser
from gps.lib.formats.gpxWriter import gpxWriter
from gps.lib.primitives.gpxSegments import Track
from gps.lib.primitives.points import WayPoint

import gps.lib.gpxCommandLine

from gps.lib.gpsObserver import GpxObserver
from gps.lib.logWriter import LogWriter


class gpxTrackInterpolate(GpxObserver):

    """
    For debugging..
    Create an interpolated track
    """

    def __init__(self, lower, upper):
        super(gpxTrackInterpolate, self).__init__()
        self.upper = upper
        self.lower = lower
        self.log = LogWriter()
        self.gpx = gpxWriter()

    def start(self):
        pass

    def nextTrack(self, track):

        self.log.i("TRACK: %s" % track.name)

        # Write the track out verbatim
        intTrk = Track()
        intTrk.name = "verbatim"
        for point in track.points():
            intTrk.addPoint(point)
        self.gpx.writeItem(intTrk)

        # Write the track out interpolated
        intTrk = Track()
        intTrk.name="interpolated"
        wps = []
        last = None
        i = d = 0
        for point in track.points_virtual(self.lower, self.upper):
            if last:
                d = point.distance(last)
            self.log.i("[%s] dist=%g" % (point.type, d))

            intTrk.addPoint(point)
            wps.append(WayPoint(copyFrom=point, name=str(i)))
            last = point
            i += 1

        self.gpx.writeItem(intTrk)

        # add the interpolated values as waypoints
        for wp in wps:
            self.gpx.writeItem(wp)

    def end(self):
        self.gpx.close()

###############################################################################


def main():

    options, args = gps.lib.gpxCommandLine.OptionsGPX().addThresholds().parse()

    app = GpxParser(gpxTrackInterpolate(options.lower, options.upper))

    app.run(args)


if __name__ == "__main__":
    main()

