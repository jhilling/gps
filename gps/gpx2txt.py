#!/usr/bin/env python

from __future__ import print_function

import sys
import os

import pathhack

from gps.lib.gpsObserver import GpxObserver
from gps.lib.formats.GpxParser import GpxParser
from gps.lib.primitives.points import WayPoint
from gps.lib.formats.gpxWriter import gpxWriter
from gps.lib.gpxMatcher import Matcher
from gps.lib.logWriter import LogWriter

from gps.lib.gpxWaypointGatherer import WayPointGatherer

from gps.lib.gpxStopSpotter import StopSpotter

from gps.lib.match.gpxPointMatcher import MatchBase, MatchDot, MatchOutputPlain, MatchPlainOneLine

from gps.lib.match.gpxPointMatcherDecorator import \
    MatchTimeDecorator, \
    MatchTimeAndMultiLocationsDecorator, \
    MatchLoggerDecorator, \
    MatchSummaryDecorator, \
    MatchAccumulatorDecorator,\
    MatchJsonPrinterDecorator

import gps.lib.gpxUtil

# POI fetcher
import gps.lib.petitpois

from gps.lib.gpxWaypointDB import WaypointDB

###############################################################################

log = LogWriter()

###############################################################################


class gpx2txtMatcher(Matcher):
    """
    This is a subclass of the Matcher class, which is the main class for 
    matching trackpoints to waypoints.
    """

    # The match threshold here determines how extended the select on the waypoints is
    def __init__(self, track, output, match_threshold_metres):
        super(gpx2txtMatcher, self).__init__(output.log, match_threshold_metres)
        
        self.track = track

        # Idea is that can use different outputters depending on what format is required.
        self.output = output

        self.lastWaypoint = None

        self.lastTrackpoint = None

        filename = os.path.splitext(track.filename())[0] + "_stop.GPX"
        fout = open(gps.lib.gpxUtil.tempFilePath(filename, "gpx2txt"), "w")
        
        self.stopSpotter = StopSpotter(fout)

        # TODO probably want to be able configure this on the command line
        self.shortStopTimeThres = 5 * 60
        self.longStopTimeThres  = 30 * 60

        self.gpxLongStop = None

        self.foundPoints = []

    def prePoint(self, trackpoint, found):
        """
        This gets called for every point in the track, and also included the nearest found waypoint
        which may be miles away.
        We use this for spotting when we are stopped.
        """

        # The the first waypoint in the ordered list, 
        # i.e the nearest waypoint
        d, waypoint = found and found[0] or (None, None)

        if trackpoint.type == "real":
            self.output.addDistance(trackpoint._distance)

            stop = self.stopSpotter.regPoint(trackpoint, waypoint)

            if stop:
                t = stop.getTimeSpan()
                if t and t > self.shortStopTimeThres: # e.g. more than 5 mins
                    self.output.longTimeAtThisOne(stop.nearestWP, stop.tpFirst, stop.tpCurr, t)

                    if self.gpxLongStop and t > self.longStopTimeThres: # e.g more than 30 mins

                        # What is happening here? Spotting when we have a long stop without a nearby waypoint?
                        # This just for the benefit of the debug output file anyway.
                        if not stop.nearestWP:
                            loc = stop.tpCurr or stop.tpFirst
                            tmin = t/60
                            lstop = WayPoint(copyFrom=loc, name="Unknown stop - %d minutes" % tmin)
                            self.gpxLongStop.writeItem(lstop)
            else:

                # We're not stopped but have we moved a long way or has some significant amount of time passed?
                if self.lastTrackpoint:
                    d = trackpoint.distance(self.lastTrackpoint)
                    if d > 100:
                        #print("*** moved " + str(d))
                        #print(trackpoint)
                        #print()
                        pass

                    td = trackpoint.time_d(self.lastTrackpoint)
                    if td > 100:
                        #print("*** time " + str(td))
                        #print(trackpoint)
                        #print()
                        pass


                self.lastTrackpoint = trackpoint


    def foundPoint(self, trackpoint, found):
        """
        This gets called with the nearest waypoint found for each point in the track
        """

        distance, waypoint = found[0] 

        self.output.pointInOrOutOfRange(trackpoint, waypoint, distance)

        if distance < self.match_threshold_metres:

            # Don't keep notifying on the same point
            if waypoint != self.lastWaypoint and \
                    (self.lastWaypoint is None or waypoint.name != self.lastWaypoint.name):

                #self.log.o("%s" % waypoint.name)
                #self.log.o("%s\t%s\t%s" % (self.track.filename(), self.track.name, waypoint.name))
                self.output.pointInRange(trackpoint, found)

                # Write this place to the debug gpx file
                wptmp = WayPoint(copyFrom=waypoint, sym="dot", name=waypoint.name, cmt="gpx2txt nearest point (thres=%d metres)" % self.match_threshold_metres)
                self.stopSpotter.gpxOut.writeItem(wptmp);

                # For the record, here is not where you store a stop.
                # We are flushing the stop out to the screen here because we
                # want it to appear in the right place in the output on the console. 

                self.foundPoints.append(waypoint)

                self.lastWaypoint = waypoint

        else:
            self.output.pointOutOfRange(trackpoint, waypoint, distance)

        self.output.pointDone()

    def endTrack(self):
        self.stopSpotter.done()

