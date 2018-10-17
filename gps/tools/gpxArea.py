#!/usr/bin/env python

from gps.lib.gpsObserver import GpxObserver
from gps.lib.formats.GpxParser import GpxParser
import gps.lib.gpxUtil
from gps.lib.logWriter import LogWriter

"""
Print the area a track covers
"""


class Observer(GpxObserver):

    def __init__(self):
        self.log = LogWriter()
        self.filename = None

    def nextFile(self, filename):
        self.filename = filename

    def nextTrack(self, track):
        # self.log.i("Track name: %s" % track.name)

        bounds = track.getBounds()
        # self.log.i("%s:%s: Bounds - %s" % (self.filename, track.name, str(bounds)))
        self.log.i("%s:%s: Area - %s" % (self.filename, track.name, gps.lib.gpxUtil.area(bounds)))


if __name__ == "__main__":
    import sys

    parser = GpxParser(Observer())
    parser.Parse(sys.argv[1:])
