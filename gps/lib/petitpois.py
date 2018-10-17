#!/usr/bin/env python

"""
A little Point Of Interest fetcher (poi == Point Of Interest).

Uses the Openstreetmap Overpass API to fetch the POI from the web
and caches the data locally.

"""

from __future__ import print_function

import tempfile
import os
import sys
import urllib2
import hashlib
import gps.tools.osm2gpx

from gps.lib.primitives.gpxBounds import Bounds
from gps.lib.primitives.points import Point


def tempDir():
    dir = os.path.join(tempfile.gettempdir(), "poi_cache")
    os.path.isdir(dir) or os.makedirs(dir)
    return dir


def repoDir():
    dir = os.path.join(os.path.expanduser('~'), "GPS_Tracks/osm")
    os.path.isdir(dir) or os.makedirs(dir)
    return dir


def cacheFilename(url, dir, extn):
    """
    base cache file on hash of the url
    """
    h = hashlib.md5()
    h.update(url)

    fn = h.hexdigest()

    if extn:
        fn += extn

    return os.path.join(dir, fn)


def cachedFetch(url, useCache=True):

    full_path = os.path.join(dir, cacheFilename(url, tempDir(), ".osm"))

    if useCache and os.path.exists(full_path):
        print("Using cached", full_path, file=sys.stderr)
    else:
        try:
            req = urllib2.Request(url)
            print("Requesting", url, file=sys.stderr)

            f = urllib2.urlopen(req)

            html = f.read()

            with open(full_path, "w") as f:
                for line in html:
                    f.write(line)
            
        except:
            print("Failed to retrieve", url, file=sys.stderr)
            raise

    return full_path


def qs(type, key, value, bottom, left, top, right):
    """
    Partial query string
    """
    return '%s["%s"="%s"](%s,%s,%s,%s);' % (type, key, value, bottom, left, top, right)


def makeUrl(bltr):
    q = []
    q.append(qs("way",  "amenity", "pub", *bltr))
    q.append(qs("node", "amenity", "pub", *bltr))
#    q.append(qs("way", "highway", "primary", *bltr))

    urlRaw = "(%s);(._;>;);out meta;" % ("".join(q))
    url = "http://overpass-api.de/api/interpreter?data=" + urllib2.quote(urlRaw)
    
    return url


def fetchPoi_osm(bltr, useCache):
    """
    urlRaw = '(way["amenity"="pub"](51.4376,-0.9419,51.5113,-0.7951); node["amenity"="pub"](51.4376,-0.9419,51.5113,-0.7951););(._;>;);out meta;'
    url = "http://overpass-api.de/api/interpreter?data=" + urllib2.quote(urlRaw)
    """
    print("Fetching pois for", bltr)
    url = makeUrl(bltr)

    fout = cachedFetch(url, useCache)

    return fout


def fetchPoi_gpx(bltr, useCache):
    """
    Return the osm in gpx format, but converting the raw osm values
    """
    # get the url
    url = makeUrl(bltr)

    # Check if we have already generated a gpx for this url
    gpx = cacheFilename(url, repoDir(), ".gpx")

    if useCache and os.path.exists(gpx):
        return gpx

    osm = fetchPoi_osm(bltr, useCache)

    print("Writing", gpx, file=sys.stderr)
    with open(gpx, "w") as fout:
        gpxWriter = gps.tools.osm2gpx.osmGpxWriter(fout)
        gpxWriter.Parse([osm])

    return gpx;


class FetchPoi(object):
    """
    Keep track of which segments have already been done
    and don't return them again
    """

    def __init__(self, useCache=True):
        self.done = set()
        self.useCache = useCache

    def fetchPoi_gpx_split(self, bottom, left, top, right):
        """Fetch the pois in segments"""
    
        bounds = Bounds()
        bounds.registerPoint(Point(bottom, left))
        bounds.registerPoint(Point(top, right))

        for bltr in bounds.split():
            if bltr in self.done:
#                print("skipping****************************************************************************", bltr)
                pass
            else:
                self.done.add(bltr)
                yield fetchPoi_gpx(bltr, self.useCache)


if __name__ == "__main__":

    bltr = ("51.4376", "-0.9419", "51.5113", "-0.7951")

    try:
        if len(sys.argv) > 1:
            bltr = sys.argv[1:5]
    except:
        print("Error parsing arguments, using test arguments", file=sys.stderr)

    fout = fetchPoi_gpx(bltr, True)

    # Output of the script is the filename post processing in scripts etc
    print(fout);
