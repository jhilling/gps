
###TODO

MetaPrinter doesn't tell you the speed!!
	would be good if it gave you average speed in terms
	of track segments. 
	maybe gpx2txt could print average speed between landmarks.


make sure the osm caching (+ others?) will cope when the data is shared across containers
e.g. write to a temporary name and move when complete etc

see snapcraft.. create a snap for this project?


print for 1st point after a long stop - WIP


run all doctests from makefile

move source into packages - WIP
how run from command line?

Some kind of test to at least run every script with a known file


Can I use @ notation for the decorator stuff somewhere
Note this is not run time decoration
replaces 

syntactic sugar for this:

@dec
def bob():
    pass

bob = dec(bob)



Format strings like this: "I am {0}, what did you think?".format(self.age + lie)

write some scripts to get the webserver into docker

Would be good to be able to have some unit tests or pseudo unit tests
testing against known output.


print time units properly not decimally

##idea
###There's no place like ~
Remove home from gpx tracks

Auto-find home by scanning tracks and looking at start/end points of each track
This could then write a "home" waypoint somewhere which the other scripts could
recogize and do the right thing with it.
