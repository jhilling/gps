#!/usr/bin/env python
import sys


class LogWriter(object):

    def __init__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    # Write to stdout etc
    def o(self, msg):
        self.stdout.write(str(msg) + "\n")

    def oN(self, msg):
        self.stdout.write(str(msg))

    def i(self, msg):
        self.stderr.write(str(msg) + "\n")

    def n(self, msg):
        self.stderr.write(str(msg))

    def dbg(self, msg):
        self.stderr.write(str(msg) + "\n")
        pass

    def e(self, msg):
        self.stderr.write(str(msg) + "\n")


if __name__ == "__main__":
    print("%s: I don't do anything standalone" % sys.argv[0])
