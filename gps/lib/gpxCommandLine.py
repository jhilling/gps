#!/usr/bin/env python

from __future__ import print_function

import sys
import optparse

from gps.lib import gpxUtil

"""
Provide a standardized command line for the different gpx modules
"""


class clInterfaceBase(object):

    """
    Enable use to easily create command line interface to the
    gpxstat modules, for testing etc
    """

    def __init__(self):
        self.p = optparse.OptionParser(self.usage())
        self.p.epilog = self.eplilog()
        self.setDefaults()
        self.addOptions()

    def usage(self):
        return "Usage: %prog [options] [file] ..."

    def addOptions(self):
        self.addOption('--verbose', '-v', action='store_true', help="be more verbose")

    def eplilog(self):
        return None

    def get(self, argv=sys.argv[1:]):
        options, args = self.p.parse_args(argv)
        return options, args

    def setDefaults(self):
        self.setDefaultValues(verbose=False)

    def setDefaultValues(self, **kwargs):
        self.p.set_defaults(**kwargs)

    def addOption(self, *args, **kwargs):
        self.p.add_option(*args, **kwargs)


###############################################################################


class OptionsGPX(clInterfaceBase):
    """
    Standard command line interface
    TODO we're not always printing!
    """
    def addSummary(self, default=False):
        self.addOption('--summary', '-s', action='store_true', default=default, help="print summary information", dest="print_summary")
        return self

    def addTotal(self, default=False):
        self.addOption('--total', '-T', action='store_true', default=default, help="print total information", dest="print_total")
        return self

    def addTrackpoints(self, default=False):
        self.addOption('--trackpoints', '-t', action='store_true', default=default, help="print trackpoints", dest="print_trackpoints")
        return self

    def addWaypoints(self, default=False):
        self.addOption('--waypoints', '-w', action='store_true', default=default, help="print waypoints", dest="print_waypoints")
        return self

    def addRoutes(self, default=False):
        self.addOption('--routes', '-r', action='store_true', default=default, help="print routes", dest="print_routes")
        return self

    def addOutputDirectory(self, default=None):
        self.addOption('--output', '-d', action='store', default=default, help="output directory", dest="output_directory")
        return self
    
    def addThresholds(self,
                      lower=gpxUtil.interpolate_thres_lower_metres,
                      upper=gpxUtil.interpolate_thres_upper_metres):
        self.addOption('--lower', '-l', type="int", action='store', default=lower, help="lower threshold")
        self.addOption('--upper', '-u', type="int", action='store', default=upper, help="upper threshold")
        return self

    def parse(self, argv=sys.argv[1:]):
        self.opts, self.args = self.get(argv)
        return self.opts, self.args

###############################################################################


def main():

    op = OptionsGPX()
    op.addSummary().addTrackpoints().addOutputDirectory("bob").addThresholds()

    options, args = op.parse() 

    print("Options:")
    print(options)

    print("Args:")
    print(args)

###############################################################################

if __name__ == "__main__":
    main()
