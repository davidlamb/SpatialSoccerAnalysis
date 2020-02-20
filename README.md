# SpatialSoccerAnalysis
 This is a series of projects slowly building of StatsBomb's datasets. I am attempting to apply spatial analytic techniques and libraries to the problem of analyzing soccer information. This is entirely python based.
 
 These examples are provided as is with miminal support, although feedback and comments are welcome. These are basic examples and don't break down the match events in every possible way. They are meant to be a stepping stone to deeper analysis.
 
[Project 1](1_BuildPitch.md)
  - In this project I look at creating the pitch based on the coordinates provided in StatsBomb's documentation. This creates the first geopandas dataframe. I also begin to look at how to interpret location and the problems I encountered from a cartesian coordinate \ geographic perspective. This does not mean problems with the data itself.
[Project 2](2_ParsingJSON.md)
  - This project builds of the first project and introduces the ssalib.py file. I look at parsing the data and building basic dataframes from the JSON. THis includes building some GeoDataFrames to plot on the pitch. Really just starting to get comfortable with the event data.
[Project 3](3_ProcessingTimeAttributes.md)
  - One of my goals is to explore building spatial trajectories from the events. To do this I want to have a datetime object to work with. From that I can query based on time, or calculate timedeltas more easily. Or at least in a way I understand to calculate them. This looks at building time objects within the GeoDataFrame and some basic queries based on time. These become integrated in the SpatialSoccer class in ssalib.py.
[Project 4](4_BuildingTriangles.md)
  - This branches off a bit from trajectories to look at Delaunay Triangulation (something I have used a lot in space-time analysis) and voronoi diagrams. This was more of an experimental project. The ideas were pulled from David Sumpter's soccermatics book. As are some of the other project ideas.
[Project 5](5_PassandCarries.md)
  - This is the first look at "trajectories" in a sense, but without the time associated with them. Again some of the ideas are pulled from Soccermatics, looking at average pass lengths and average pass directions. This adds a grid overlay or fishnet to the SpatialSoccer class for processing averages over the pitch. I also look at some social network analysis applied to pass connections.
Project 6
 - Full look at developing trajectories from the StatsBomb data. Not yet uploaded.

## Libraries
 *Required external libraries:*
 
 1. Pandas
 2. GeoPandas
 3. Shapely
 4. Matplotlib
 
 *Optional libraries:*
 
 1. Seaborn
 2. Networkx
 
## Dataset

The dataset used in these examples are pulled from StatsBomb's open datasets. As you can see I had trouble understanding the location information contained in their json event datasets. I found them counterintutive to how I typically view locations. I think I understand now, and appreciate their (assumed) reasoning behind it, but you'll see I play around with placement on the pitch.

- [Github statsbomb](https://github.com/statsbomb/open-data)
- [StatsBomb Signup](https://statsbomb.com/resource-centre/)
- [StatsBomb R package](http://statsbomb.com/wp-content/uploads/2019/07/Using-StatsBomb-Data-In-R_up.pdf) <- one of the required packages is no longer in the R repository? The presentation is helpful to see how some analysis can be done.
- [StatsBomb Messi](https://statsbomb.com/2019/07/messi-data-release-part-1-working-with-statsbomb-data-in-r/)
- [StatsBomb in Use](https://statsbomb.com/2019/05/statsbomb-data-one-year-on/)

## Python

The SpatialSoccer class in ssalib.py contains some scripts I preserved to make it easier to process the data repeatedly, or create the pitch. I will add to this as I move through my projects.

## Help

If you can, it would be helpful to find a video of the match you are interested in. These don't seem to be readily available, but it could really improve interpretation.
