#!/usr/bin/env python3

"""
This is the layer below the Rest Handler (see gpxRestFlask.py).
the idea being different Rest frameworks can be used to call into this.
"""

from gps.lib import petitpois

from gps.lib.formats.GpxParser import GpxParser

from gps.lib.gpxWaypointGatherer import WayPointGatherer

from gps.lib.logWriter import LogWriter

from gps.gpx2txt import TrackCompareObserver

from gps.lib.gpxWaypointDB import WaypointDB

from gps.lib.match.gpxPointMatcher import MatchOutputPlain, TrackTxtEncoder
from gps.lib.match.gpxPointMatcherDecorator import MatchSummaryDecorator, MatchAccumulatorDecorator


###############################################################################

log = LogWriter()

###############################################################################


class GpxRest(object):

    def __init__(self, use_cache=True):
        self.wpg = WayPointGatherer()
        self.use_cache = use_cache

        self.auto_load()

        self.max_match_threshold_metres = 300

        # output will be saved in the memfile object

        self.poi = petitpois.FetchPoi(use_cache)

    def handler(self, trackFiles, format):

        # It doesn't matter which MatchBase class we use.
        # This used to receive the output as the file is parsed/processed
        # by the matching algo
        matcherHandler = MatchSummaryDecorator(MatchAccumulatorDecorator(MatchOutputPlain(log)))

        # Observer for the file parse. This looks for the landmarks
        # as the file is parsed.
        compareObserver = TrackCompareObserver(self.wpg.qtree, self.max_match_threshold_metres, matcherHandler, self.poi)

        log.dbg("Tracks files are: %s" % trackFiles)

        # Now need to load a track and check the nearest point for every point in the track
        # specialOne will be the track, and track will be the waypoint db

        # The observers for the file parse
        observers = [compareObserver]

        tc = GpxParser(observers)

        tc.Parse(trackFiles)

        encoder = TrackTxtEncoder(matcherHandler.trackstxt)

        return encoder.get(format)

    def close(self):
        self.parse_result.done()

    def load_wp(self, filename, dthres):
        print(("Loading " + filename))
        self.wpg.Parse(filename, dthres)

    def auto_load(self):
        wdb = WaypointDB()

        for filename, dthres in wdb.get():
            self.load_wp(filename, dthres)


def main(argv):

    gpxrest = GpxRest()

    gpxrest.handler(argv[1:])

    # gpxrest.serve()

###############################################################################

if __name__ == "__main__":

    # Run directly, e.g. no rest service. See gpxRestFlask.py to run the rest service
    import sys
    main(sys.argv)
