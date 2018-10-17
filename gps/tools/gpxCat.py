#!/usr/bin/env python

from __future__ import print_function

import pathhack

from gps.lib.gpsObserver import GpxObserverPrint
from gps.lib.gpxCommandLine import OptionsGPX
from gps.lib.formats.gpxWriter import gpxWriter
from gps.lib.formats.GpxParser import GpxParser

###############################################################################


class gpxCat(GpxObserverPrint):

    """
    Concatenate trackpoints, waypoints, routes from passed in from files to stdout as a single gpx file.
    Optionally filter out routes, waypoints, or trackpoints.
    """
    
    def __init__(self, options):
        super(gpxCat, self).__init__()
        self.opts = options
        self.gpx = gpxWriter()

    def nextTrack(self, track):
        super(gpxCat, self).nextTrack(track)
        if self.opts.print_trackpoints:
            self.gpx.writeItem(track)

    def nextWayPoint(self, point):
        super(gpxCat, self).nextWayPoint(point)
        if self.opts.print_waypoints:
            self.gpx.writeItem(point)

    def nextRoute(self, route):
        super(gpxCat, self).nextRoute(route)
        if self.opts.print_routes:
            self.gpx.writeItem(route)

    def nextRoutePoint(self, routePoint):
        pass

    def nextTrackPoint(self, trackPoint):
        pass

    def end(self):
        self.gpx.close()

###############################################################################


if __name__ == "__main__":

    options, args = OptionsGPX().addTrackpoints().addWaypoints().addRoutes().parse()

    if options.print_trackpoints or options.print_waypoints or options.print_routes:
        pass
    else:
        options.print_trackpoints = options.print_waypoints = options.print_routes = True

    app = GpxParser(gpxCat(options))

    app.run(args)
