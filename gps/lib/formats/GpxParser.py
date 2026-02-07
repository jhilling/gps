#!/usr/bin/env python



import sys
import errno

from xml.sax.handler import ContentHandler
import xml.sax

from gps.lib.logWriter import LogWriter

from gps.lib.primitives.points import Trackpoint, RoutePoint, WayPoint, Point

from gps.lib.primitives.gpxBounds import Bounds

from gps.lib.primitives.gpxSegments import Route, Track

from gps.lib.gpsObserver import GpxObserverPrint

"""

Parse a gpx file, calling out to the registered Observers for each 
gpx item parsed

See design pattern Observer (aka Event Listener) design pattern.
https://en.wikipedia.org/wiki/Observer_pattern

"""


# Note how we multi-inherit here because ContentHandler is an old style class. Also
# inheriting from object means super will work on the subclasses
class GpxParser(ContentHandler, object):
    """
    Parse a gpx file, and either call a callback for each tp parsed
    (if cb supplied) or just works out some stats on the tps read.
    
    Note that ContentHandler is an old style class, hence why we also
    inherit from object to allow compatibility with new style classes.
    """
    
    #def characters(self, ch):
        #sys.stdout.write(ch.encode("Latin-1"))

    # observers should "implement" GpxObserver
    def __init__(self, observers=None):
        super(GpxParser, self).__init__()

        self.log = LogWriter()

        self.track = None

        # The trackpoint we will build up        
        self.tp = None
        self.tp_cb = None

        self.location = []
        self.attrs = None

        self.content = None

        self.fout = sys.stdout

        if observers:
            try:
                # Ensure observers is iterable
                iter(observers)
                self.observers = observers
            except TypeError:
                # Not iterable
                self.observers = [observers]
        else:
            self.observers = [GpxObserverPrint(self.log)]

    def run(self, filenames):
        self.Parse(filenames)

    def startElement(self, name, attrs):

        self.location.append(name)
        self.attrs = attrs
        #print("At", self.location)

        # See also endElement where much of the action is.

        if self.location == ["gpx", "trk"]:
            self.track = Track()

        elif self.location == ["gpx", "trk", "trkseg"]:
            self.track.startSegment()

        elif self.location == ["gpx", "trk", "trkseg", "trkpt"]:
            self.tp = Trackpoint(attrs.get("lat"), attrs.get("lon"))

        elif self.location == ["gpx", "wpt"]:
            self.wayPoint = WayPoint(attrs.get("lat"), attrs.get("lon"))

        elif self.location == ["gpx", "rte"]:
            self.route = Route()

        elif self.location == ["gpx", "rte", "rtept"]:
            self.rp = RoutePoint(attrs.get("lat"), attrs.get("lon"))
        else:
            
            pass
            #self.log.i("IGNORING START OF SECTION:%s" % self.location)

        self.content=None

    def characters(self, content):

        if self.content is None:
#            print("type first assign:", type(content))
            self.content = content
        else:
#            print("add type to content", type(content))
            
            # Remember content is not complete!!
            self.content += content

    def selectObj(self):
        obj = None
        if len(self.location) >= 2:

            if self.location[:4] == ["gpx", "trk", "trkseg", "trkpt"]:
                obj = self.tp
            else:
                top_level = self.location[1]
                if top_level == "trk":
                    obj = self.track
                elif top_level == "wpt":
                    obj = self.wayPoint
                elif top_level == "rte":   
                    obj = self.route

        return obj

    def endElement(self, name):
        
        if self.content:
#            print("have full content of type", type(self.content), self.content)
            content = self.content.strip()
