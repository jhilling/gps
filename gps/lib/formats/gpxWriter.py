#!/usr/bin/env python

"""

If get:
UnicodeEncodeError: 'ascii' codec can't encode character u'\\u2019' in position 54: ordinal not in range(128)

Do this if getting errors redirecting output to a file:
export PYTHONIOENCODING=utf-8
"""



import os
import sys

from gps.lib.gpxXml import Xml

jxml = Xml()


def gpxWriter(*names):
    """
    Factory to create the actual writer to make it less likely to accidentally overwrite existing files
    """

    if len(names) == 0:
        return gpxWriterImpl(sys.stdout)
    elif len(names) == 1:
        name = names[0]

        if not name:
            return None

        if hasattr(name, "write"):
            # Maybe we have a file like object
            return gpxWriterImpl(name)
        else:
            if os.path.exists(name):
                # Do not obliterate existing files
                return None
            else:
                gpxWriterImpl(open(name, "w"))

        return gpxWriterImpl(open(name, "w"))
    else:
        raise TypeError("Only expecting 0 or 1 arguments")

    return None


class gpxWriterImpl(object):

    def __init__(self, fout):
        self.fout = fout
        self.done_header = False

    def _writeHeader(self):

        if self.done_header or not self.fout:
            return False

        # TODO this should only write out the extensions header if the file contains extensions
        # This could be tricky though, as we don't know at the point of writing the header what
        # tracks are coming up, so don't know if the contain the extensions or not.

        self.fout.write("""<?xml version="1.0" encoding="UTF-8"?>
<gpx
 version="1.1" 
 creator="gpxtools"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns="http://www.topografix.com/GPX/1/1"
 xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
 xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
 xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
""")
        self.done_header = True

        return True

    def close(self):

        if self.done_header:
            self.fout.write(jxml.ee("gpx"))

        self.fout = None

    def writeItem(self, obj):

        self._writeHeader()

        """Just try and call an objects gpxWrite method TODO it shouldn't work like this"""
        obj.gpxWrite(self.fout)


if __name__ == "__main__":
    import sys
    print("%s: I don't do anything standalone" % sys.argv[0])
