#!/usr/bin/env python3

from __future__ import print_function

import pathhack

from gps.lib.formats.GpxParser import GpxParser
from gps.lib.gpsObserver import GpxObserver
from gps.lib.gpxCommandLine import OptionsGPX

import gps.lib.gpxUtil
from gps.lib.logWriter import LogWriter


class Observer(GpxObserver):

    def __init__(self, options):
        super(Observer, self).__init__()
        self.opts = options

        self.total_distance = 0
        self.total_tracks = 0
        self.total_elevation_gain = 0

        self.log = LogWriter()

    # Overrides for derived classes
    def nextTrack(self, track):
#        self.log.i("TRACK: %s" % track.name)
        if self.opts.print_summary:
            track.PrintStats( self.log.o )

        self.total_distance += track.distance
        self.total_elevation_gain += track.elevation_gain
        self.total_tracks += 1

    def nextTrackPoint(self, trackPoint):
        if self.opts.print_trackpoints:
            self.log.i("%s" % self.tp)

    def end(self):
        if not self.opts.print_total:
            return

        # TODO the range of dates covered
        self.log.i("""
===============================================================================
Totals:
%d tracks processed
Distance       : %s
Elevation gain : %s
""" % (self.total_tracks, gps.lib.gpxUtil.distance(self.total_distance), gps.lib.gpxUtil.elevation(self.total_elevation_gain)))

    def nextRoute(self, route):
        self.log.i("ROUTE: %s" % route.name)

    def nextWayPoint(self, wayPoint):
        self.log.i("WAYPOINT: %s" % wayPoint.name)

###############################################################################


if __name__ == "__main__":

    options, args = OptionsGPX().addSummary().addTrackpoints().addTotal().parse()

    if options.print_summary or options.print_trackpoints or options.print_total:
        pass
    else:
#        print("No output selected, auto selecting totals", file=sys.stderr)
        options.print_summary = options.print_total = True

    app = GpxParser(Observer(options))
    app.Parse(args)