#            content = self.content.strip().encode('ascii', 'ignore')  # this screws up on python3
#            print("have full content ENCODED of type", type(content), content)
        else:
            content = None
            
        obj = self.selectObj()

        # Handle the content

        if self.location[:2] == ["gpx", "trk"]:
            if self.location == ["gpx", "trk"]:
                [observer.nextTrack(self.track) for observer in self.observers]
                self.track = None

            elif self.location == ["gpx", "trk", "name"]:
                obj.name = content
 
            elif self.location == ["gpx", "trk", "type"]:
                obj.type = content

            elif self.location == ["gpx", "trk", "trkseg"]:
                [observer.nextTrackSegment(self.track.currentSegment) for observer in self.observers]
                self.track.endSegment()

            elif self.location == ["gpx", "trk", "trkseg", "trkpt"]:
                self.track.addPoint(self.tp)
                [observer.nextTrackPoint(self.tp) for observer in self.observers]
                self.tp = None

            elif self.location == ["gpx", "trk", "trkseg", "trkpt", "extensions", "gpxtpx:TrackPointExtension", "gpxtpx:hr"]:
                self.tp.hr = int(content)

            elif self.location == ["gpx", "trk", "trkseg", "trkpt", "extensions", "gpxtpx:TrackPointExtension", "gpxtpx:cad"]:
                self.tp.cad = int(content)

            elif self.location == ["gpx", "trk", "trkseg", "trkpt", "time"]:
                
#                print("yContent is type", type(content))
#                print("yContent value is", content)
            
                self.tp.setTime(content)
                
            elif self.location == ["gpx", "trk", "trkseg", "trkpt", "ele"]:
                if content:
#                    print("xContent is type", type(content))
#                    print("xContent value is", content)
                    self.tp.elevation = float(content)

        elif self.location[:2] == ['gpx', 'wpt']:

            if self.location == ['gpx', 'wpt']:
                [observer.nextWayPoint(self.wayPoint) for observer in self.observers]
                self.wayPoint = None

            elif self.location == ["gpx", "wpt", "name"]:                
                obj.name = content
                
            elif self.location == ["gpx", "wpt", "cmt"]:                
                obj.comment = content
            else:
                pass

        elif self.location[:2] == ['gpx', 'rte']:
            if self.location == ['gpx', 'rte']:
                [observer.nextRoute(self.route) for observer in self.observers]
                self.route = None

            elif self.location == ['gpx', 'rte', 'name']:
                self.route.name = content

            elif self.location == ["gpx", "rte", "rtept"]:
                self.route.addPoint(self.rp)
                [observer.nextRoutePoint(self.rp) for observer in self.observers]

            elif self.location == ["gpx", "rte", "rtept", "sym"]:
                self.rp.sym = content

            elif self.location == ["gpx", "rte", "rtept", "type"]:
                self.rp.type = content

        elif self.location == ['gpx']:
            pass
        elif self.location == ["gpx", "metadata", "bounds"]:
            minlat = self.attrs.getValue("minlat")
            minlon = self.attrs.getValue("minlon")
            maxlat = self.attrs.getValue("maxlat")
            maxlon = self.attrs.getValue("maxlon")
            
            bounds = Bounds()
            bounds.registerPoint(Point(minlon, minlat))
            bounds.registerPoint(Point(maxlon, maxlat))

            [observer.haveBounds(bounds) for observer in self.observers]

        elif self.location[:2] == ["gpx", "metadata"]:
#         elif self.location == ["gpx", "metadata", "time"]:
            pass
        else:
            self.log.i("IGNORED: %s, content: %s" % (self.location, content))

        self.content = None

        self.location.pop()

    def endDocument(self):
        pass
        #if self.opts.print_summary:
            #self.track.PrintStats()

    def Parse(self, files):

        if not isinstance(files, (list, tuple)):
            files = [files]

        parser = xml.sax.make_parser()
        parser.setContentHandler(self)

        [observer.start() for observer in self.observers]

        for f in files:

            # Create a new analyzer to each time so values from previous file not used
            # This is the object we will register the trackpoints with
            try:
                [observer.nextFile(f) for observer in self.observers]

                with open(f, 'r') as file_handle:
                    parser.parse(file_handle)

            except IOError as e:

                try:
                    (err_number, strerror) = e.args
                    if err_number == errno.EPIPE:
                        # this happens when piped into head, for example
                        continue
                except:
                    pass

                self.log.i("IOError occurred parsing file")
                self.log.i(e)
                raise e

            #except ValueError, e:
            #    self.log..i("Value Error exception caught:", e

        [observer.end() for observer in self.observers]


###############################################################################


if __name__ == "__main__":

    app = GpxParser()
    app.run(sys.argv[1:])
