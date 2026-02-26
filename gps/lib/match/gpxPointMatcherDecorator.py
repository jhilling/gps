#!/usr/bin/env python

"""
Decorators for classes of type MatchBase + subclasses (see gpxPointMatcher.py)
"""

from .gpxPointMatcher import TrackTxt, PointTxt, stopTxt, TrackTxtEncoder

import gps.lib.gpxUtil


class MatchDecorator(object):
    """
    Generic template base class for doing Decorators,
    This delegates unknown property/method references to the parent - neat!
    When decorating a method, you usually want to call the parent's method
    too (see examples such as MatchAccumulatorDecorator)
    """

    def __init__(self, parent):
        self.parent = parent

    # For any access to properties or methods unknown to the decorator, go to the parent
    def __getattr__(self, name):
        return getattr(self.parent, name)


class MatchAccumulatorDecorator(MatchDecorator):
    """
    This creates a version in memory of the landmarks as they come in
    using TrackTxt and PointTxt.
    Used for printing the result out as json
    """
    def __init__(self, parent):
        super(MatchAccumulatorDecorator, self).__init__(parent)
        self.trackstxt = []
        self.tracktxt = None

    def startTrack(self, track):
        self.parent.startTrack(track)

        self.tracktxt = TrackTxt(self.track.filename(), self.track.name)
        self.trackstxt.append(self.tracktxt)

        # Print the first point
        tp = track.firstPoint()
        if tp:
            self.tracktxt.add(PointTxt(tp.timeStr_short(), self.acc_distance, "Track start"))

    def pointInRange(self, tp, found):
        self.parent.pointInRange(tp, found)

        d, wp = found[0]
        self.tracktxt.add(PointTxt(tp.timeStr_short(), self.acc_distance, wp.name))

    def longTimeAtThisOne(self, pt, tp_first, tp_last, durationStationary):
        self.parent.longTimeAtThisOne(pt, tp_first, tp_last, durationStationary)

        self.tracktxt.add(PointTxt(tp_first.timeStr_short(),
                                   self.acc_distance,
                                   stopTxt(durationStationary, pt, tp_first, tp_last)))

    def endTrack(self, hitStats):
        self.parent.endTrack(hitStats)

        self.tracktxt.hitStats = hitStats

        tp = self.track.lastPoint()
        if tp:
            self.tracktxt.add(PointTxt(tp.timeStr_short(),
                                       self.acc_distance,
                                       "Track stop"))


def DecMatchAccumulatorDecorator(otherCls):

    return MatchAccumulatorDecorator





class MatchJsonPrinterDecorator(MatchDecorator):

    """This is relying on the data gathered by the MatchAccumulatorDecorator so make sure that has been included"""

    def end(self):
        self.parent.end()

        encoder = TrackTxtEncoder(self.trackstxt)

        # Now we need to print the thing
        self.log.o(encoder.asJson())


class MatchLoggerDecorator(MatchDecorator):
    """
    Add some more logging to a basic matcher outputter
    """

    def pointInOrOutOfRange(self, tp, wp, distance):
        self.log.i("Found point: %s" % tp)
        self.log.i("Distance: %f (out of range)" % distance)

        self.parent.pointInOrOutOfRange(tp, wp, distance)

    def longTimeAtThisOne(self, pt, tp_first, tp_last, durationStationary):
        self.parent.longTimeAtThisOne(pt, tp_first, tp_last, durationStationary)

        # self.log.i("%s\t%s\t%s STOPPED at %s" % (tp_first.timeStr_short(),
        #                   gpxUtil.distance(self.parent.acc_distance),
        #                   gpxUtil.duration(durationStationary),
        #                   self.parent.stopLoc(pt, tp_first, tp_last)))

        self.log.i("pt:       %s" % pt)
        self.log.i("tpCurr first: %s" % tp_first)
        self.log.i("tpCurr last:  %s" % tp_last)


class MatchSummaryDecorator(MatchDecorator):
    """
    Print summary information at the end of each track
    """

    def endTrack(self, hitStats):

        self.parent.endTrack(hitStats)

        self.log.i("Trackpoints hit %d, missed %d (%.1f%% waypoint hit rate)" % (hitStats["hit"], hitStats["miss"], hitStats["match_pct"]))
        # self.log.i("%d/%d\t%.1f%%\t%s" % (hit, hit + miss, match_pct, track.name))
        # self.log.i("distance %g" % (track.distance))

        self.log.i("Moving time %.1f%% - %s moving, %s stopped" % (hitStats["mv_pct"],
                                                          gps.lib.gpxUtil.duration(hitStats["movingTime"]),
                                                          gps.lib.gpxUtil.duration(hitStats["stopTimeTotal"])))

        # self.log.i("Stopped time %.1f%% - %s out of %s" % (st_pct, gpxUtil.duration(st), gpxUtil.duration(ts)))
        self.log.i("%d stops over %s" % (hitStats["stops"], gps.lib.gpxUtil.distance(hitStats["distance"])))


class MatchTimeDecorator(MatchDecorator):
    """
    Include the date/time of the stop
    """

    def pointInRange(self, tp, found):
        self.parent.pointInRange(tp, found)

        d, wp = found[0]
        self.log.o("%s\t%s\t%s" % (tp.timeStr_short(), gps.lib.gpxUtil.distance(self.acc_distance), wp.name))


class MatchTimeAndMultiLocationsDecorator(MatchDecorator):
    """
    Include the date/time of the stop and multiple locations
    e.g. Charvil/Alpars Kebab Van
    """

    def pointInRange(self, tp, found):

        # Do not ripple up call to parent - we need to control the output otherwise get dups printed so this needs to to right
        # after the base class in a chain of decorators

        #self.parent.pointInRange(tp, found)

        d, wp = found[0]

        location = ""
        for i, found in enumerate(reversed(found)):
            d, wp = found

            # It is possible to have an empty name, just skip it
            if not wp.name:
                continue

            if i > 0:
                location += "/"

            location += wp.name

        self.log.o("%s\t%s\t%s" % (tp.timeStr_short(), gps.lib.gpxUtil.distance(self.acc_distance), location))


def testDecorators():
    """
    >>> from gps.lib.match.gpxPointMatcher import MatchBase
    >>> from gps.lib.logWriter import LogWriter
    >>> obj = MatchBase(LogWriter())
    >>> obj.value = 10

    The value is inherited by the decorated object
    >>> dec1 = MatchLoggerDecorator(obj)
    >>> dec1.value
    10

    The value is inherited again by another level of decorator
    >>> dec2 = MatchLoggerDecorator(dec1)
    >>> dec2.value
    10

    Change the base, value, the decorated value changes
    >>> obj.value += 10
    >>> dec1.value
    20
    >>> dec2.value
    20

    Add a value to the decorated object and show that value is used downstream
    >>> dec1.value = 25
    >>> dec2.value
    25
    """

    pass


def main():
    print("I don't do anything stand-alone")


def test():

    print("Running module tests")

    import doctest
    doctest.testmod()

    print("Tests passed")

###############################################################################

if __name__ == "__main__":

    #main()
    test()

