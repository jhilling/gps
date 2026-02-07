#!/usr/bin/env python3

import gps.lib.gpxCommandLine

from gps.lib.formats.GpxParser import GpxParser
from gps.lib.gpsObserver import GpxObserver
from gps.lib.logWriter import LogWriter


class gpxTrackPointDistances(GpxObserver):

    """
    For debugging..
    Print the distance between successive points for
    a real track and an interpolated track
    """

    def __init__(self, lower, upper):
        super(gpxTrackPointDistances, self).__init__()
        self.upper = upper
        self.lower = lower
        self.log = LogWriter()

    def nextTrack(self, track):

        self.log.o("TRACK: %s" % track.name)

        # Real points
        last = None
        d = 0
        for point in track.points():
            if last:
                d = point.distance(last)

            self.log.o("dist real=%g" % d)
            last = point

        # Virtual points (interpolated)
        last = None
        d = 0
        for point in track.points_virtual(self.lower, self.upper):
            if last:
                d = point.distance(last)

            self.log.o("[%s] dist virt=%g" % (point.type, d))
            last = point

###############################################################################


def main():

    options, args = gps.lib.gpxCommandLine.OptionsGPX().addThresholds().parse()
    app = GpxParser(gpxTrackPointDistances(options.lower, options.upper))
    app.run(args)

if __name__ == "__main__":
    main()
