```python

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

sns.set()
%matplotlib inline

%load_ext autoreload
%autoreload 2
```

# Limitations

Not surprisingly I reached a limit on the adhoc sort of library I was developing. For one, it was pretty specific to Statsbomb's data. That's fine, but then I found some open [wyscout data](https://www.nature.com/articles/s41597-019-0247-7). This is similar in that they are event based, but quite different in their structure. So to load the events I would have to really create many different loading functions, blah, blah, blah.

Instead I created ssalib2. I used an object-based approach to abstract some of the similarities so I could easily load the data from the source. I also simplified the dataframe to just the elements I was interested in.

I hadn't posted it yet, but I began using Statsbomb's possession id to develop trajectories. It's pretty cool, and makes identifying sequences much easier. Unfortunately, wyscout doesn't have a similar feature. So, I included a basic tool to build this almost entirely off the time and types of events. It's limited but still something.

Wyscout also standardizes the location based as a percentage in the x and y from the upper left corner (at least that's how I understood it to be). So I standardize these to fit the Statsbomb pitch and make them "comparable."

Finally, I kept the ssalib so you can still use it with the older notebooks and projects.

## Use

To use the library you load as before.


```python


from ssalib2 import SpatialSoccer
sa = SpatialSoccer()
```

Matches are loaded using the get_match_list_from_source tool. You specify the match json file, and then the code for either statsbomb or wyscout matches


```python
sb_matches = sa.get_match_list_from_source("open-data-master/data/matches/11/1.json",SpatialSoccer.STATS_BOMB_DATA)
ws_matches = sa.get_match_list_from_source("wyscout/matches_England.json",SpatialSoccer.WYSCOUT_DATA)
```

Matches are match objects with simple properties taken and standardized across the sources.


```python
m_ws = ws_matches[0]
print(m_ws .match_id)
m_sb = sb_matches[0]
print(m_sb.match_id)
```

    2500089
    9642
    


```python
vars(m_sb)
```




    {'match_id': 9642,
     'home_team_id': 212,
     'home_team_name': 'Atlético Madrid',
     'home_team_score': 1,
     'away_team_id': 217,
     'away_team_name': 'Barcelona',
     'away_team_score': 1,
     'season_id': 0,
     'season_name': '',
     'kick_off': '20:45:00.000',
     'match_date': '2017-10-14',
     'match_date_time': datetime.datetime(2017, 10, 14, 20, 45),
     'events': []}



Events is an empty list, but will be populated after calling the sa.load_events_from_match function. The path to the events is different for statsbomb and wyscout. You need to specify the source and then provide the match object.

This function creates the geodataframe and uses the start point as the default geometry. Time is converted based on the match's time and kickoff. 


```python
df_sb = sa.load_events_from_match("open-data-master/data/events",SpatialSoccer.STATS_BOMB_DATA,m_sb)
```


```python
df_sb.head()
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
      <th>event_id</th>
      <th>event_name</th>
      <th>subevent_name</th>
      <th>...</th>
      <th>event_player</th>
      <th>possession_id</th>
      <th>timestamp</th>
      <th>body_part</th>
      <th>tags</th>
      <th>original_json</th>
      <th>event_time</th>
      <th>start_point</th>
      <th>end_point</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>1</td>
      <td>None</td>
      <td>98c0356d-5ded-45b4-aa26-e91890cbc9b4</td>
      <td>Starting XI</td>
      <td>None</td>
      <td>...</td>
      <td>None</td>
      <td>1</td>
      <td>00:00:00.000</td>
      <td>None</td>
      <td>None</td>
      <td>{"id": "98c0356d-5ded-45b4-aa26-e91890cbc9b4",...</td>
      <td>2017-10-14 20:45:00.000</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>1</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>1</td>
      <td>None</td>
      <td>d0a7db05-01d9-4939-8713-07bfba6b6869</td>
      <td>Starting XI</td>
      <td>None</td>
      <td>...</td>
      <td>None</td>
      <td>1</td>
      <td>00:00:00.000</td>
      <td>None</td>
      <td>None</td>
      <td>{"id": "d0a7db05-01d9-4939-8713-07bfba6b6869",...</td>
      <td>2017-10-14 20:45:00.000</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>2</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>1</td>
      <td>None</td>
      <td>f9652949-4e0d-4448-ab9f-45d38bcafdc2</td>
      <td>Half Start</td>
      <td>None</td>
      <td>...</td>
      <td>None</td>
      <td>1</td>
      <td>00:00:00.000</td>
      <td>None</td>
      <td>None</td>
      <td>{"id": "f9652949-4e0d-4448-ab9f-45d38bcafdc2",...</td>
      <td>2017-10-14 20:45:00.000</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>3</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>1</td>
      <td>None</td>
      <td>58d1751f-31f0-45e2-a355-92dba687b706</td>
      <td>Half Start</td>
      <td>None</td>
      <td>...</td>
      <td>None</td>
      <td>1</td>
      <td>00:00:00.000</td>
      <td>None</td>
      <td>None</td>
      <td>{"id": "58d1751f-31f0-45e2-a355-92dba687b706",...</td>
      <td>2017-10-14 20:45:00.000</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>4</th>
      <td>60.0</td>
      <td>40.0</td>
      <td>43.0</td>
      <td>39.0</td>
      <td>0.0</td>
      <td>1</td>
      <td>None</td>
      <td>a778634f-ba04-44b5-a48d-ab3cdce9b6d8</td>
      <td>Pass</td>
      <td>None</td>
      <td>...</td>
      <td>Luis Alberto Suárez Díaz</td>
      <td>2</td>
      <td>00:00:00.020</td>
      <td>None</td>
      <td>None</td>
      <td>{"id": "a778634f-ba04-44b5-a48d-ab3cdce9b6d8",...</td>
      <td>2017-10-14 20:45:00.020</td>
      <td>POINT (60 40)</td>
      <td>POINT (43 39)</td>
      <td>POINT (60.00000 40.00000)</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 22 columns</p>
</div>



The only major difference in the dataframes between wyscout and statsbomb is that wyscout only populates using the keys\ids in the json file. I will eventually add a function to get the names instead, since I find that easier to work with.

The path for wyscout goes directly to the json file that you are trying to load. This is because the open wyscout data file is one big dump of the events, and they need to be matched to the match_id.


```python
df_ws = sa.load_events_from_match("wyscout/events_England.json",SpatialSoccer.WYSCOUT_DATA,m_ws)
df_ws.head()
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
      <th>event_id</th>
      <th>event_name</th>
      <th>subevent_name</th>
      <th>...</th>
      <th>event_player</th>
      <th>possession_id</th>
      <th>timestamp</th>
      <th>body_part</th>
      <th>tags</th>
      <th>original_json</th>
      <th>event_time</th>
      <th>start_point</th>
      <th>end_point</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>60.0</td>
      <td>40.0</td>
      <td>48.0</td>
      <td>44.0</td>
      <td>0</td>
      <td>1</td>
      <td>2500089</td>
      <td>251700146</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>...</td>
      <td>9637</td>
      <td>0</td>
      <td>2.763597</td>
      <td>None</td>
      <td>1801</td>
      <td>{"eventId": 8, "subEventName": "Simple pass", ...</td>
      <td>2018-05-13 16:00:02.763597-02:00</td>
      <td>POINT (60 40)</td>
      <td>POINT (48 44)</td>
      <td>POINT (60.00000 40.00000)</td>
    </tr>
    <tr>
      <th>1</th>
      <td>48.0</td>
      <td>44.0</td>
      <td>46.8</td>
      <td>68.0</td>
      <td>0</td>
      <td>1</td>
      <td>2500089</td>
      <td>251700147</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>...</td>
      <td>8351</td>
      <td>0</td>
      <td>4.761353</td>
      <td>None</td>
      <td>1801</td>
      <td>{"eventId": 8, "subEventName": "Simple pass", ...</td>
      <td>2018-05-13 16:00:04.761353-02:00</td>
      <td>POINT (48 44)</td>
      <td>POINT (46.8 68)</td>
      <td>POINT (48.00000 44.00000)</td>
    </tr>
    <tr>
      <th>2</th>
      <td>46.8</td>
      <td>68.0</td>
      <td>37.2</td>
      <td>56.0</td>
      <td>0</td>
      <td>1</td>
      <td>2500089</td>
      <td>251700148</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>...</td>
      <td>9285</td>
      <td>0</td>
      <td>5.533097</td>
      <td>None</td>
      <td>1801</td>
      <td>{"eventId": 8, "subEventName": "Simple pass", ...</td>
      <td>2018-05-13 16:00:05.533097-02:00</td>
      <td>POINT (46.8 68)</td>
      <td>POINT (37.2 56)</td>
      <td>POINT (46.80000 68.00000)</td>
    </tr>
    <tr>
      <th>3</th>
      <td>37.2</td>
      <td>56.0</td>
      <td>79.2</td>
      <td>57.6</td>
      <td>0</td>
      <td>1</td>
      <td>2500089</td>
      <td>251700161</td>
      <td>Pass</td>
      <td>High pass</td>
      <td>...</td>
      <td>239411</td>
      <td>0</td>
      <td>7.707561</td>
      <td>None</td>
      <td>1801</td>
      <td>{"eventId": 8, "subEventName": "High pass", "t...</td>
      <td>2018-05-13 16:00:07.707561-02:00</td>
      <td>POINT (37.2 56)</td>
      <td>POINT (79.2 57.59999999999999)</td>
      <td>POINT (37.20000 56.00000)</td>
    </tr>
    <tr>
      <th>4</th>
      <td>79.2</td>
      <td>57.6</td>
      <td>85.2</td>
      <td>65.6</td>
      <td>0</td>
      <td>1</td>
      <td>2500089</td>
      <td>251700149</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>...</td>
      <td>9637</td>
      <td>0</td>
      <td>11.614943</td>
      <td>None</td>
      <td>1801</td>
      <td>{"eventId": 8, "subEventName": "Simple pass", ...</td>
      <td>2018-05-13 16:00:11.614943-02:00</td>
      <td>POINT (79.2 57.59999999999999)</td>
      <td>POINT (85.19999999999999 65.59999999999999)</td>
      <td>POINT (79.20000 57.60000)</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 22 columns</p>
</div>



I need to review the possession id a little more for the wyscout data, but it seems ok for a start. I have to get more familiar with how wyscout organizes its information.


```python
df_ws.loc[df_ws['possession_id']==0,["possession_id","event_name","subevent_name","event_team_name"]]
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
      <th>possession_id</th>
      <th>event_name</th>
      <th>subevent_name</th>
      <th>event_team_name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0</td>
      <td>Pass</td>
      <td>High pass</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>5</th>
      <td>0</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>6</th>
      <td>0</td>
      <td>Pass</td>
      <td>Cross</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>7</th>
      <td>0</td>
      <td>Others on the ball</td>
      <td>Clearance</td>
      <td>1646</td>
    </tr>
    <tr>
      <th>8</th>
      <td>0</td>
      <td>Pass</td>
      <td>Cross</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>9</th>
      <td>0</td>
      <td>Others on the ball</td>
      <td>Clearance</td>
      <td>1646</td>
    </tr>
    <tr>
      <th>10</th>
      <td>0</td>
      <td>Interruption</td>
      <td>Ball out of the field</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>11</th>
      <td>0</td>
      <td>Free Kick</td>
      <td>Throw in</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>12</th>
      <td>0</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>13</th>
      <td>0</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>14</th>
      <td>0</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>15</th>
      <td>0</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>16</th>
      <td>0</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>17</th>
      <td>0</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>18</th>
      <td>0</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>19</th>
      <td>0</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>20</th>
      <td>0</td>
      <td>Duel</td>
      <td>Ground attacking duel</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>21</th>
      <td>0</td>
      <td>Duel</td>
      <td>Ground defending duel</td>
      <td>1646</td>
    </tr>
  </tbody>
</table>
</div>




```python
df_ws.loc[df_ws['possession_id']==1,["possession_id","event_name","subevent_name","event_team_name"]]
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
      <th>possession_id</th>
      <th>event_name</th>
      <th>subevent_name</th>
      <th>event_team_name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>22</th>
      <td>1</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1646</td>
    </tr>
    <tr>
      <th>23</th>
      <td>1</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1646</td>
    </tr>
    <tr>
      <th>24</th>
      <td>1</td>
      <td>Duel</td>
      <td>Ground defending duel</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>25</th>
      <td>1</td>
      <td>Duel</td>
      <td>Ground attacking duel</td>
      <td>1646</td>
    </tr>
    <tr>
      <th>26</th>
      <td>1</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1646</td>
    </tr>
    <tr>
      <th>27</th>
      <td>1</td>
      <td>Pass</td>
      <td>Simple pass</td>
      <td>1646</td>
    </tr>
    <tr>
      <th>28</th>
      <td>1</td>
      <td>Pass</td>
      <td>Launch</td>
      <td>1646</td>
    </tr>
    <tr>
      <th>29</th>
      <td>1</td>
      <td>Duel</td>
      <td>Air duel</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>30</th>
      <td>1</td>
      <td>Duel</td>
      <td>Air duel</td>
      <td>1646</td>
    </tr>
    <tr>
      <th>31</th>
      <td>1</td>
      <td>Pass</td>
      <td>Launch</td>
      <td>1646</td>
    </tr>
    <tr>
      <th>32</th>
      <td>1</td>
      <td>Duel</td>
      <td>Air duel</td>
      <td>1659</td>
    </tr>
    <tr>
      <th>33</th>
      <td>1</td>
      <td>Duel</td>
      <td>Air duel</td>
      <td>1646</td>
    </tr>
  </tbody>
</table>
</div>




```python

```
