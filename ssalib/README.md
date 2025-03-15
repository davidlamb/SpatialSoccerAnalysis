# Spatial Soccer Analysis Library
 
 Simple python-based class for loading, parsing, and working with Statsbomb, Wyscout, and Metrica open data sources. ssalib2 revised the previous class so it was more flexible with other types of event based and tracking based data.
 
 Several examples using ssalib are available in the projects folder.
 
 ## Libraries
 *Required external libraries:*
 
 1. Pandas
 2. GeoPandas
 3. Shapely
 4. Matplotlib
 
 *Optional libraries:*
 
 1. Seaborn
 2. Networkx
 
 
 ## Examples using ssalib2
 
 [Updated ssalib2](../projects/_RevisedSpatialSoccerLibrary.md)
- I hit the limit of my working ssalib python library pretty quickly. I wanted to also work with wyscout data, and the way I set up the original library wasn't well tailored to working across different data sources. Now, I have ssalib2 that abstracts some of the importing to classes for matches and events. I leave ssalib there to work with the older previous projects.

 [Alternatives to Visualizing Pass Maps](../projects/8_VisualizingPassNetworks.md)
  - In this project I present some alternatives to the flow map style passing network visuals, including sankey diagrams and heat maps.
  
 [Inferring player locations from event data](../projects/9_InferringLocationFromEventData.md)
  - This project explores using a Potential Path Areas (a common tool from Time Geography) to understand where a player was in the field during an event. In other words, inferring a player's location prior to the event given their speed and a time interval.


 ## Examples using old version:
 
 [Project 1](../projects/1_BuildPitch.md)
  - In this project I look at creating the pitch based on the coordinates provided in StatsBomb's documentation. This creates the first geopandas dataframe. I also begin to look at how to interpret location and the problems I encountered from a cartesian coordinate \ geographic perspective. This does not mean problems with the data itself.
  
[Project 2](../projects/2_ParsingJSON.md)
  - This project builds of the first project and introduces the ssalib.py file. I look at parsing the data and building basic dataframes from the JSON. THis includes building some GeoDataFrames to plot on the pitch. Really just starting to get comfortable with the event data.
  
[Project 3](../projects/3_ProcessingTimeAttributes.md)
  - One of my goals is to explore building spatial trajectories from the events. To do this I want to have a datetime object to work with. From that I can query based on time, or calculate timedeltas more easily. Or at least in a way I understand to calculate them. This looks at building time objects within the GeoDataFrame and some basic queries based on time. These become integrated in the SpatialSoccer class in ssalib.py.
  
[Project 4](../projects/4_BuildingTriangles.md)
  - This branches off a bit from trajectories to look at Delaunay Triangulation (something I have used a lot in space-time analysis) and voronoi diagrams. This was more of an experimental project. The ideas were pulled from David Sumpter's soccermatics book. As are some of the other project ideas.
  
[Project 5](../projects/5_PassandCarries.md)
  - This is the first look at "trajectories" in a sense, but without the time associated with them. Again some of the ideas are pulled from Soccermatics, looking at average pass lengths and average pass directions. This adds a grid overlay or fishnet to the SpatialSoccer class for processing averages over the pitch. I also look at some social network analysis applied to pass connections.
  
[Project 6 Draft](../projects/6_UnderstandExploringPossession.md)
 - I guess all of these should really be considered drafts. With this one I am still working through some of it, but thought I would upload it. In this document, I am looking to understand StatsBomb's possession variable. I also develop the convex hull of player possession similar to what is briefly described in Soccermatics.
 
 
