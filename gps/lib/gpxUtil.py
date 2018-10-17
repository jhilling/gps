#!/usr/bin/env python

import os
import tempfile

interpolate_thres_lower_metres=50 # do not return points closer together than this
interpolate_thres_upper_metres=100 # for gaps bigger than this, return interpolated points


def utf8(content):
    try:
        s = content.encode('UTF-8')
#         print("encoded as utf8")
        return s 
    except:
#         print("encoded as str")
        return str(content)


def SafeVal(x, defaultv="-"):
    if x is None:
        return defaultv
    else:
        return utf8(x)


def distance(metres):
    """Return display string for distance"""
    miles = 0.62137119
    return "%.1f km|%.1f mi" % (metres/1000, metres/1000 * miles)


def elevation(metres):
    """Return display string for elevation"""
    feet = 3.2808399
    return "%.1f m|%.1f ft" % (metres, metres * feet)


def area(a):
    return "%.1f square kms" % ((a.width() / 1000.0) * (a.height() / 1000.0))


def width_height(wh):
    return "%.1f kms x %.1f kms" % (wh.width() / 1000.0, wh.height() / 1000.0)


def tempFilePath(filename, subdir="gpxscripts"):
    path = os.path.join(tempfile.gettempdir(), subdir)
    try: os.makedirs(path)
    except: pass
    
    if filename:
        path = os.path.join(path, filename)

    #if os.path.exists(path):
    #    print("temp file already exists " + path)

    return path


def name(pt):
    if pt:
        return pt.name
    else:
        return "Unknown"


def duration(d_seconds):
    d_minutes = d_seconds/60.0
    return "%.1f minutes" % d_minutes




###############################################################################

if __name__ == "__main__":
    import sys
    print("%s: I don't do anything standalone" % sys.argv[0])


