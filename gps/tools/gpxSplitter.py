#!/usr/bin/env python

from __future__ import print_function

import pathhack

# Required for imports to to work on the command line
import os

from gps.lib import gpxUtil
from gps.lib.gpsObserver import GpxObserverPrint
from gps.lib.formats.GpxParser import GpxParser
from gps.lib.formats.gpxWriter import gpxWriter
from gps.lib.gpxCommandLine import OptionsGPX

split_track_threshold_mins = 4 * 60  # 4 hours
split_track_threshold_metres = 200
tiny_track_area_threshold = 1000 # i.e. 100 x 100 metres


class SplitObserver(GpxObserverPrint):
    """
    This writes each track in a gpx file to a separate file. It
    also splits an individual track when large time or distance
    gap is found between trackpoints
    """

    def __init__(self, options):
        super(SplitObserver, self).__init__()
        self.opts = options

    def nextTrack(self, track):

        self.log.i("Track name: %s" % track.name)

        count = 0

        # TODO note that the distance based split seems to be commented out in gpxSegments currently?
        for t in track.split(opts.time * 60, opts.distance):
            fn = t.filename(count)
            count += 1
            self.log.i("Track: " + fn)

            bounds = t.getBounds()
            self.log.i("Bounds are " + str(bounds))
            self.log.i("Area is " + gpxUtil.area(bounds))

            if bounds.area() < tiny_track_area_threshold: # i.e. 100 x 100 meters
                self.log.i("Area of track is tiny (%s) - not writing out" % (gpxUtil.area(bounds)))
            else:
                # If a directory supplied, use a directory structure with the year for the output.
                # Could do months as well etc
                # May want a separate switch to achieve this.ct means super will work on the subclasses
                if self.opts.output_directory:

                    try: year = str(t.time_first.year)
                    except: year = "unknown_date"

                    dir = os.path.join(self.opts.output_directory, "tracks", year)

                    try: os.makedirs(dir)
                    except: pass

                    fn = os.path.join(dir, fn)

                gpx = gpxWriter(fn)

                if not gpx:
                    self.log.i("Skip as already exists")
                    continue

                self.log.i("Writing %s to %s" % (t.gpxTypeInfo(), fn))

                # Write the track bounds
                gpx.writeItem(t.getBounds())

                gpx.writeItem(t)
                gpx.close()

    def nextTrackPoint(self, trackPoint):
        pass

    def nextRoute(self, route):

        # We could do as for tracks, and as if by magic, it might work
        # but we don't want to split the route, which typically will
        # have large distances between the points!
        ##self.nextTrack(route)

        fn = route.filename()

        if self.opts.output_directory:
            dir = os.path.join(self.opts.output_directory, "routes")
            try: os.makedirs(dir)
            except: pass
            fn = os.path.join(dir, fn)

        gpx = gpxWriter(fn)

        if not gpx:
            self.log.i("Skip: %s" % route.filename())
            return

        self.log.i("Writing %s to %s" % (route.gpxTypeInfo(), route.filename()))

        gpx.writeItem(route)

        gpx.close()


if __name__ == "__main__":
    
    op = OptionsGPX()
    op.addOutputDirectory()
    op.addOption('--time', '-t', type="int", action='store', default=split_track_threshold_mins, help="time split thres mins")
    op.addOption('--distance', '-D', type="int", action='store', default=split_track_threshold_metres, help="dist split thres metres")
 
    opts, args = op.parse()

    app = GpxParser(SplitObserver(opts))

    # Note that when this script is run directly, the output (by default) goes to 
    # the users home directory, and the tracks are filed by year.
    # When the main class is accessed through gpxstat split the tracks are dumped in the cwd. 

    # Remember the filename of the SOURCE gpx file has no significance WRT the 
    # file written out. It is the date and TRACK name which is used for the output name 
    
    if not opts.output_directory:
        opts.output_directory = os.path.join(os.path.expanduser("~"), "GPS_Tracks", "Repository")
        app.log.i("Writing files to %s" % opts.output_directory)

    app.run(args)