###############################################################################


class WayPointGathererFiltered(WayPointGatherer):

    def __init__(self, qtree):
        super(WayPointGathererFiltered, self).__init__()
        self.qtree = qtree

    def allowWayPoint(self, wayPoint):
        """
        Examine the waypoint before adding it.
        Here simply reject based on proximity
        """
        for p in self.qtree.queryPoint(wayPoint):
            
            if not p.name:
                continue

            if p.name != wayPoint.name:
                print("Skipping", wayPoint, "because near waypoint:", p)
            return False

        return True


class TrackCompareObserver(GpxObserver):

    def __init__(self, qtree, max_match_threshold_metres, outputFormatter, poiFetcher=None):

        # TODO beware multiple instances will overwrite each other. consider tempfile.mktemp. This is only for debugging anyway
        self.gpxLongStop = gpxWriter(open(gps.lib.gpxUtil.tempFilePath("stop_unknown.GPX", "gpx2txt"), "w"))

        if not self.gpxLongStop:
            raise Exception("Failed create long stop gpx file" + gps.lib.gpxUtil.tempFilePath("stop_unknown.GPX", "gpx2txt"))

        self.segmentsCompare = qtree

        self.poi = poiFetcher or gps.lib.petitpois.FetchPoi(True)

        self.max_match_threshold_metres = max_match_threshold_metres
        self.output = outputFormatter

        self.log = LogWriter()

        self.fetchPois = True

    def start(self):
        ## TODO doesn't this get called anyway?
        self.output.start()

    def end(self):
        self.output.end()

    def haveBounds(self, bounds):
        pass

    def nextTrack(self, track):
        super(TrackCompareObserver, self).nextTrack(track)

        matcher = gpx2txtMatcher(track, self.output, self.max_match_threshold_metres)

        matcher.gpxLongStop = self.gpxLongStop

        if self.fetchPois:

            self.log.dbg("Track: %s" % (track.filename()))

            self.log.dbg("Fetching POI")

            tb = track.getBounds()
            self.log.i("Track bounds are: %s" % tb)

            self.log.i("Track bounded area is: %s (%s)" % (gps.lib.gpxUtil.area(tb),
                                                           gps.lib.gpxUtil.width_height(tb)))

            area = tb.area() / 1000 / 1000

            # Don't get crazy large areas
            if not area < 5000:
                log.i("Skipping fetching web waypoints as area is very large")
            else:

                bltr = tb.BLTR()

                # Note we are creating another WayPointGatherer, but this one is filtered
                # We will share the same qtree as the original one
                wpgFiltered = WayPointGathererFiltered(self.segmentsCompare)

                #  going to split the boundaries in the smaller chunks
                for poi in self.poi.fetchPoi_gpx_split(*bltr):
                    # TODO maybe move out "hit" pubs to our file (especially when have stopped there)
                    # self.log.i("Wrote poi for track to %s" % (poi))

                    # Let's be quite precise to include these ones.  If any of these points are near points
                    # we already have loaded then they will be rejected.  Otherwise we get duplicates listed.
                    dthres = 30

                    wpgFiltered.Parse(poi, dthres)

        #         self.log.o("TRACK: %s|%s, %s - %s" % (track.filename(), track.name, track.time_first, track.time_last))

        # TODO should interpolate the track such that we only get a point every 100 metres
        # or so to limit number of checks we do
        # Compare with the db

        self.output.startTrack(track)

        # This calls back to "foundPoint" in the derived matcher class above
        hitStats = matcher.matchAlgo2(track, self.segmentsCompare)

        matcher.endTrack()

        hitStatsX = {}
        hitStatsX["hit"] = hitStats[0]
        hitStatsX["miss"] = hitStats[1]
        hitStatsX["match_pct"] = hitStats[2]
        hitStatsX["stopTimeTotal"] = matcher.stopSpotter.stopTimeTotal()
        hitStatsX["stops"] = len(matcher.stopSpotter.stops)
        hitStatsX["distance"] = track.distance

        hitStatsX["st_pct"] = hitStatsX["mv_pct"] = hitStatsX["movingTime"] = 0
        ts = track.duration()
        if ts:
            hitStatsX["st_pct"] = (hitStatsX["stopTimeTotal"] / ts) * 100
            hitStatsX["mv_pct"] = 100 - hitStatsX["st_pct"]
            hitStatsX["movingTime"] = ts - hitStatsX["stopTimeTotal"] # format with gpxUtil.duration()



        self.output.endTrack(hitStatsX)

    def nextTrackPoint(self, trackPoint):
        pass

    def nextRoutePoint(self, routePoint):
        pass

    def done(self):
        self.gpxLongStop.close()


