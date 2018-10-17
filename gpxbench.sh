#!/bin/bash


TEST=gpx2txt

RESULT_ROOT="."
RESULT_BASE="$RESULT_ROOT/BENCHMARKS"
mkdir -p "$RESULT_BASE"

RESULT_FILE="$RESULT_BASE/$(hostname)_$TEST.bench"



#echo $(date +%Y%m%d-%H-%M-%S) 

echo "*** START ***" >> "$RESULT_FILE"
date >> "$RESULT_FILE"

/usr/bin/time -f '\n%C\n\nELAPSED: %e' --append --output="$RESULT_FILE" "$TEST" "$HOME/GPS_Tracks/Bench/"*.gpx -- "$HOME/GPS_Tracks/Bench/trk 2012-10-17 18-09-47-0 - 6.GPX" > /dev/null 2>&1

echo "rc=$?" >> "$RESULT_FILE"

grep "ELAPSED" "$RESULT_FILE" | tail -10
