#!/usr/bin/env python

from gps.lib.logWriter import LogWriter


class GpxObserver(object):
    """
    Base gpx element observer.  Receives gpx elements as they are parsed
    """

    def start(self):
        pass

    def nextFile(self, filename):
        pass

    def haveBounds(self, bounds):
        """This is the bounds of the file, before much processing has happened.
        The idea being that you can abort early if bounds not in range."""
        pass

    # Overrides for derived classes
    def nextTrack(self, track):
        pass

    def nextTrackSegment(self, segment):
        pass

    def nextTrackPoint(self, trackPoint):
        pass

    def nextRoute(self, route):
        pass

    def nextRoutePoint(self, routePoint):
        pass

    def nextWayPoint(self, wayPoint):
        pass

    def end(self):
        """Call when all files parsed"""
        pass


class GpxObserverPrint(GpxObserver):
    """
    Prints gpx elements as it receives them
    For customising output add a decorator in gpxPointMatchWriter, don't use this.
    These Observers are for hooking into the "pre-parsed" data
    """

    def __init__(self, log=None):
        self.log = log or LogWriter()

    def start(self):
        self.log.i("START")

    def nextFile(self, filename):
        # When processing StringIO instances when don't have a filename
        if str(filename):
            self.log.dbg("\nParsing: %s" % filename)

    # Overrides for derived classes
    def nextTrack(self, track):
        self.log.i("TRACK: %s" % track.name)

    def nextTrackSegment(self, segment):
        self.log.i("TRACK SEGMENT: " + str(segment))

    def nextTrackPoint(self, trackPoint):
        self.log.i("TRACK POINT: " + str(trackPoint))

    def nextRoute(self, route):
        self.log.i("ROUTE: %s" % route.name)

    def nextRoutePoint(self, routePoint):
        self.log.i("ROUTE POINT:")

    def nextWayPoint(self, wayPoint):
        self.log.i("WAYPOINT: %s" % wayPoint.name)

    def end(self):
        self.log.i("END")


if __name__ == "__main__":

    pass


