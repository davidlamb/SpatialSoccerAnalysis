# Network Maps

Passing network maps are quite common. These are essentially graphs where each node is placed at a player's given position (ideal location or average positioning), and the edges are weighted by the number of passes between them. There may be direction too. Some players pass one-way rather than receiving from the same players.

These are essentially flow maps with origin and destinations as players, and frequencies as the number of passes (or other connectivity measure). While not a bad way to visuzlize flows between points, there are other approaches that I have seen less often. One of my favorites is the Sankey diagram. In particular, these work well for a single origin, to many destinations. Or the other way around. They are similar to a chord diagram, but with a linear layout rather than circular. Chord diagrams are interesting, but found they can be overwhelming for an audience that doesn't have experience with them and definitely need to be interactive over static.

Let's dive into a sankey diagram. As usual, I'll load data using the ssalib2 class. I'll work the StatsBomb Data since it has a lot available.


```python
import geopandas as gpd
from shapely.geometry.point import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from shapely import affinity

%load_ext autoreload
%autoreload 2
sns.set()
%matplotlib inline

```


```python
from ssalib2 import SpatialSoccer
```

I'll pull out all matches from Chelsea.


```python
sa = SpatialSoccer()
pitchgdf = SpatialSoccer.build_polygon_pitch_statsbomb()
team_name = "Chelsea FCW"
sb_matches = sa.get_match_list_from_source("open-data-master/data/matches/37/4.json",SpatialSoccer.STATS_BOMB_DATA,team_name=team_name)
m = sb_matches[0]
vars(m)

```




    {'match_id': 19743,
     'home_team_id': 969,
     'home_team_name': 'Birmingham City WFC',
     'home_team_score': 0,
     'away_team_id': 971,
     'away_team_name': 'Chelsea FCW',
     'away_team_score': 0,
     'season_id': 0,
     'season_name': '',
     'kick_off': '13:30:00.000',
     'match_date': '2018-10-21',
     'match_date_time': datetime.datetime(2018, 10, 21, 13, 30),
     'events': []}




