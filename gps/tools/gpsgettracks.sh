#!/bin/bash

# James Hilling

# This is what I used to extract gps data from my 
# Garmin (using gpsbabel), split the data up and tell me (in words)
# something about it using my python scripts

# It requires some of the python scripts to be available
# on the path. TODO rudimentary setup for this.
# Should really be a python script for compatibility...


# This will list all connected garmins 
# gpsbabel -t -i garmin -f usb:-1 # | cut -f 1,4 -d " "
# could use this to handle multiple devices, e.g. currently
# can't upload from 2 devices on the same day due to the
# caching of the days gps log.

# gpxviewer gpsprune
: ${VIEWER="gpsprune"}

set -e

if ! which "gpsbabel" >& /dev/null ; then
  echo "No gpsbabel found - please install it."
  exit 1
fi

OUTDIR="$HOME/GPS_Tracks"
mkdir -p "$OUTDIR"

echo "Get and view latest track from GPS.  Output to $OUTDIR"

cd "$OUTDIR"

OUTFILE="$OUTDIR/$(date +%Y%m%d).gpx"
LOGFILE=/tmp/gpsbabel.out

if [ -s "$OUTFILE" -a "$1" == "-f" ] ; then
    # Force fetch from the gps
    OUTFILE="$OUTDIR/$(date +%Y%m%d-%s).gpx"
fi

if [ -s "$OUTFILE" ] ; then
	echo "Already have the file from the GPX for today, skip fetching it again. Use -f to override."
else
	for ((i = 0; i < 5 ; i++))
	do
		echo "Extract tracks attempt $i, logging to $LOGFILE.$i"
		gpsbabel -t -i garmin -f usb: -o gpx,garminextensions -F "$OUTFILE" > "$LOGFILE.$i" 2>&1

		if [ "$(grep -c ERROR "$LOGFILE.$i")" -gt 0 ] ; then
			echo "extract, failed"
			rm "$OUTFILE"
			sleep 2
		else
			echo "GPS data appeared to have been extracted successfully"
			break
		fi
	done
fi

# This will file away the result in a neat directory structure
gpxsplit "$OUTFILE"

# TODO the following is now broken as we don't know where the track
# was written to!!

# Print a description of the track
 
# Choose file, or automatically choose the last one?

CHOICE=$(ls "$OUTDIR/Repository/tracks/$(date +%Y)"/*.GPX | tail -1)

# Create an alias for convenience on the command line
ln -sf "$CHOICE" "$OUTDIR/Repository/tracks/$(date +%Y)/current.GPX"

#IFS=$'\n'
#select CHOICE in $(ls *.GPX | sort -r | head)
#do 
#	echo $CHOICE
#	break
#done

echo "Track summary:"
gpx2txt -- "$CHOICE" 2> /tmp/gpx2txt.stderr &


echo "Viewing $CHOICE" 

if [ -n "$CHOICE" ] ; then
	"$VIEWER" "$CHOICE" &
fi