class TrackCompare(object):
    def __init__(self, observers):
        self.observers = observers

    def Parse(self, trackfiles):
        GpxParser(self.observers).Parse(trackfiles)

###############################################################################

# TODO remove / add as method to Bounds
def printBounds(bounds):
    log.i("These are the extremities:")
    log.i("L: %s" % bounds.left())
    log.i("R: %s" % bounds.right())
    log.i("T: %s" % bounds.top())
    log.i("B: %s" % bounds.bottom())
    log.i("")


def gpx2txt_main(wpFiles, trackFiles, max_match_threshold_metres, outputFormatter, useCache):

    log.dbg("Waypoint files are: %s" % wpFiles)
    log.dbg("Tracks files are: %s" % trackFiles)

    wpg = WayPointGatherer()

    for filename, dthres in wpFiles:
        wpg.Parse(filename, dthres)

    # For interest, these are the extreme points
#     bounds = wpg.qtree.getBounds()
#     printBounds(bounds)
#     log.i("%s" % wpg)

    # The observers for the file parse
    compare = TrackCompareObserver(wpg.qtree, max_match_threshold_metres, outputFormatter, gps.lib.petitpois.FetchPoi(useCache))

    observers = [compare]

    # Now need to load a track and check the nearest point for every point in the track
    # specialOne will be the track, and track will be the waypoint db

    GpxParser(observers).Parse(trackFiles)

    compare.done()


@MatchTimeAndMultiLocationsDecorator
@MatchSummaryDecorator
class defaultPrinter(MatchOutputPlain):
    pass


def main():

    wpFiles = list(WaypointDB().get())
    wpFilesStat = []
    trackFiles = []

    # Do a home grown arg parser as we want to be able to specify a radius
    # and have that affect args following it.

    dthres = 300
    max_match_threshold_metres = dthres
    needOptValue = optValue = None
    onTracks = False
    outputFormat = "default"  
    useCache = True

    outputFormats = {"default":  (MatchOutputPlain, [MatchTimeAndMultiLocationsDecorator, MatchSummaryDecorator]),
                     "plain":    (MatchOutputPlain, []),
                     "line":     (MatchPlainOneLine, [MatchLoggerDecorator]),
                     "1":        (MatchPlainOneLine, []),
                     "time":     (MatchOutputPlain, [MatchTimeDecorator]),
                     "json":     (MatchBase, [MatchAccumulatorDecorator, MatchJsonPrinterDecorator]),
                     "dot":       (MatchDot, [])}

    for f in sys.argv[1:]:

        if f in ['-d', '-o']:
            if needOptValue:
                print("Need opt for", needOptValue, "but got", f)
                sys.exit(1)
            else:
                needOptValue = f
        elif f in ['--help', '-h', '-?']:

            print("""
Usage message:
TODO
Separate the files which are used for waypoints and tracks with a --
            """)

        elif f in ['--',]:
            onTracks = True
        elif needOptValue:
            optValue = f
            
            # deal with that OPT/VALUE pair
            if needOptValue == "-d":
#                log.i("Setting distance threshold to %s" % f)
                dthres = int(optValue)
                if dthres > max_match_threshold_metres:
                    max_match_threshold_metres = dthres
            elif needOptValue == '-o':
                outputFormat = optValue
            else:
                print("didn't do anything with that")
                sys.exit(1)

            needOptValue = optValue = None
        elif f in ["--no-cache"]:
            useCache = False

        elif onTracks:
            trackFiles.append(f)
        else:
            statThis = os.stat(f)
            for have in wpFilesStat:
                if have == statThis:
#                    log.i("Ignoring duplicate specification of: %s" % f)
                    break
            else:
                wpFilesStat.append(statThis)
                wpFiles.append( (f, dthres) )

    opFormatter = outputFormats.get(outputFormat)

    if not opFormatter:
        print("Unknown formatter", outputFormat)
        print("Valid values are:", outputFormats.keys())
        sys.exit(1)

    # Instantiate the outputter
    opf = opFormatter[0](log)

    # Add decorators to base outputter
    for dec in opFormatter[1]:
        opf = dec(opf)

    gpx2txt_main(wpFiles, trackFiles, max_match_threshold_metres, opf, useCache)

###############################################################################

if __name__ == "__main__":
    main()