```python
trajectories = None
   
for m in sb_matches:
    df = sa.load_events_from_match("open-data-master/data/events",SpatialSoccer.STATS_BOMB_DATA,m)
    trajs = m.build_match_trajectories(team_name,only_goals=False)

    try:
        trajectories = trajectories.append(trajs,ignore_index=True,sort=False)
    except:
        try:
            trajectories = trajs.copy()
        except:
            pass
    del trajs
    del df
trajectories.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>start_x</th>
      <th>start_y</th>
      <th>end_x</th>
      <th>end_y</th>
      <th>is_goal</th>
      <th>period</th>
      <th>match_id</th>
      <th>xg</th>
      <th>event_id</th>
      <th>event_name</th>
      <th>...</th>
      <th>timestamp</th>
      <th>body_part</th>
      <th>tags</th>
      <th>original_json</th>
      <th>event_time</th>
      <th>start_point</th>
      <th>end_point</th>
      <th>geometry</th>
      <th>trajectory_id</th>
      <th>temporal_distance</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>94.0</td>
      <td>31.0</td>
      <td>95.0</td>
      <td>31.0</td>
      <td>0</td>
      <td>1</td>
      <td>19743</td>
      <td>NaN</td>
      <td>f5787bc1-a906-48e6-8afd-f2a910a05030</td>
      <td>Carry</td>
      <td>...</td>
      <td>00:04:35.091</td>
      <td>None</td>
      <td>None</td>
      <td>{"id": "f5787bc1-a906-48e6-8afd-f2a910a05030",...</td>
      <td>2018-10-21 13:34:35.091</td>
      <td>POINT (94 31)</td>
      <td>POINT (95 31)</td>
      <td>POINT (94.00000 31.00000)</td>
      <td>19743_11</td>
      <td>275.091</td>
    </tr>
    <tr>
      <th>1</th>
      <td>95.0</td>
      <td>31.0</td>
      <td>105.0</td>
      <td>26.0</td>
      <td>0</td>
      <td>1</td>
      <td>19743</td>
      <td>NaN</td>
      <td>a726d31f-330f-44ab-8be6-501f5b779f5e</td>
      <td>Pass</td>
      <td>...</td>
      <td>00:04:35.786</td>
      <td>None</td>
      <td>None</td>
      <td>{"id": "a726d31f-330f-44ab-8be6-501f5b779f5e",...</td>
      <td>2018-10-21 13:34:35.786</td>
      <td>POINT (95 31)</td>
      <td>POINT (105 26)</td>
      <td>POINT (95.00000 31.00000)</td>
      <td>19743_11</td>
      <td>275.786</td>
    </tr>
    <tr>
      <th>2</th>
      <td>105.0</td>
      <td>26.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0</td>
      <td>1</td>
      <td>19743</td>
      <td>NaN</td>
      <td>76b34125-a56a-40e5-a974-ae673b07e91e</td>
      <td>Ball Receipt*</td>
      <td>...</td>
      <td>00:04:37.148</td>
      <td>None</td>
      <td>None</td>
      <td>{"id": "76b34125-a56a-40e5-a974-ae673b07e91e",...</td>
      <td>2018-10-21 13:34:37.148</td>
      <td>POINT (105 26)</td>
      <td>None</td>
      <td>POINT (105.00000 26.00000)</td>
      <td>19743_11</td>
      <td>277.148</td>
    </tr>
    <tr>
      <th>3</th>
      <td>105.0</td>
      <td>26.0</td>
      <td>109.0</td>
      <td>34.0</td>
      <td>0</td>
      <td>1</td>
      <td>19743</td>
      <td>NaN</td>
      <td>ce41e6ae-e09c-4bd0-ac86-66a0f135fd5d</td>
      <td>Carry</td>
      <td>...</td>
      <td>00:04:37.148</td>
      <td>None</td>
      <td>None</td>
      <td>{"id": "ce41e6ae-e09c-4bd0-ac86-66a0f135fd5d",...</td>
      <td>2018-10-21 13:34:37.148</td>
      <td>POINT (105 26)</td>
      <td>POINT (109 34)</td>
      <td>POINT (105.00000 26.00000)</td>
      <td>19743_11</td>
      <td>277.148</td>
    </tr>
    <tr>
      <th>4</th>
      <td>109.0</td>
      <td>34.0</td>
      <td>112.0</td>
      <td>35.0</td>
      <td>0</td>
      <td>1</td>
      <td>19743</td>
      <td>0.275178</td>
      <td>2ce2d620-e651-4d32-b6d8-261199b22bd1</td>
      <td>Shot</td>
      <td>...</td>
      <td>00:04:38.609</td>
      <td>None</td>
      <td>None</td>
      <td>{"id": "2ce2d620-e651-4d32-b6d8-261199b22bd1",...</td>
      <td>2018-10-21 13:34:38.609</td>
      <td>POINT (109 34)</td>
      <td>POINT (112 35)</td>
      <td>POINT (109.00000 34.00000)</td>
      <td>19743_11</td>
      <td>278.609</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 25 columns</p>
</div>



My ssalib2 class does not handle every loading eventuality, so some times I need to parse the data to get the values I'm looking for on an ad hoc basis. In this case, I need to pull out the recipient. Because the json doesn't always have the same properties for different situations on the pitch, it's easiest to handle this as an error in a function. This may be a little slower, but it works well enough here.


```python
passes = trajectories[trajectories['event_name']=='Pass'].copy()
```


```python
import json
def get_name(x):
    x = json.loads(x)
    try:
        return x['pass']['recipient']['name']
    except:
        return ""
