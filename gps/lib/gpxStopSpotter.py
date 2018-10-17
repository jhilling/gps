#!/usr/bin/env python

from __future__ import print_function

import pathhack

import sys
import datetime

from gps.lib.primitives.points import Point, WayPoint
from gps.lib.formats.gpxWriter import gpxWriter
from gps.lib.logWriter import LogWriter
from gps.lib.primitives.gpxSegments import Track

from gps.lib import gpxUtil

# This is how far you have to travel from being stopped to be considered "started" again
# Have increased from 20 to 35 based on noise when gps stationary
# Algo can surely be improved
STOP_TO_START_THRES = 35

###############################################################################

log = LogWriter()

###############################################################################


class Stop(object):
    """
    This implements the algo for deciding if the person is stopped or not.

    Do think I need to do it based on speed.
    What if there are two points a long way apart with a big time gap?
    Does that count as a stop? Only if speed was very slow!?
    Also need to use a sliding window.  Don't think I can just
    move up in blocks.
    """

    def __init__(self, trackpoint, nearestWP):
        self.tpFirst = self.tpCurr = trackpoint 
#         self.tpLast

        self.nearestWP = nearestWP
        self.distance = 0
        self.on_a_stop = False

        self.tpCurrWP = None

    def setNextPoint(self, waypoint, trackpoint, force=False):
        """
        Take the next point and decide whether it is part of
        the same stop or not.  Return True if it is.
        """
        
        if not self.nearestWP:
            self.nearestWP = waypoint

        d = trackpoint.distance(self.tpFirst)
        t = trackpoint.time_d(self.tpFirst)

#         print("%f and %d seconds from %s" % (d, t, self.tpFirst))

        inRange = (d < STOP_TO_START_THRES)

        if not inRange and d < 10000:
           # Here we are detecting the scenario when come to a stop at pub. Turn off gps.
           # Later, set off, forget to turn gps on, turn it on.. 
           # Let's assume if the d is greater than 10 k that you've jumped in a plane or something.
            t2 = trackpoint.time_d(self.tpCurr)
            if t2 > (5 * 60):
                log.dbg("(Big time gap of %d minutes - considering this point to be part of the stop. Distance is %d meters)" % (t2/60, d))
                #log.dbg("wp is " + str(self.nearestWP))
                #log.dbg("tp is " + str(trackpoint))
                inRange = True

        # Is d from first point large? In which case should break the run. 
        if not inRange and not force:
            return None

        self.distance += trackpoint.distance(self.tpCurr)

#         if self.distance > 100:
#             return None

        self.tpCurr = trackpoint
        self.tpCurrWP = waypoint

        return inRange

    def getTimeSpan(self):
        """
        Return timespan in seconds
        """
        return self.tpCurr.time_d(self.tpFirst)

    def getSpeed_window(self):
        
        timeDelta_Window = self.getTimeSpan()

        # TODO if the point causes a massive time gap and already in
        # a stop, then ww timeDelta_Window want to take the current point into account

#         if timeDelta_Window < 10:  # This is this time window
#             mps = -1
#         else:
        # We've sampled over n seconds worth of trackpoints, let's examine them.
        mps = (self.distance / timeDelta_Window)

        return mps
    
    def __str__(self):
        
        time = self.getTimeSpan() / 60
        units = "minutes"
        
        if (time >= 60): 
            time /= 60
            units = "hours"

        return """
Stopped between these points (d=%f):
%s
%s
Travelled %f metres in %d %s, %f metres per second.
Near %s""" % (self.tpFirst.distance(self.tpCurr), self.tpFirst, self.tpCurr, self.distance, time, units, self.getSpeed_window(), self.nearestWP)

#         print("distance between the two points is",  self.tpCurr.distance(self.tpLast))
#         print(self.tpFirst)
#         print(self.tpCurr)
    

