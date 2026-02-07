#!/usr/bin/env python



from gps.lib.logWriter import LogWriter
import gps.lib.gpxUtil

import json

# If nearest WP is < than this we say we are "at" that location
AT_PLACE_THRES = 50

###############################################################################

log = LogWriter()

###############################################################################


def stopTxt(durationStationary, pt, tp_first, tp_last):

    return "%s STOPPED %s " % (gps.lib.gpxUtil.duration(durationStationary),
                               stopLoc(pt, tp_first, tp_last))


def stopLoc(pt, tp_first, tp_last):
    # tp_last could be when the GPS was switched on again, don't use it for distance

    # pt could be none
    d = pt and tp_first.distance(pt) or None

    if pt is None or d < AT_PLACE_THRES:
        s = "at %s" % gps.lib.gpxUtil.name(pt)
    else:
        s = "%s away from %s" % (gps.lib.gpxUtil.distance(d), gps.lib.gpxUtil.name(pt))
    return s


class PointTxt(object):
    """
    Model a single "interesting" named point
    """

    def __init__(self, time, dist, name):
        self.time = time
        self.dist = dist
        self.name = name

    def __str__(self):
        return "%s\t%s\t%s" % (self.time, gps.lib.gpxUtil.distance(self.dist), self.name)


class TrackTxt(object):
    def __init__(self, filename, name):
        self.filename = filename
        self.name = name
        self.points = []
        self.hitStats = None
        self.distance = None

    def add(self, point):
        self.points.append(point)

    def __str__(self):
        return 'TRACK: %s|%s' % (self.filename, self.name)


class TrackJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        """Handle serialisation to json"""

        # print type(obj)

        if isinstance(obj, TrackTxt):
            return obj.__dict__

        if isinstance(obj, PointTxt):
            return obj.__dict__

        return super(TrackJSONEncoder, self).default(obj)


class TrackTxtEncoder(object):

    def __init__(self, tracks):
        self.tracks = tracks

    def asText(self):
        lines = []
        for track in self.tracks:
            lines.append(str(track))
            for point in track.points:
                lines.append(str(point))

            hitStats = track.hitStats

            # Add summary info
            lines.append("Trackpoints hit %d, missed %d (%.1f%% waypoint hit rate)" % (hitStats["hit"], hitStats["miss"], hitStats["match_pct"]))
            #        self.log.i("%d/%d\t%.1f%%\t%s" % (hit, hit + miss, match_pct, track.name))
            #        self.log.i("distance %g" % (track.distance))

            lines.append("Moving time %.1f%% - %s moving %s stopped" % (hitStats["mv_pct"],
                                                                gps.lib.gpxUtil.duration(hitStats["movingTime"]),
                                                                gps.lib.gpxUtil.duration(hitStats["stopTimeTotal"])))

            #self.log.i("Stopped time %.1f%% - %s out of %s" % (st_pct, gpxUtil.duration(st), gpxUtil.duration(ts)))
            lines.append("%d stops over %s" % (hitStats["stops"], gps.lib.gpxUtil.distance(hitStats["distance"])))

            lines.append("")


        return "\n".join(lines)

    def asJson(self):
        return json.dumps(self.tracks, cls=TrackJSONEncoder)

    def get(self, format):
        return {"json": self.asJson(), "text": self.asText()}[format]


class MatchBase(object):
    """
    Template matcher which mainly just defines the interface.
    """

    def __init__(self, logger):
        self.log = logger
        self.i = None
        self.track = None
        self.acc_distance = None

    def start(self):
        pass

    def end(self):
        pass

    def startTrack(self, track):
        self.track = track
        self.i = 0
        self.acc_distance = 0

    def addDistance(self, distance):
        self.acc_distance += distance

    def pointInOrOutOfRange(self, tp, wp, distance):
        pass

    def pointOutOfRange(self, tp, wp, distance):
        pass

    def pointInRange(self, tp, found):
        """This gets called for every new point found in range"""
        pass

    def pointDone(self):
        self.i += 1

    def longTimeAtThisOne(self, pt, tp_first, tp_last, durationStationary):
        pass

    def endTrack(self, hitStats):
        pass


