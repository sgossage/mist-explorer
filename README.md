#WIP

# Isochrone Explorer
This is a bokeh app used to examine isochrones on a color-magnitude 
diagram (CMD). Various parameters (age, metallicity, and rotation rate of the 
stars) can be manipulated. Developed with Python 3.6.1.

# Requires

* A set of MIST/MESA style isochrones (http://waps.cfa.harvard.edu/MIST/). 
  The intended set is not publically available at the moment, but will be 
  in the future.
* A modded version of Jieun Choi's MIST_codes 
  (https://github.com/jieunchoi/MIST_codes).
* Aaron Dotter's iso code: https://github.com/dotbot2000/iso

# Run Command
Execute with e.g. bokeh serve mist-explorer.py

Or, using optional commands:

bokeh serve mist-explorer.py --args -pf path/to/a_photometry.file -ps UBVRIplus

Optional args:

...

# Planned Features

TBA
