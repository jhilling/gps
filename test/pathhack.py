#!/usr/bin/env python

# Add self directory to pythonpath so packages can be found

import sys
import os
s = os.path.split(os.path.abspath(__file__))[0]
s = os.path.split(s)[0]
sys.path.append(s)

if __name__ == "__main__":
    print(s)