passes['recipient_name'] = passes['original_json'].apply(lambda x: get_name(x))
```

For the passing diagrams I will be using a chart called a Sankey digram. I've used these alot to visualize flows, and find them to be clean and easy to follow. I use a free version called [PySankey](https://github.com/anazalea/pySankey) that I find creates very nice looking flexible diagrams. I've modified the code slightly to get the figure and axes objects from matplotlib, and that's what I'll use below.. Holoviews also has a sankey diagram tool. I don't like the look as much, but it is easier to create sequences of flows, meaning you can have more than two columns.

Here are the counts of each connection from a source to a target. If the target is blank, I'll assume it was a failed pass, either intercepted or otherwise.


```python
counts = passes[['event_name','event_player','recipient_name']].groupby(['event_player','recipient_name']).count().reset_index().rename(columns = {'event_player':'source',
'recipient_name':'target','event_name':'value'})
counts.loc[counts['target']=="","target"] = "Failed"
players = list(set().union(set(counts['source'].unique()),set(counts['target'].unique())))
counts
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>source</th>
      <th>target</th>
      <th>value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Adelina Engman</td>
      <td>Failed</td>
      <td>4</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Adelina Engman</td>
      <td>Bethany England</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Adelina Engman</td>
      <td>Drew Spence</td>
      <td>2</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Adelina Engman</td>
      <td>Erin Cuthbert</td>
      <td>3</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Adelina Engman</td>
      <td>Francesca Kirby</td>
      <td>1</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>314</th>
      <td>Sophie Ingle</td>
      <td>Maren Nævdal Mjelde</td>
      <td>1</td>
    </tr>
    <tr>
      <th>315</th>
      <td>Sophie Ingle</td>
      <td>Maria Thorisdottir</td>
      <td>1</td>
    </tr>
    <tr>
      <th>316</th>
      <td>Sophie Ingle</td>
      <td>Millie Bright</td>
      <td>10</td>
    </tr>
    <tr>
      <th>317</th>
      <td>Sophie Ingle</td>
      <td>Ramona Bachmann</td>
      <td>16</td>
    </tr>
    <tr>
      <th>318</th>
      <td>Sophie Ingle</td>
      <td>So-yun Ji</td>
      <td>21</td>
    </tr>
  </tbody>
</table>
<p>319 rows × 3 columns</p>
</div>



Here is the PySankey function that I've modified. This could be imported, but this is easier to incorporate in the notebook for here.


```python
# -*- coding: utf-8 -*-
"""
Produces simple Sankey Diagrams with matplotlib.
@author: Anneya Golob & marcomanz & pierre-sassoulas & jorwoods
                      .-.
                 .--.(   ).--.
      <-.  .-.-.(.->          )_  .--.
       `-`(     )-'             `)    )
         (o  o  )                `)`-'
        (      )                ,)
        ( ()  )                 )
         `---"\    ,    ,    ,/`
               `--' `--' `--'
                |  |   |   |
                |  |   |   |
                '  |   '   |
