#!/usr/bin/env python

from __future__ import print_function

from gps.lib.formats.GpxParser import GpxParser
from gps.lib.gpxCommandLine import OptionsGPX
from gps.lib.gpxMatcher import Matcher
from gps.lib.gpsObserver import GpxObserver
from gps.lib.logWriter import LogWriter


class gpxTrackMatcher(GpxObserver):
    """Use the first track read as a track to look for in other tracks"""

    def __init__(self, options):
        super(gpxTrackMatcher, self).__init__()
        self.opts = options
        self.log = LogWriter()

    def start(self, match_pct_thres=75):
        self.specialOne = None
        self.count = 0
        self.match_pct_thres = match_pct_thres

    def nextTrack(self, track):

        if self.specialOne is None:
            self.log.i("Using %s as the segment" % track.name)
            self.specialOne = track
            self.specialOne.name += " segment"
        else:

#            self.gpx = gpxWriter()
#            f=self.gpx.open("match %s against %s.GPX" % (self.specialOne.filename(ext=False), track.filename(ext=False)), overwrite=False)

#            if not f:
#                self.log.i("Skipping %s" % track.filename(self.count))
#                return

#            self.gpx.writeItem(self.specialOne)

            self.log.i("Checking %s against %s" % (track.name, self.specialOne.name))

            matcher = Matcher(self.log)

            # look for matches in the special in this one
            hit, miss, match_pct = matcher.matchAlgo(self.specialOne, track)

            if match_pct > self.match_pct_thres:
                result_str = "MATCH"
            else:
                result_str = "no match"

            self.log.i("Hit %d, missed %d, is %f%% = %s" % (hit, miss, match_pct, result_str))

            self.log.o("%d/%d\t%.1f%%\t%s\t%s" % (hit, hit + miss, match_pct, result_str, track.name))
            # self.fout.flush()

##            self.gpx.close()
            self.count += 1


if __name__ == "__main__":
    
    options, args = OptionsGPX().parse()

    app = GpxParser(gpxTrackMatcher(options))

    app.run(args)