class StopSpotter(object):
    """
    Takes a points from multiple calls to regpoint, and decides
    from the stream of points whether the person was stopped or not.
    """

    def __init__(self, fileOut):
        self.stop = None
        self.stops = []

        self.gpxOut = gpxWriter(fileOut)

        self.track = Track()

    def __str__(self):
        s = "%d stops:\n" % len(self.stops)
        for i, stop in enumerate(self.stops):
            s += "%d : %d seconds\n" % (i,  stop.getTimeSpan())
        s += "total : %d seconds" % self.stopTimeTotal()
        return s

    def stopTimeTotal(self):
        t = 0
        for stop in self.stops:
            t += stop.getTimeSpan()
        return t

    def stopTime(self):
        t = self.stop.getTimeSpan()
        if t is None:
            log.i("Why is t none?")
            t = -1
        return t

    def checkStopped(self, threshold=20):
        t = self.stopTime()
        if t > threshold:
            self.onStopped(self.stop, t)
        return t

    def onStopped(self, stop, t):
        # TODO write comment at the nearest place.
#       self.gpxOut.writeItem(WayPoint(copyFrom=self.stop.nearestWP, sym="dot", cmt="Nearest waypoint match"))
#        self.gpxOut.writeItem(WayPoint(copyFrom=stop.tpFirst, name="A: %ds @ %s" % (t, stop.tpFirst.timeStr()), sym="flag", cmt="Stopped near %s" % stop.nearestWP))
        self.gpxOut.writeItem(WayPoint(copyFrom=stop.tpFirst, name= "Stopped near %s : %ds @ %s" % (
        gpxUtil.name(stop.nearestWP), t, stop.tpFirst.timeStr()), sym="flag", cmt="Stopped near %s" % stop.nearestWP))

#       self.gpxOut.writeItem(WayPoint(copyFrom=self.stop.tpCurr, name="B: %ds @ %s" % (t, self.stop.tpCurr.timeStr()), sym="dot"))
        self.track.startSegment()

        self.stops.append(stop)

    def regPoint(self, trackpoint, nearestWP=None):
        """
        Return previous stop object
        """
        
        stop_ret = None

#        if trackpoint.lat == "51.508986857":
#            pass

        if not self.stop:
            self.stop = Stop(trackpoint, nearestWP)
        else:
#             print("On %s" % trackpoint)

            # TODO this should attempt to store the nearestWP if one hasn't been got yet
            # as we end up with stops without a nearest WP when there is one there somewhere
            # either on the first/mid/last 
            if not self.stop.setNextPoint(nearestWP, trackpoint):
                
                # This trackpoint is NOT yet added to a Stop.
                # Check if we need to print this stop as it is.
                self.checkStopped()

                # need to create a new stop with the last item in the current stop
                stop_ret = self.stop

                # We are favouring the first stops WP, so cope with the case where we get a big time and distance
                # jump. The "stop" was probably where we were, not where we are now..
                self.stop = Stop(self.stop.tpCurr, nearestWP)
#                self.stop = Stop(self.stop.tpCurr, self.stop.tpCurrWP)

                if not self.stop.setNextPoint(nearestWP, trackpoint, force=True):
                    t = self.checkStopped()

        self.track.addPoint(trackpoint)

        return stop_ret

    def done(self):
        self.gpxOut.writeItem(self.track)
        self.gpxOut.close()

###############################################################################


def main():
    print("Run some tests")

    ss = StopSpotter(sys.stdout)

    p = Point(50.1, 0.8)
    p.setTime("2015-03-08T18:07:24+00:00")
    td = datetime.timedelta(seconds=30)

    for i in range(100):
        px = Point(copyFrom=p, name=i)
        px.time_obj = p.time_obj + td
        ss.regPoint(px)
        p = px

    # Move 35 meters to the right
    p.move(STOP_TO_START_THRES * 2, 0)

    for i in range(100):
        px = Point(copyFrom=p, name=i)
        px.time_obj = p.time_obj + td
        ss.regPoint(px)
        p = px

    print(ss)

###############################################################################


if __name__ == "__main__":
    main()