class MatchDot(MatchBase):

    def start(self):
        super(MatchDot, self).start()
        self.log.o("digraph test {")

    def end(self):
        super(MatchDot, self).end()
        self.log.o("}")

    def pointInRange(self, tp, found):
        super(MatchDot, self).pointInRange(tp, found)
        d, wp = found[0]

        if self.i == 0:
            self.log.oN('"TRACK: %s|%s" -> "%s"' % (self.track.filename(), self.track.name, wp.name))
        else:
            # NOT the first time!
            self.log.oN(' -> "%s"' % wp.name)

        self.log.dbg("Distance: %f" % self.acc_distance)

    def endTrack(self, hitStats):
        # self.log.o("i is %d" % self.i)
        if self.i > 0: # if already printed something
            self.log.o(";")


class MatchOutputPlain(MatchBase):
    
    def startTrack(self, track):
        super(MatchOutputPlain, self).startTrack(track)

        self.log.o(TrackTxt(self.track.filename(), self.track.name))

        # Print the first point
        tp = track.firstPoint()
        if tp:
            self.log.o(PointTxt(tp.timeStr_short(), self.acc_distance, "Track start"))

    def pointInOrOutOfRange(self, tp, wp, distance):
        super(MatchOutputPlain, self).pointInOrOutOfRange(tp, wp, distance)
#        self.log.o(PointTxt(tp.timeStr_short(), self.acc_distance, "unknown"))

    def pointInRange(self, tp, found):
        super(MatchOutputPlain, self).pointInRange(tp, found)
        d, wp = found[0]
        self.log.o(PointTxt(tp.timeStr_short(), self.acc_distance, wp.name))

    def pointOutOfRange(self, tp, wp, distance):
        super(MatchOutputPlain, self).pointOutOfRange(tp, wp, distance)
        # self.log.o(PointTxt(tp.timeStr_short(), self.acc_distance, "unknown"))

    def longTimeAtThisOne(self, pt, tp_first, tp_last, durationStationary):
        # loc = pt or tp_last or tp_first

        self.log.o(PointTxt(tp_first.timeStr_short(),
                            self.acc_distance,
                            stopTxt(durationStationary, pt, tp_first, tp_last)))

    def endTrack(self, hitStats):
        # Print the last point
        tp = self.track.lastPoint()
        if tp:
            self.log.o("%s\t%s\t%s" % (tp.timeStr_short(), gps.lib.gpxUtil.distance(self.acc_distance), "Track stop"))


class MatchPlainOneLine(MatchBase):
    def startTrack(self, track):
        super(MatchPlainOneLine, self).startTrack(track)
        self.log.oN('TRACK: %s|%s' % (self.track.filename(), self.track.name))

    def pointInRange(self, tp, found):
        super(MatchPlainOneLine, self).pointInRange(tp, found)
        d, wp = found[0]
        self.log.oN(" -> %s" % wp.name)

    def endTrack(self, hitStats):
#         self.log.o("i is %d" % self.i)
        if self.i > 0: # if already printed something
            self.log.o("")
            self.log.o("")

    def longTimeAtThisOne(self, pt, tp_first, tp_last, durationStationary):
#         super(MatchPlainOneLine, self).longTimeAtThisOne(pt, tp_first, tp_last, durationStationary)
        self.log.oN(" (STOPPED %s)" % gps.lib.gpxUtil.duration(durationStationary))

###############################################################################


def main():
    print("I don't do anything stand-alone")


def test():

    print("Running module tests")

    import doctest
    doctest.testmod()

    print("Tests passed")

###############################################################################

if __name__ == "__main__":

    main()
    # test()

