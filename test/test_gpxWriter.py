#!/usr/bin/env python

import pathhack

import os

import unittest

from gps.lib.formats.gpxWriter import gpxWriter


class Test_gpxWriter(unittest.TestCase):

    def test_normal(self):
        """Test file that doesn't already exist (normal case)"""
        tf = "wibble"

        try:
            os.remove(tf)
        except OSError as e:
            pass
        g = gpxWriter(tf)
        self.assertIsNotNone(g)
        os.remove(tf)

    def test_default(self):
        """Test no file supplied (default to stdout)"""
        g = gpxWriter()
        self.assertIsNotNone(g)

    def test_none(self):
        """Test none supplied, which is an error"""
        g = gpxWriter(None)
        self.assertIsNone(g)

    def test_too_many(self):
        """Test too many args supplied, which is an error"""
        self.assertRaises(TypeError, gpxWriter, "wibble", "wobble")


if __name__ == '__main__':
    unittest.main()