"""

from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


class PySankeyException(Exception):
    pass


class NullsInFrame(PySankeyException):
    pass


class LabelMismatch(PySankeyException):
    pass


def check_data_matches_labels(labels, data, side):
    if len(labels) > 0:
        if isinstance(data, list):
            data = set(data)
        if isinstance(data, pd.Series):
            data = set(data.unique().tolist())
        if isinstance(labels, list):
            labels = set(labels)
        if labels != data:
            msg = "\n"
            if len(labels) <= 20:
                msg = "Labels: " + ",".join(labels) + "\n"
            if len(data) < 20:
                msg += "Data: " + ",".join(data)
            raise LabelMismatch('{0} labels and data do not match.{1}'.format(side, msg))


def sankey(left, right, leftWeight=None, rightWeight=None, colorDict=None,
           leftLabels=None, rightLabels=None, aspect=4, rightColor=False,
           fontsize=14, figureName=None, closePlot=False,fileType="png",resolution=150,returnFigure=False,
           fig=None,subplot=111):
    '''
    Make Sankey Diagram showing flow from left-->right

    Inputs:
        left = NumPy array of object labels on the left of the diagram
        right = NumPy array of corresponding labels on the right of the diagram
            len(right) == len(left)
        leftWeight = NumPy array of weights for each strip starting from the
            left of the diagram, if not specified 1 is assigned
        rightWeight = NumPy array of weights for each strip starting from the
            right of the diagram, if not specified the corresponding leftWeight
            is assigned
        colorDict = Dictionary of colors to use for each label
            {'label':'color'}
        leftLabels = order of the left labels in the diagram
        rightLabels = order of the right labels in the diagram
        aspect = vertical extent of the diagram in units of horizontal extent
        rightColor = If true, each strip in the diagram will be be colored
                    according to its left label
    Ouput:
        None
    '''
    if leftWeight is None:
        leftWeight = []
    if rightWeight is None:
        rightWeight = []
    if leftLabels is None:
        leftLabels = []
    if rightLabels is None:
        rightLabels = []
    # Check weights
    if len(leftWeight) == 0:
        leftWeight = np.ones(len(left))

    if len(rightWeight) == 0:
        rightWeight = leftWeight
    if fig == None:
        plt.figure()
    else:
        fig.add_subplot(subplot) 
        
    plt.rc('text', usetex=False)
    #plt.rc('font', family='serif')

    # Create Dataframe
    if isinstance(left, pd.Series):
        left = left.reset_index(drop=True)
    if isinstance(right, pd.Series):
        right = right.reset_index(drop=True)
    dataFrame = pd.DataFrame({'left': left, 'right': right, 'leftWeight': leftWeight,
                              'rightWeight': rightWeight}, index=range(len(left)))

    if len(dataFrame[(dataFrame.left.isnull()) | (dataFrame.right.isnull())]):
        raise NullsInFrame('Sankey graph does not support null values.')

    # Identify all labels that appear 'left' or 'right'
    allLabels = pd.Series(np.r_[dataFrame.left.unique(), dataFrame.right.unique()]).unique()

    # Identify left labels
    if len(leftLabels) == 0:
        leftLabels = pd.Series(dataFrame.left.unique()).unique()
    else:
        check_data_matches_labels(leftLabels, dataFrame['left'], 'left')

    # Identify right labels
    if len(rightLabels) == 0:
        rightLabels = pd.Series(dataFrame.right.unique()).unique()
    else:
        check_data_matches_labels(rightLabels, dataFrame['right'], 'right')
    # If no colorDict given, make one
    if colorDict is None:
        colorDict = {}
        palette = "Blues"
        colorPalette = sns.color_palette(palette, len(allLabels))
        for i, label in enumerate(allLabels):
            colorDict[label] = colorPalette[i]
    else:
        missing = [label for label in allLabels if label not in colorDict.keys()]
        if missing:
            msg = "The colorDict parameter is missing values for the following labels : "
            msg += '{}'.format(', '.join(missing))
            raise ValueError(msg)

    # Determine widths of individual strips
    ns_l = defaultdict()
    ns_r = defaultdict()
    for leftLabel in leftLabels:
        leftDict = {}
        rightDict = {}
        for rightLabel in rightLabels:
            leftDict[rightLabel] = dataFrame[(dataFrame.left == leftLabel) & (dataFrame.right == rightLabel)].leftWeight.sum()
            rightDict[rightLabel] = dataFrame[(dataFrame.left == leftLabel) & (dataFrame.right == rightLabel)].rightWeight.sum()
        ns_l[leftLabel] = leftDict
        ns_r[leftLabel] = rightDict

    # Determine positions of left label patches and total widths
    leftWidths = defaultdict()
    for i, leftLabel in enumerate(leftLabels):
        myD = {}
        myD['left'] = dataFrame[dataFrame.left == leftLabel].leftWeight.sum()
        if i == 0:
            myD['bottom'] = 0
            myD['top'] = myD['left']
        else:
            myD['bottom'] = leftWidths[leftLabels[i - 1]]['top'] + 0.02 * dataFrame.leftWeight.sum()
            myD['top'] = myD['bottom'] + myD['left']
            topEdge = myD['top']
        leftWidths[leftLabel] = myD

    # Determine positions of right label patches and total widths
    rightWidths = defaultdict()
    for i, rightLabel in enumerate(rightLabels):
        myD = {}
        myD['right'] = dataFrame[dataFrame.right == rightLabel].rightWeight.sum()
        if i == 0:
            myD['bottom'] = 0
            myD['top'] = myD['right']
        else:
            myD['bottom'] = rightWidths[rightLabels[i - 1]]['top'] + 0.02 * dataFrame.rightWeight.sum()
            myD['top'] = myD['bottom'] + myD['right']
            topEdge = myD['top']
        rightWidths[rightLabel] = myD

    # Total vertical extent of diagram
    xMax = topEdge / aspect

    # Draw vertical bars on left and right of each  label's section & print label
    for leftLabel in leftLabels:
        plt.fill_between(
            [-0.02 * xMax, 0],
            2 * [leftWidths[leftLabel]['bottom']],
            2 * [leftWidths[leftLabel]['bottom'] + leftWidths[leftLabel]['left']],
            color=colorDict[leftLabel],
            alpha=0.99
        )
        plt.text(
            -0.05 * xMax,
            leftWidths[leftLabel]['bottom'] + 0.5 * leftWidths[leftLabel]['left'],
            leftLabel,
            {'ha': 'right', 'va': 'center'},
            fontsize=fontsize
        )
    for rightLabel in rightLabels:
        plt.fill_between(
            [xMax, 1.02 * xMax], 2 * [rightWidths[rightLabel]['bottom']],
            2 * [rightWidths[rightLabel]['bottom'] + rightWidths[rightLabel]['right']],
            color=colorDict[rightLabel],
            alpha=0.99
        )
        plt.text(
            1.05 * xMax,
            rightWidths[rightLabel]['bottom'] + 0.5 * rightWidths[rightLabel]['right'],
            rightLabel,
            {'ha': 'left', 'va': 'center'},
            fontsize=fontsize
        )

    # Plot strips
    for leftLabel in leftLabels:
        for rightLabel in rightLabels:
            labelColor = leftLabel
            if rightColor:
                labelColor = rightLabel
            if len(dataFrame[(dataFrame.left == leftLabel) & (dataFrame.right == rightLabel)]) > 0:
                # Create array of y values for each strip, half at left value,
                # half at right, convolve
                ys_d = np.array(50 * [leftWidths[leftLabel]['bottom']] + 50 * [rightWidths[rightLabel]['bottom']])
                ys_d = np.convolve(ys_d, 0.05 * np.ones(20), mode='valid')
                ys_d = np.convolve(ys_d, 0.05 * np.ones(20), mode='valid')
                ys_u = np.array(50 * [leftWidths[leftLabel]['bottom'] + ns_l[leftLabel][rightLabel]] + 50 * [rightWidths[rightLabel]['bottom'] + ns_r[leftLabel][rightLabel]])
                ys_u = np.convolve(ys_u, 0.05 * np.ones(20), mode='valid')
                ys_u = np.convolve(ys_u, 0.05 * np.ones(20), mode='valid')

                # Update bottom edges at each label so next strip starts at the right place
                leftWidths[leftLabel]['bottom'] += ns_l[leftLabel][rightLabel]
                rightWidths[rightLabel]['bottom'] += ns_r[leftLabel][rightLabel]
                plt.fill_between(
                    np.linspace(0, xMax, len(ys_d)), ys_d, ys_u, alpha=0.65,
                    color=colorDict[labelColor]
                )
    plt.gca().axis('off')
    #plt.gcf().set_size_inches(10,10)
    if figureName != None:
        plt.savefig("{}.{}".format(figureName,fileType), bbox_inches='tight', dpi=resolution)
    if closePlot:
        plt.close()
    if returnFigure:
        return (plt.gca(),plt.gcf())
```

Here is the overall layout for all the players to get a sense of what the diagram looks like. On the left is the source, and the target is on the right. 

I admit this is a little hard to read. You could manipulate the font size, or the figure size, but then it is still hard to follow the exact path to the target. Giving each player a unique color could help too.


```python
a,fig = sankey(
    left=counts['source'], right=counts['target'],leftWeight= counts['value'], rightWeight=counts['value'], aspect=4,
    fontsize=8, figureName="test_passes",rightColor=False, returnFigure=True
)
fig
```




![png](images/8/output_14_0.png)



Another approach is to filter out those source/target combinations that had very few passes. Here I use only the 75th percentile and above to make it fewer combinations, and increased the figure size.


```python
quartile = np.percentile(counts['value'],75)
fig = plt.figure(figsize=(10,10))
tbl = counts[counts['value']>=quartile][['source','target','value']].values
sankey(
    left=tbl[:,0], right=tbl[:,1],leftWeight= tbl[:,2], rightWeight=tbl[:,2], aspect=4,
    fontsize=8, figureName="test_passes",rightColor=False, fig = fig
)
fig
```




![png](images/8/output_16_0.png)



Ultimately, I think this looks best if I only show the source as a certain player. We can really see who Sophie Ingle feeds the ball too.


```python
quartile = np.percentile(counts['value'],75)
fig = plt.figure(figsize=(10,10))
tbl = counts[counts['source']=='Sophie Ingle'][['source','target','value']].sort_values("value").values
sankey(
    left=tbl[:,0], right=tbl[:,1],leftWeight= tbl[:,2], rightWeight=tbl[:,2], aspect=4,
    fontsize=8, figureName="test_passes",rightColor=True, fig = fig
)
fig
```




![png](images/8/output_18_0.png)



The same plot may be created with Holoviews, but it throws an error when I try and use the same data because the names of the players are both source and target. Or, in other words, the nodes are both the source and target. Holoviews says this is a cyclical graph, but I would argue that the source and target are never the same...anyway, we can get around this by picking a single source.


```python
import holoviews as hv
from holoviews import opts, dim
hv.extension('matplotlib')
```







<div class="logo-block">
<img src='data:image/png;base64,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
roTBs2RqAAAAAElFTkSuQmCC'
     style='height:25px; border-radius:12px; display: inline-block; float: left; vertical-align: middle'></img>




  <img src='data:image/png;base64,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'
       style='height:15px; border-radius:12px; display: inline-block; float: left'></img>



</div>




```python
sankey = hv.Sankey(counts[counts['source']=='Sophie Ingle'][['source','target','value']].values)
sankey.opts()
```




<img src='data:image/png;base64,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lhJh33bnFCS554v7MPN4vLj44ssRF8dVGKq/GNAQERFVwqkcrJGu6p5VsQahlVNYWIhevc5Gfn6+Y5mEhATs2nWwajokqoMY0BARERGFUHUBq+i5tEq0JknIz8/H9OnTHcvMnDmzajojqqPk0EWIiIiIiIjqJgY0REREREQUsRjQEBERERFRxGJAQ0REREREEYsBDRERERERRSwGNEREREREFLEY0BARERERUcRiQENERERERBGLAQ0REREREUUsBjRERERERBSxGNAQEREREVHEYkBDREREVA+kpa3EkCEDUVJSAgA4fPgPXHHFRcjOzqpQO4cP/4F58+YI81JSxlR6nG+88RpSUsZg1qypmDVrKlatSjXlL168qNJ9nIzi4mIsWDAXX3yxGgCwZMnrmD17BiZPnojRo++rlTGRylvbAyAiIiKimtG1azd8993X6N//GqSlrcS5554PAFix4gNkZOxGdnYmBg68Dv36XYJ58+YgISEB27ZtxaOPTsDevRnYvn0rysrK4PV6sX//Pixd+i/ExMSipKQYU6fOAgD4/X688spL8Pv9KCjIx5gx4zF79kx07doNhw//gcsuuwLt2nUQ1tXcc88D6NGjZ3A/LW0lvv76S3Tr1gMZGbsBAK+99jJKSoqRmZmJJ56YioULn0dCQiKKi4swbtxjmDv3meD+xImT8fLLL6KoqAh5ebl46KFH8cYbryIpqSV8vgK0bdseN910i+u5e//9/4Ms62sB99zzAABgzpyZGDduYuXfHDppDGiIiIiI6okrr+yPb7/9H668sj+OHctGUlISAKBLl67o0KEj0tN/xbp1a+DzFeCqq/rjssuuxPPPzwYAfPPNV5g370Xs3bsHH3zwHho2bIghQ25ETk4OXnttcbCPH39ch71796BTp84oLPRh69Z0FBcX4c4770Z2djaWLHkNXbt2F9bVvPXWv9C4cRMAwPXX3wAAuPjiSzFs2M1ISRmD/fv3oaSkGGPGpODgwQMIBAI4evQIunfvgbPP7ga/v8y0v3fvHpSWlmLChEn47bcdWL78fQDA4MFDcdppp2PChDEhA5qRI+9BWtpKU9r69Wtxxhlt0bJlq5N8R6gq8JYzIiIionoiJiYGTZo0w0cfrUC/fpcG019//WX4fD5069YdiqKgpKQEkiQBAGTZAwDBfY9H3f/889XYvHkj2rZt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' style='max-width:100%; margin: auto; display: block; '/>



Just for completeness, another option is to visualize the graph matrix as a heat map (or a heat matrix). Often these are used to visualize correlations. I think these can work well, but there are a number of gaps between players in this dataset. 

The heat map lets us quickly identify very popular passing combinations. For example, from Joanna Anderson to Magdalena Ericsson. But the gaps also tell us something. I won't read too much into this, but why doesn't Bethany England have any passes to Magdalena? The answer probably varies: positions, playing time, tactics, etc... but if we were to do a deep dive what could that tell us about Chelsea's strategies?



```python
%matplotlib inline
fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(111)
countpivot = counts.pivot('source','target','value')
sns.heatmap(countpivot,ax=ax)
```




    <matplotlib.axes._subplots.AxesSubplot at 0x1a1b55853c8>




![png](images/8/output_23_1.png)



```python

```
