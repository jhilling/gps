#!/usr/bin/env python3

from __future__ import print_function

import sys
import errno

from xml.sax.handler import ContentHandler
import xml.sax

from gps.lib.logWriter import LogWriter

from gps.lib.primitives.points import WayPoint
from gps.lib.primitives.gpxSegments import Route

from gps.lib.formats.gpxWriter import gpxWriter

# TODO should the default action for this just be to spit out the (parsed) version as GPX? Think "cat".
# Then whatever overrides it will maintain the GPX except for what they choose to fiddle with?


# Note how we multi inherit here because ContentHandler is an old style class. Also
# inheriting from object means super will work on the subclasses
class osmParser(ContentHandler, object):
    """
    Parse an osm file

    Note that ContentHandler is an old style class, hence why we also
    inherit from object to allow compatibility with new style classes.
    """
    
    #def characters(self, ch):
        #sys.stdout.write(ch.encode("Latin-1"))

    def __init__(self):

        self.log = LogWriter()

        self.filename = None

        self.location = []
        self.attrs = None

        self.content = None

        self.fout = sys.stdout
        
        self.nodes = {}

    def run(self, filenames):
        """is this for compatibility?"""
        self.Parse(filenames)
    
    def startElement(self, name, attrs):

        self.location.append(name)
        self.attrs = attrs
        #print("At", self.location)

        # See also endElement where much of the action is.

        if self.location == ["osm", "node"]:
            # lat=None, lon=None, copyFrom=None, name=None, sym=None, cmt=None):
            self.wp = WayPoint(attrs['lat'], attrs['lon'])

            # Could be a route point!

            # osm node        
            self.nodes[attrs['id']]  = self.wp

        elif self.location == ["osm", "node", "tag"]:
            if attrs['k'] == "name":
                self.wp.name = attrs['v']
        
        elif self.location == ["osm", "meta"]:
            pass
        elif self.location == ["osm", "way"]:

            assert(self.wp is None)

            # We have to get the coordinates from the node references

            # Start a route
            self.route = Route()

        elif self.location == ["osm", "way", "nd"]:
            self.rp = self.nodes[attrs['ref']]
            self.route.addPoint(self.rp)
        elif self.location == ["osm", "way", "tag"]:
            if attrs['k'] == "name":
                self.route.name = attrs['v']
        else:
            pass
#            self.log.i("IGNORING START OF SECTION:%s" % self.location)

        self.content=None

    def characters(self, content):

        if self.content is None:
#            print("type first assign:", type(content))
            self.content = content
        else:
#            print("add type to content", type(content))
            
            # Remember content is not complete!!
            self.content += content

    def endElement(self, name):
        
        if self.content:
#            print("have full content of type", type(self.content), self.content)
            content = self.content.strip()
#            content = self.content.strip().encode('ascii', 'ignore')  # this screws up on python3
#            print("have full content ENCODED of type", type(content), content)
        else:
            content = None
            
        # Handle the content

        if self.location == ["osm", "node"]:
            self.nextWayPoint(self.wp)
            self.wp = None

        elif self.location == ["osm", "meta"]:
            pass
        elif self.location == ["osm", "node", "tag"]:
            pass
        elif self.location == ["osm", "way"]:
            self.nextRoute(self.route)
            self.route = None
        elif self.location == ["osm", "way", "nd"]:
            self.nextRoutePoint(self.rp)
        elif self.location == ["osm", "way", "tag"]:
            pass
        else:
            pass
#            self.log.i("IGNORED: %s, content: %s" % (self.location, content))

        self.content = None

        self.location.pop()

    def endDocument(self):
        pass
        #if self.opts.print_summary:
            #self.track.PrintStats()

    def nextFile(self, filename):
        self.filename  = filename

    def Parse(self, files):
        parser = xml.sax.make_parser()
        parser.setContentHandler(self)

        self.start()
        
        for f in files:

            # Create a new analyzer to each time so values from previous file not used
            # This is the object we will register the trackpoints with
            try:
                self.nextFile(f)
                parser.parse( f )

            except IOError as e:
                
                (err_number, strerror) = e.args

                if err_number == errno.EPIPE:
                    # this happens when piped into head, for example
                    pass
                else:
                    self.log.i("IOError occured parsing file")
                    self.log.i(strerror)
            #except ValueError, e:
            #    self.log..i("Value Error exception caught:", e

        self.end()

##########################################

    # These are designed to be overridden

    def start(self):
        pass

    def haveBounds(self, bounds):
        """This is the bounds of the file, before much processing has happened.
        The idea being that you can abort early if not bounds not in range."""
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
        pass


class osmParserX(osmParser):
    
    def start(self):
        self.log.i("start")

    # Overrides for derived classes
    def nextTrack(self, track):
        self.log.i("TRACK: %s" % track.name)

    def nextTrackSegment(self, segment):
        self.log.i("track segment")

    def nextTrackPoint(self, trackPoint):
        self.log.i("track point")

    def nextRoute(self, route):
        self.log.i("ROUTE: %s" % route.name)

    def nextRoutePoint(self, routePoint):
        self.log.i("route point")

    def nextWayPoint(self, wayPoint):
        self.log.i("WAYPOINT: %s" % wayPoint.name)

    def end(self):
        self.log.i("end") 


class osmGpxWriter(osmParser):
    
    def __init__(self, outputFile):
        super(osmGpxWriter, self).__init__()
        self.gpx = gpxWriter(outputFile)

    def netLatLon(self, route):
        """
        Try and return the centre
        """
        point = route.centre()
        return point.lat, point.lon

    def nextRoute(self, route):
#        self.log.i("ROUTE: %s" % route.name)
        
        # need to generate a single new waypoint for the route and write that instead

        if not route.name:
#            self.log.i("Skipping no name route: " + str(route))
#            route.name = "(No name in OSM data)"
            return

        wp = WayPoint(name=route.name)
        wp.lat, wp.lon = self.netLatLon(route)
        
        self.gpx.writeItem(wp)

    def nextRoutePoint(self, routePoint):
        #self.log.i("route point")
        pass

    def nextWayPoint(self, wayPoint):
#        self.log.i("WAYPOINT: %s" % wayPoint.name)
        
        if wayPoint.name:
            self.gpx.writeItem(wayPoint)

    def end(self):
        self.gpx.close()
        
###############################################################################


if __name__ == "__main__":
    
#    app = osmParserX()
    app = osmGpxWriter(sys.stdout)

    app.run(sys.argv[1:])
