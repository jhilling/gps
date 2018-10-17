#!/usr/bin/python

from __future__ import print_function

import os

from gps.lib.formats.GpxParser import GpxParser
from gps.lib.gpsObserver import GpxObserver

from gps.lib.formats.gpxWriter import gpxWriter


class WaypointDB(object):
    """
    Models dir structure of waypoints with a directory
    which is its distance threshold, e.g:

    ~/GPS_Tracks/Waypoints/10/pubs.gpx
    ~/GPS_Tracks/Waypoints/20/cafes.gpx
    """

    # ~/GPS_Tracks/Waypoints

    def __init__(self):
        self.base_directory = os.path.join(os.path.expanduser("~"), "GPS_Tracks", "Waypoints")

        self.wps = []

        self.scan_directory(self.base_directory)

    def scan_directory(self, base_directory):

        for dirpath, dirnames, filenames in os.walk(base_directory):
            for filename in filenames:
                if os.path.splitext(filename)[1] == ".gpx":
                    self.add_file(os.path.join(dirpath, filename),
                                  os.path.basename(dirpath))

    def add_file(self, filename, distance):
        self.wps.append([filename, int(distance)])

    def get(self):
        for wp in self.wps:
            yield wp


if __name__ == "__main__":

    """
    Dump all the waypoints out as a single gpx file to stdout
    """

    class WaypointObserver(GpxObserver):

        def __init__(self):
            super(WaypointObserver, self).__init__()
            self.gpx = gpxWriter()

        def nextWayPoint(self, point):
            super(WaypointObserver, self).nextWayPoint(point)
            self.gpx.writeItem(point)

        def end(self):
            super(WaypointObserver, self).end()
            self.gpx.close()

    wdb = WaypointDB()

    o = WaypointObserver()
    app = GpxParser(o)

    from gps.lib.logWriter import LogWriter
    log = LogWriter()

    files = [x[0] for x in wdb.get()]

    # Print the waypoints
    app.Parse(files)










