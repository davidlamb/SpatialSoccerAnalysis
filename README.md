# SpatialSoccerAnalysis
 This is a series of projects slowly building of StatsBomb's datasets. I am attempting to apply spatial analytic techniques and libraries to the problem of analyzing soccer information. This is entirely python based.
 
 These examples are provided as is with miminal support, although feedback and comments are welcome. These are basic examples and don't break down the match events in every possible way. They are meant to be a stepping stone to deeper analysis.
 

## Libraries
 *Required external libraries:*
 
 1. Pandas
 2. GeoPandas
 3. Shapely
 4. Matplotlib
 
 *Optional libraries:*
 
 1. Seaborn
 
## Dataset

The dataset used in these examples are pulled from StatsBomb's open datasets. As you can see I had trouble understanding the location information contained in their json event datasets. I found them counterintutive to how I typically view locations. I think I understand now, and appreciate their (assumed) reasoning behind it, but you'll see I play around with placement on the pitch.

 
## Python

The SpatialSoccer class in ssalib.py contains some scripts I preserved to make it easier to process the data repeatedly, or create the pitch. I will add to this as I move through my projects.

## Help

If you can, it would be helpful to find a video of the match you are interested in. These don't seem to be readily available, but it could really improve interpretation.