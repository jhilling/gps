#!/usr/bin/env python3

"""
cats GPX file(s) and
derives a WP in the center for each of the passed in tracks
"""

from __future__ import print_function

import pathhack

from gps.lib.formats.GpxParser import GpxParser
from gps.lib.gpxCommandLine import OptionsGPX
from gps.lib.formats.gpxWriter import gpxWriter

from gps.lib.primitives.points import WayPoint

from gps.lib.gpsObserver import GpxObserver
from gps.lib.logWriter import LogWriter


class Observer(GpxObserver):

    def __init__(self, options):
        super(Observer, self).__init__()

        self.opts = options

        self.log = LogWriter()

        self.w = gpxWriter()

    def nextTrack(self, track):
        self.log.i("TRACK: %s" % track.name)
        self.w.writeItem(track)

        cp = track.centre()
        wp = WayPoint(copyFrom=cp, name=cp.name)
        self.w.writeItem(wp)

    def nextRoute(self, route):
        self.log.i("ROUTE: %s" % route.name)
        #self.w.writeItem(route)

    def end(self):
        self.w.close()

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
