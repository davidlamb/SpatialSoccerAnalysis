# Premier League ICT

Fantasy Premier League (FPL) includes an interesting index for managers to evaluate different players. This is called the ICT, or Influence Creativity Threat index. Each in turn is available on their own. Presumeably ICT is a weighted combination of the three components. These indices are very useful, and accruately predict the value of a player as I've found with my cost models.

Unfortunately, the Bundesliga does not have such an index. The basic information provided in their player list gives information about their points, that doesn't necessarily tell you much about the player. How many minutes are they likely to play? What type of xG do they get?

All that information is wrapped up in the ICT and different component parts. The FPL doesn't provide much information about how ICT is calculated. Presumeably because they are using to calculate a price for a player, and don't want managers to somehow manipulate it.

I'm going to try and use a simple factor analysis to create my own indices that follow the Influence, Creativity and Threat. FPL may be using a different approach, and there could be other ways to do this. I also have no way of validating if this will produce correct results until the Bundesliga fantasy game starts again.

Data for this comes from FBREF for the 2019/2020 Bundesliga season. FBREF separates the data for goalkeepers and everyone else, so I will break the factor analysis by position.

First I will load the data. I'm not sharing my downloaded data since I'm not clear if that would violate FBREF's policies. I took my time scraping and tried my best to not put too much preassure on their servers.



```python
import pandas as pd
import numpy as np
import sklearn
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
from factor_analyzer.factor_analyzer import calculate_kmo
from factor_analyzer import FactorAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
%matplotlib inline  
fbrefdata = pd.read_csv("playermatchstatswithidc.csv",index_col=0)
```

I've matched the names in the webpage to what they are for each of the positions, and pulled out what I thought were relevant variables. I did not include red or yellow cards. Those are so rare (especially for a goal keeper) that it wouldn't add any information to the anlaysis.

You can see FBREF includes a lot of different pieces of information.


```python
goal_keeper_variables = {'minutes': 'Min -- Minutes',
'shots_on_target_against':"Shots on Target Against",
'goals_against_gk':"Goals Against",
'saves':"saves",
'clean_sheets':"Clean sheets",
'psxg_gk':"Post-Shot Expected Goals is expected goals based on how likely the goalkeeper is to save the shot",
'passes_launched_gk':"Passes attempted longer than 40 yards",
'def_actions_outside_pen_area_gk':"number of defensive actions outside of the penalty area",
'passes_throws_gk':"Throws attempted",
'crosses_stopped_gk':"Number of crosses into penalty area which were successfully stopped by the goalkeeper",
'passes_gk':"Passes attempted",
'passes_completed_launched_gk':"Passes completed longer than 40 yards",
'goal_kicks':"Passes Attempted",
'crosses_gk':"Opponent's attempted crosses into penalty area",
'avg_distance_def_actions_gk':"Average distance from goal to perform defensive actions",
'psxg_gk':"Post-Shot Expected Goals is expected goals based on how likely the goalkeeper is to save the shot"}
```

Goalkeepers are separated and any missing values are replaced with a zero. Finally, the data is normalized using standard deviations.


```python
goal_keepers= fbrefdata[fbrefdata['playerposition']=="GK"][goal_keeper_variables.keys()].copy()
goal_keepers.dropna(thresh=6,inplace=True)
goal_keepers.fillna(0,inplace=True)
goal_keepers_norm=(goal_keepers-goal_keepers.mean())/goal_keepers.std()
Xgk = goal_keepers_norm.values
```

Some preliminaries show that using a factor analysis is approriate. The Chi-Square test for bartlett sphericity is significant. And KMO is at .60, just at the threshold recommended for this tool.


```python
chi_square_value,p_value=calculate_bartlett_sphericity(Xgk)
print(chi_square_value, p_value)
kmo_all,kmo_model=calculate_kmo(Xgk)
print(kmo_model)
```

    5263.007051909828 0.0
    0.6017069851073323
    

While we are only considering 3 factors to make this comparable to ICT, it's worth seeing how many factors this data can be broken down to.


```python
fa = FactorAnalyzer()
fa.fit(Xgk)
ev, v = fa.get_eigenvalues()
ev
```




    array([3.49618056, 2.58765273, 1.7932264 , 1.28496664, 1.14605257,
           1.04557113, 0.93998101, 0.70748287, 0.45640441, 0.44273216,
           0.39662938, 0.35676539, 0.19710348, 0.13592899, 0.01332228])



There are 6 factors suggested by the eigenvalues.

If I were to use 6 indices for a goalkeeper, it seems like it would be:

1. Goals scored against the keeper
2. Passing and influence on building up from the back.
3. Shots against the keeper
4. Defensive abilities
5. Penalties
6. Time in game.

I don't really think this level of detail is needed.


```python
n_factors = 6
fa = FactorAnalyzer(n_factors=n_factors,rotation="varimax")
fa.fit(Xgk)
lgk = pd.DataFrame(fa.loadings_,index=goal_keepers.columns,columns=range(1,n_factors+1))
lgk['MaxFactor'] = lgk[list(range(1,n_factors+1))].idxmax(axis=1)
lgk.sort_values("MaxFactor")
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
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
      <th>5</th>
      <th>6</th>
      <th>MaxFactor</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>goals_against_gk</th>
      <td>0.997485</td>
      <td>-0.006130</td>
      <td>0.032778</td>
      <td>0.007394</td>
      <td>-0.045809</td>
      <td>-0.020157</td>
      <td>1</td>
    </tr>
    <tr>
      <th>psxg_gk</th>
      <td>0.807507</td>
      <td>0.034202</td>
      <td>0.353884</td>
      <td>-0.003488</td>
      <td>0.054866</td>
      <td>0.033229</td>
      <td>1</td>
    </tr>
    <tr>
      <th>clean_sheets</th>
      <td>-0.633900</td>
      <td>0.030267</td>
      <td>-0.039670</td>
      <td>-0.007564</td>
      <td>0.026849</td>
      <td>-0.040566</td>
      <td>2</td>
    </tr>
    <tr>
      <th>passes_launched_gk</th>
      <td>-0.032518</td>
      <td>0.916403</td>
      <td>0.093272</td>
      <td>-0.114541</td>
      <td>0.292385</td>
      <td>0.032804</td>
      <td>2</td>
    </tr>
    <tr>
      <th>passes_completed_launched_gk</th>
      <td>-0.003283</td>
      <td>0.757876</td>
      <td>0.075714</td>
      <td>-0.083081</td>
      <td>0.119050</td>
      <td>0.130654</td>
      <td>2</td>
    </tr>
    <tr>
      <th>shots_on_target_against</th>
      <td>0.588681</td>
      <td>0.110186</td>
      <td>0.789091</td>
      <td>-0.032234</td>
      <td>0.080988</td>
      <td>0.080723</td>
      <td>3</td>
    </tr>
    <tr>
      <th>saves</th>
      <td>0.117706</td>
      <td>0.139657</td>
      <td>0.942428</td>
      <td>-0.047572</td>
      <td>0.135713</td>
      <td>0.122787</td>
      <td>3</td>
    </tr>
    <tr>
      <th>def_actions_outside_pen_area_gk</th>
      <td>0.006677</td>
      <td>-0.074354</td>
      <td>-0.019128</td>
      <td>0.609950</td>
      <td>-0.059832</td>
      <td>0.138597</td>
      <td>4</td>
    </tr>
    <tr>
      <th>avg_distance_def_actions_gk</th>
      <td>-0.008751</td>
      <td>-0.074398</td>
      <td>-0.041231</td>
      <td>0.988991</td>
      <td>-0.102694</td>
      <td>-0.007904</td>
      <td>4</td>
    </tr>
    <tr>
      <th>crosses_stopped_gk</th>
      <td>-0.042648</td>
      <td>0.040221</td>
      <td>-0.026155</td>
      <td>-0.012622</td>
      <td>0.343293</td>
      <td>0.220380</td>
      <td>5</td>
    </tr>
    <tr>
      <th>goal_kicks</th>
      <td>0.033549</td>
      <td>0.311772</td>
      <td>0.137117</td>
      <td>-0.092057</td>
      <td>0.438525</td>
      <td>-0.115833</td>
      <td>5</td>
    </tr>
    <tr>
      <th>crosses_gk</th>
      <td>0.007348</td>
      <td>0.194356</td>
      <td>0.135061</td>
      <td>-0.107155</td>
      <td>0.877963</td>
      <td>0.021963</td>
      <td>5</td>
    </tr>
    <tr>
      <th>minutes</th>
      <td>0.073357</td>
      <td>0.142677</td>
      <td>0.071056</td>
      <td>0.098124</td>
      <td>0.047246</td>
      <td>0.208769</td>
      <td>6</td>
    </tr>
    <tr>
      <th>passes_throws_gk</th>
      <td>0.061174</td>
      <td>-0.200391</td>
      <td>0.090664</td>
      <td>-0.002786</td>
      <td>0.186838</td>
      <td>0.690186</td>
      <td>6</td>
    </tr>
    <tr>
      <th>passes_gk</th>
      <td>-0.053455</td>
      <td>0.282961</td>
      <td>0.012279</td>
      <td>0.116481</td>
      <td>-0.115860</td>
      <td>0.666814</td>
      <td>6</td>
    </tr>
  </tbody>
</table>
</div>



Let's see how our variables would be broken up into three components.

How can we translate 1,2,3 into Influence Creativity and Threat.

Influence strikes me as the goalkeeper's ability to perform in their position. To me this seems to be Factor 1. Creativity seems to suggest their ability to respond to the attacking offense. I think that would be factor 3. Finally threat is how they can beat the opponent. We are left with factor 2 for that.

There's probably an argument to be made that influence may be how they build up play from the back, which would be factor 2. And, factor 1 could be their threat, meaning a threat to the opposition.


This is important to decide, because you need to align these factors with the other position, so that you have variables for threat, creativity, and influence.


```python
n_factors = 3
fa = FactorAnalyzer(n_factors=n_factors,rotation="varimax")
fa.fit(Xgk)
lgk = pd.DataFrame(fa.loadings_,index=goal_keepers.columns,columns=range(1,n_factors+1))
lgk['MaxFactor'] = lgk[list(range(1,n_factors+1))].idxmax(axis=1)
lgk.sort_values("MaxFactor")
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
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>MaxFactor</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>shots_on_target_against</th>
      <td>0.871261</td>
      <td>0.306949</td>
      <td>0.102879</td>
      <td>1</td>
    </tr>
    <tr>
      <th>goals_against_gk</th>
      <td>0.816645</td>
      <td>-0.135173</td>
      <td>-0.012684</td>
      <td>1</td>
    </tr>
    <tr>
      <th>saves</th>
      <td>0.485677</td>
      <td>0.417080</td>
      <td>0.108827</td>
      <td>1</td>
    </tr>
    <tr>
      <th>psxg_gk</th>
      <td>0.915968</td>
      <td>0.054941</td>
      <td>0.035895</td>
      <td>1</td>
    </tr>
    <tr>
      <th>clean_sheets</th>
      <td>-0.576957</td>
      <td>0.106427</td>
      <td>-0.015340</td>
      <td>2</td>
    </tr>
    <tr>
      <th>passes_launched_gk</th>
      <td>-0.019570</td>
      <td>0.849839</td>
      <td>0.030332</td>
      <td>2</td>
    </tr>
    <tr>
      <th>crosses_stopped_gk</th>
      <td>-0.041674</td>
      <td>0.245441</td>
      <td>0.084974</td>
      <td>2</td>
    </tr>
    <tr>
      <th>passes_completed_launched_gk</th>
      <td>0.000298</td>
      <td>0.674358</td>
      <td>0.094029</td>
      <td>2</td>
    </tr>
    <tr>
      <th>goal_kicks</th>
      <td>0.082776</td>
      <td>0.501039</td>
      <td>-0.108805</td>
      <td>2</td>
    </tr>
    <tr>
      <th>crosses_gk</th>
      <td>0.077051</td>
      <td>0.572033</td>
      <td>-0.073674</td>
      <td>2</td>
    </tr>
    <tr>
      <th>minutes</th>
      <td>0.091221</td>
      <td>0.164276</td>
      <td>0.225577</td>
      <td>3</td>
    </tr>
    <tr>
      <th>def_actions_outside_pen_area_gk</th>
      <td>-0.028091</td>
      <td>-0.230739</td>
      <td>0.684753</td>
      <td>3</td>
    </tr>
    <tr>
      <th>passes_throws_gk</th>
      <td>0.114960</td>
      <td>0.085186</td>
      <td>0.254461</td>
      <td>3</td>
    </tr>
    <tr>
      <th>passes_gk</th>
      <td>-0.038171</td>
      <td>0.230888</td>
      <td>0.418966</td>
      <td>3</td>
    </tr>
    <tr>
      <th>avg_distance_def_actions_gk</th>
      <td>-0.056693</td>
      <td>-0.319037</td>
      <td>0.613164</td>
      <td>3</td>
    </tr>
  </tbody>
</table>
</div>



Because I want these weights to be a weighted combination of the variables that bar part of that factor, I need to derive the weights for it. In this case I'm going to use the sum of the loadings and create a percentage of each variable to be added to the index total.


```python

def perc(values):
    return (values/np.sum(values))
lgk['Label']=""
lgk['weight']=0.0
lgk.loc[lgk['MaxFactor']==3,"Label"] = "Influence"
lgk.loc[lgk['MaxFactor']==2,"Label"] = "Creativity"
lgk.loc[lgk['MaxFactor']==1,"Label"] = "Threat"

lgk.loc[lgk['MaxFactor']==1,"weight"]=perc(lgk[lgk['MaxFactor']==1][1].values)
lgk.loc[lgk['MaxFactor']==3,"weight"]=perc(lgk[lgk['MaxFactor']==3][3].values)
lgk.loc[lgk['MaxFactor']==2,"weight"]=perc(lgk[lgk['MaxFactor']==2][2].values)

lgk.sort_values("MaxFactor")
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
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>MaxFactor</th>
      <th>Label</th>
      <th>weight</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>shots_on_target_against</th>
      <td>0.871261</td>
      <td>0.306949</td>
      <td>0.102879</td>
      <td>1</td>
      <td>Threat</td>
      <td>0.282002</td>
    </tr>
    <tr>
      <th>goals_against_gk</th>
      <td>0.816645</td>
      <td>-0.135173</td>
      <td>-0.012684</td>
      <td>1</td>
      <td>Threat</td>
      <td>0.264325</td>
    </tr>
    <tr>
      <th>saves</th>
      <td>0.485677</td>
      <td>0.417080</td>
      <td>0.108827</td>
      <td>1</td>
      <td>Threat</td>
      <td>0.157200</td>
    </tr>
    <tr>
      <th>psxg_gk</th>
      <td>0.915968</td>
      <td>0.054941</td>
      <td>0.035895</td>
      <td>1</td>
      <td>Threat</td>
      <td>0.296473</td>
    </tr>
    <tr>
      <th>clean_sheets</th>
      <td>-0.576957</td>
      <td>0.106427</td>
      <td>-0.015340</td>
      <td>2</td>
      <td>Creativity</td>
      <td>0.036088</td>
    </tr>
    <tr>
      <th>passes_launched_gk</th>
      <td>-0.019570</td>
      <td>0.849839</td>
      <td>0.030332</td>
      <td>2</td>
      <td>Creativity</td>
      <td>0.288165</td>
    </tr>
    <tr>
      <th>crosses_stopped_gk</th>
      <td>-0.041674</td>
      <td>0.245441</td>
      <td>0.084974</td>
      <td>2</td>
      <td>Creativity</td>
      <td>0.083225</td>
    </tr>
    <tr>
      <th>passes_completed_launched_gk</th>
      <td>0.000298</td>
      <td>0.674358</td>
      <td>0.094029</td>
      <td>2</td>
      <td>Creativity</td>
      <td>0.228663</td>
    </tr>
    <tr>
      <th>goal_kicks</th>
      <td>0.082776</td>
      <td>0.501039</td>
      <td>-0.108805</td>
      <td>2</td>
      <td>Creativity</td>
      <td>0.169894</td>
    </tr>
    <tr>
      <th>crosses_gk</th>
      <td>0.077051</td>
      <td>0.572033</td>
      <td>-0.073674</td>
      <td>2</td>
      <td>Creativity</td>
      <td>0.193966</td>
    </tr>
    <tr>
      <th>minutes</th>
      <td>0.091221</td>
      <td>0.164276</td>
      <td>0.225577</td>
      <td>3</td>
      <td>Influence</td>
      <td>0.102679</td>
    </tr>
    <tr>
      <th>def_actions_outside_pen_area_gk</th>
      <td>-0.028091</td>
      <td>-0.230739</td>
      <td>0.684753</td>
      <td>3</td>
      <td>Influence</td>
      <td>0.311688</td>
    </tr>
    <tr>
      <th>passes_throws_gk</th>
      <td>0.114960</td>
      <td>0.085186</td>
      <td>0.254461</td>
      <td>3</td>
      <td>Influence</td>
      <td>0.115826</td>
    </tr>
    <tr>
      <th>passes_gk</th>
      <td>-0.038171</td>
      <td>0.230888</td>
      <td>0.418966</td>
      <td>3</td>
      <td>Influence</td>
      <td>0.190706</td>
    </tr>
    <tr>
      <th>avg_distance_def_actions_gk</th>
      <td>-0.056693</td>
      <td>-0.319037</td>
      <td>0.613164</td>
      <td>3</td>
      <td>Influence</td>
      <td>0.279101</td>
    </tr>
  </tbody>
</table>
</div>



Finally, we can create the variables for each player over each match of the season.


```python
gk_ict = {"Influence":{"Variables":[],"Weights":[]},
         "Creativity":{"Variables":[],"Weights":[]},
         "Threat":{"Variables":[],"Weights":[]}}

for k,v in gk_ict.items():
    v['Weights'] += list(lgk[lgk['Label']==k]['weight'].values)
    v['Variables'] += list(lgk[lgk['Label']==k].index)

fbrefdata['Threat'] = 0.0
fbrefdata['Creativity'] = 0.0
fbrefdata['Influence'] = 0.0

for k,v in gk_ict.items():
    sumvalues = None
    for var,wt in zip(v['Variables'],v['Weights']):
        if (sumvalues is None):
            sumvalues = fbrefdata[fbrefdata['playerposition']=="GK"][var].values * wt
        else:
            sumvalues += fbrefdata[fbrefdata['playerposition']=="GK"][var].values * wt
    fbrefdata.loc[fbrefdata['playerposition']=="GK",k] = sumvalues
    
view = fbrefdata[fbrefdata['playerposition']=="GK"].groupby("playername")[['genid','squad','Threat','Creativity','Influence','mpcount']].mean().reset_index()
view.fillna(0,inplace=True)
view["ICT"] = (view['Threat'] + view['Creativity'] + view['Influence'])/3.0
view["ICT"] = view["ICT"] * (view["mpcount"]/34)
view['position']="GK"
```

I'm using their average over the season to keep the numbers smaller and make it easier to compare when there is fewer matches in the next season. The goal is to use this to identify players that are performing well and are undervalued by the fantasy bundesliga system.

Then I take ICT as the weighted linear combination of the three components, then divide by the sum of the weights. In this case, the weights are equal. Finally, I decided to weight the ICT by the number of games played so that players that have really good games but only played once or twice are penalized for this in their ICT.

I'm happy overall with the result. I think the top players in this list, sorted by their ICT are definitely ones that would make a top Bundesliga goalkeeper list. I was a little surprised to find Manuel Neuer lower on the list (still in the top 6). I thought he would be higher. At the same time, he is going to naturally be lower in some of the components because he is surrounded by so many good players. A good goalkeeper on a bad team will probably be ranked a little higher, because they are going to get more opportunties to save, block, and defend.


```python
view.sort_values("ICT",ascending=False)
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
      <th>playername</th>
      <th>genid</th>
      <th>Threat</th>
      <th>Creativity</th>
      <th>Influence</th>
      <th>mpcount</th>
      <th>ICT</th>
      <th>position</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>22</th>
      <td>Rafał Gikiewicz</td>
      <td>435</td>
      <td>2.779034</td>
      <td>13.824743</td>
      <td>20.470075</td>
      <td>33</td>
      <td>11.994482</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>13</th>
      <td>Lukáš Hrádecký</td>
      <td>71</td>
      <td>2.328389</td>
      <td>9.349445</td>
      <td>22.284942</td>
      <td>34</td>
      <td>11.320925</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>29</th>
      <td>Yann Sommer</td>
      <td>743</td>
      <td>2.472665</td>
      <td>8.763309</td>
      <td>21.127233</td>
      <td>34</td>
      <td>10.787736</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>27</th>
      <td>Timo Horn</td>
      <td>178</td>
      <td>2.665024</td>
      <td>10.517666</td>
      <td>18.622268</td>
      <td>34</td>
      <td>10.601653</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Jiří Pavlenka</td>
      <td>39</td>
      <td>2.933663</td>
      <td>10.418430</td>
      <td>19.229585</td>
      <td>33</td>
      <td>10.541131</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>14</th>
      <td>Manuel Neuer</td>
      <td>523</td>
      <td>1.888086</td>
      <td>6.858401</td>
      <td>23.057815</td>
      <td>33</td>
      <td>10.289627</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>18</th>
      <td>Oliver Baumann</td>
      <td>871</td>
      <td>2.721232</td>
      <td>8.975323</td>
      <td>21.306814</td>
      <td>30</td>
      <td>9.706873</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>21</th>
      <td>Péter Gulácsi</td>
      <td>718</td>
      <td>2.062170</td>
      <td>7.496594</td>
      <td>21.234887</td>
      <td>32</td>
      <td>9.660753</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>25</th>
      <td>Rune Jarstein</td>
      <td>839</td>
      <td>2.596285</td>
      <td>11.710259</td>
      <td>18.388721</td>
      <td>29</td>
      <td>9.295712</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>12</th>
      <td>Leopold Zingerle</td>
      <td>520</td>
      <td>3.152317</td>
      <td>8.735035</td>
      <td>20.663078</td>
      <td>28</td>
      <td>8.935412</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>24</th>
      <td>Roman Bürki</td>
      <td>2</td>
      <td>1.816204</td>
      <td>6.386455</td>
      <td>19.526601</td>
      <td>31</td>
      <td>8.427520</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>11</th>
      <td>Koen Casteels</td>
      <td>737</td>
      <td>2.347717</td>
      <td>10.218339</td>
      <td>20.363911</td>
      <td>26</td>
      <td>8.393913</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>0</th>
      <td>Alexander Nübel</td>
      <td>691</td>
      <td>2.542675</td>
      <td>9.385643</td>
      <td>19.911684</td>
      <td>26</td>
      <td>8.116079</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>28</th>
      <td>Tomáš Koubek</td>
      <td>252</td>
      <td>3.023924</td>
      <td>10.900556</td>
      <td>19.358909</td>
      <td>24</td>
      <td>7.831386</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Alexander Schwolow</td>
      <td>639</td>
      <td>2.624715</td>
      <td>10.979468</td>
      <td>18.805042</td>
      <td>24</td>
      <td>7.625700</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Kevin Trapp</td>
      <td>548</td>
      <td>2.709890</td>
      <td>9.831755</td>
      <td>21.044932</td>
      <td>22</td>
      <td>7.244164</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>23</th>
      <td>Robin Zentner</td>
      <td>263</td>
      <td>2.958189</td>
      <td>10.358500</td>
      <td>19.798030</td>
      <td>22</td>
      <td>7.142390</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>31</th>
      <td>Zack Steffen</td>
      <td>276</td>
      <td>3.256035</td>
      <td>10.773089</td>
      <td>19.164401</td>
      <td>17</td>
      <td>5.532254</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Florian Kastenmeier</td>
      <td>344</td>
      <td>2.628855</td>
      <td>9.808061</td>
      <td>19.988135</td>
      <td>17</td>
      <td>5.404175</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Florian Müller</td>
      <td>812</td>
      <td>2.926072</td>
      <td>9.656403</td>
      <td>19.601488</td>
      <td>13</td>
      <td>4.101878</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>15</th>
      <td>Mark Flekken</td>
      <td>49</td>
      <td>3.676202</td>
      <td>11.536737</td>
      <td>19.412469</td>
      <td>10</td>
      <td>3.394648</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Andreas Luthe</td>
      <td>685</td>
      <td>2.080820</td>
      <td>10.947191</td>
      <td>19.962344</td>
      <td>10</td>
      <td>3.234349</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Frederik Rønnow</td>
      <td>264</td>
      <td>3.009070</td>
      <td>11.021008</td>
      <td>19.714327</td>
      <td>9</td>
      <td>2.977447</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>16</th>
      <td>Markus Schubert</td>
      <td>653</td>
      <td>3.355687</td>
      <td>10.178870</td>
      <td>18.064002</td>
      <td>9</td>
      <td>2.788108</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Pavao Pervan</td>
      <td>366</td>
      <td>2.444129</td>
      <td>9.501601</td>
      <td>19.178639</td>
      <td>8</td>
      <td>2.441127</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Jannik Huth</td>
      <td>816</td>
      <td>3.250255</td>
      <td>8.115080</td>
      <td>21.042221</td>
      <td>6</td>
      <td>1.906327</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>26</th>
      <td>Thomas Kraft</td>
      <td>600</td>
      <td>2.955870</td>
      <td>12.088795</td>
      <td>19.406484</td>
      <td>4</td>
      <td>1.351025</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>20</th>
      <td>Philipp Pentke</td>
      <td>14</td>
      <td>2.747846</td>
      <td>8.615817</td>
      <td>21.525460</td>
      <td>4</td>
      <td>1.289770</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Felix Wiedwald</td>
      <td>324</td>
      <td>4.002440</td>
      <td>10.201592</td>
      <td>19.683189</td>
      <td>3</td>
      <td>0.996683</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>17</th>
      <td>Marwin Hitz</td>
      <td>268</td>
      <td>1.010328</td>
      <td>4.392318</td>
      <td>19.825880</td>
      <td>4</td>
      <td>0.989354</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Dennis Smarsch</td>
      <td>466</td>
      <td>3.178337</td>
      <td>8.656023</td>
      <td>18.102156</td>
      <td>2</td>
      <td>0.586991</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>30</th>
      <td>Yvon Mvogo</td>
      <td>114</td>
      <td>1.495871</td>
      <td>5.545668</td>
      <td>21.035249</td>
      <td>2</td>
      <td>0.550525</td>
      <td>GK</td>
    </tr>
  </tbody>
</table>
</div>



To make it easier to repeat this process I've migrated the steps into different functions.


```python
def loadingsdataframe(loadings,variables=["Influence","Creativity","Threat"]):
    loadings['Label']=""
    loadings.loc[loadings['MaxFactor']==1,"Label"] = variables[0]
    loadings.loc[loadings['MaxFactor']==2,"Label"] = variables[1]
    loadings.loc[loadings['MaxFactor']==3,"Label"] = variables[2]
    loadings.loc[loadings['MaxFactor']==1,"weight"]=perc(loadings[loadings['MaxFactor']==1][1].values)
    loadings.loc[loadings['MaxFactor']==3,"weight"]=perc(loadings[loadings['MaxFactor']==3][3].values)
    loadings.loc[loadings['MaxFactor']==2,"weight"]=perc(loadings[loadings['MaxFactor']==2][2].values)
    return loadings


def getplayers(fbrefdata,loadings,positions=["GK"]):
    gk_ict = {"Influence":{"Variables":[],"Weights":[]},
         "Creativity":{"Variables":[],"Weights":[]},
         "Threat":{"Variables":[],"Weights":[]}}

    for k,v in gk_ict.items():
        v['Weights'] += list(loadings[loadings['Label']==k]['weight'].values)
        v['Variables'] += list(loadings[loadings['Label']==k].index)

    fbrefdata['Threat'] = 0.0
    fbrefdata['Creativity'] = 0.0
    fbrefdata['Influence'] = 0.0

    for k,v in gk_ict.items():
        sumvalues = None
        for var,wt in zip(v['Variables'],v['Weights']):
            if (sumvalues is None):
                sumvalues = fbrefdata[fbrefdata['playerposition'].isin(positions)][var].values * wt
            else:
                sumvalues += fbrefdata[fbrefdata['playerposition'].isin(positions)][var].values * wt
        fbrefdata.loc[fbrefdata['playerposition'].isin(positions),k] = sumvalues

    view = fbrefdata[fbrefdata['playerposition'].isin(positions)].groupby("playername")[['genid','squad','Threat','Creativity','Influence','mpcount']].mean().reset_index()
    view.fillna(0,inplace=True)
    view["ICT"] = (view['Threat'] + view['Creativity'] + view['Influence'])/3.0
    view["ICT"] = view["ICT"] * (view["mpcount"]/34)
    view["position"] = positions[0]
    return view
```

# Defender

Now the variables for defenders, midfielders, and forwards are pretty much the same. There is a mix of the potential from a player (such as xa and xg), their actions, and their mistakes. I'll use similar variables in the factors found for the goal keeper to try and match the ICT components. For the most part these overlap in the different positions.


```python
variables = {'minutes': 'Min -- Minutes',
'goals':'Gls -- Goals scored or allowed',
'assists':'Ast -- Assists',
'xa':'xA -- xG Assisted xG which follows a pass that assists a shot',
'carry_progressive_distance':"Total distance in yards a player moved the ball while controlling it with their feet towards the opponent's goal",
'passes':"Passes Attempted",
'shots_on_target':"Shots on Target",
'blocks':"Number of times blocking the ball by standing in its path",
'touches':"Number of Times a player touched the ball (receive, dribble, pass = 1 touch)",
'passes_completed':"Passes Completed",
'pens_made':"Penalty Kicks Made", 
'sca':"Shot creating actions", 
'carries':"Number of times the player controlled the ball with their feet",
'pens_att':"Penalty Kicks Attempted",
'tackles':"Number of players tackled",
'cards_yellow':"Yellow Cards",
'shots_total':"Shots Total",
'xg':"Expected Goals", 
'pressures':"Number of times applying pressure to opposing player who is receiving, carrying or releasing the ball", 
'dribbles':"dribbles attempted",   
'npxg':"Non Penalty Expected Goals", 
'interceptions':"Interceptions",
'gca':"Goals creating action"}
```


```python
defenders= fbrefdata[(fbrefdata['playerposition']=='DF')|(fbrefdata['playerposition']=='DF,FW')|(fbrefdata['playerposition']=='DF,MF')][variables.keys()].copy()
defenders.dropna(thresh=6,inplace=True)
defenders.fillna(0,inplace=True)
defenders_norm=(defenders-defenders.mean())/defenders.std()
Xdf = defenders_norm.values
n_factors = 3
fa = FactorAnalyzer(n_factors=n_factors,rotation="varimax")
fa.fit(Xdf)
ldf= pd.DataFrame(fa.loadings_,index=defenders.columns,columns=range(1,n_factors+1))
ldf['MaxFactor'] = ldf[list(range(1,n_factors+1))].idxmax(axis=1)
ldf.sort_values("MaxFactor")
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
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>MaxFactor</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>minutes</th>
      <td>0.643636</td>
      <td>0.087500</td>
      <td>0.175112</td>
      <td>1</td>
    </tr>
    <tr>
      <th>cards_yellow</th>
      <td>0.041674</td>
      <td>-0.009024</td>
      <td>-0.006864</td>
      <td>1</td>
    </tr>
    <tr>
      <th>tackles</th>
      <td>0.249532</td>
      <td>0.023928</td>
      <td>0.095873</td>
      <td>1</td>
    </tr>
    <tr>
      <th>carries</th>
      <td>0.947986</td>
      <td>0.012896</td>
      <td>0.058707</td>
      <td>1</td>
    </tr>
    <tr>
      <th>interceptions</th>
      <td>0.217574</td>
      <td>0.019628</td>
      <td>-0.025200</td>
      <td>1</td>
    </tr>
    <tr>
      <th>touches</th>
      <td>0.994516</td>
      <td>0.028253</td>
      <td>0.112791</td>
      <td>1</td>
    </tr>
    <tr>
      <th>blocks</th>
      <td>0.226777</td>
      <td>0.023025</td>
      <td>0.096388</td>
      <td>1</td>
    </tr>
    <tr>
      <th>passes_completed</th>
      <td>0.945034</td>
      <td>-0.025643</td>
      <td>0.006500</td>
      <td>1</td>
    </tr>
    <tr>
      <th>passes</th>
      <td>0.975411</td>
      <td>-0.010433</td>
      <td>0.084485</td>
      <td>1</td>
    </tr>
    <tr>
      <th>carry_progressive_distance</th>
      <td>0.729271</td>
      <td>0.045795</td>
      <td>0.141527</td>
      <td>1</td>
    </tr>
    <tr>
      <th>pressures</th>
      <td>0.262062</td>
      <td>0.077233</td>
      <td>0.219850</td>
      <td>1</td>
    </tr>
    <tr>
      <th>xg</th>
      <td>0.043953</td>
      <td>0.942113</td>
      <td>0.046355</td>
      <td>2</td>
    </tr>
    <tr>
      <th>pens_made</th>
      <td>-0.016983</td>
      <td>0.187393</td>
      <td>0.018120</td>
      <td>2</td>
    </tr>
    <tr>
      <th>pens_att</th>
      <td>-0.012025</td>
      <td>0.188043</td>
      <td>0.008011</td>
      <td>2</td>
    </tr>
    <tr>
      <th>npxg</th>
      <td>0.051818</td>
      <td>0.881529</td>
      <td>0.052811</td>
      <td>2</td>
    </tr>
    <tr>
      <th>goals</th>
      <td>0.006784</td>
      <td>0.613660</td>
      <td>0.000146</td>
      <td>2</td>
    </tr>
    <tr>
      <th>shots_total</th>
      <td>0.141182</td>
      <td>0.653492</td>
      <td>0.206122</td>
      <td>2</td>
    </tr>
    <tr>
      <th>shots_on_target</th>
      <td>0.052371</td>
      <td>0.667652</td>
      <td>0.114568</td>
      <td>2</td>
    </tr>
    <tr>
      <th>dribbles</th>
      <td>0.173738</td>
      <td>0.109275</td>
      <td>0.344677</td>
      <td>3</td>
    </tr>
    <tr>
      <th>sca</th>
      <td>0.183629</td>
      <td>0.129986</td>
      <td>0.616743</td>
      <td>3</td>
    </tr>
    <tr>
      <th>assists</th>
      <td>-0.032618</td>
      <td>0.013015</td>
      <td>0.708685</td>
      <td>3</td>
    </tr>
    <tr>
      <th>xa</th>
      <td>0.054075</td>
      <td>0.032768</td>
      <td>0.702174</td>
      <td>3</td>
    </tr>
    <tr>
      <th>gca</th>
      <td>0.018661</td>
      <td>0.059090</td>
      <td>0.709957</td>
      <td>3</td>
    </tr>
  </tbody>
</table>
</div>




```python
ldf = loadingsdataframe(ldf,["Influence","Threat","Creativity"])
ldf.sort_values("MaxFactor")
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
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>MaxFactor</th>
      <th>Label</th>
      <th>weight</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>minutes</th>
      <td>0.643636</td>
      <td>0.087500</td>
      <td>0.175112</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.103255</td>
    </tr>
    <tr>
      <th>cards_yellow</th>
      <td>0.041674</td>
      <td>-0.009024</td>
      <td>-0.006864</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.006685</td>
    </tr>
    <tr>
      <th>tackles</th>
      <td>0.249532</td>
      <td>0.023928</td>
      <td>0.095873</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.040031</td>
    </tr>
    <tr>
      <th>carries</th>
      <td>0.947986</td>
      <td>0.012896</td>
      <td>0.058707</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.152080</td>
    </tr>
    <tr>
      <th>interceptions</th>
      <td>0.217574</td>
      <td>0.019628</td>
      <td>-0.025200</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.034904</td>
    </tr>
    <tr>
      <th>touches</th>
      <td>0.994516</td>
      <td>0.028253</td>
      <td>0.112791</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.159544</td>
    </tr>
    <tr>
      <th>blocks</th>
      <td>0.226777</td>
      <td>0.023025</td>
      <td>0.096388</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.036381</td>
    </tr>
    <tr>
      <th>passes_completed</th>
      <td>0.945034</td>
      <td>-0.025643</td>
      <td>0.006500</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.151606</td>
    </tr>
    <tr>
      <th>passes</th>
      <td>0.975411</td>
      <td>-0.010433</td>
      <td>0.084485</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.156480</td>
    </tr>
    <tr>
      <th>carry_progressive_distance</th>
      <td>0.729271</td>
      <td>0.045795</td>
      <td>0.141527</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.116993</td>
    </tr>
    <tr>
      <th>pressures</th>
      <td>0.262062</td>
      <td>0.077233</td>
      <td>0.219850</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.042041</td>
    </tr>
    <tr>
      <th>xg</th>
      <td>0.043953</td>
      <td>0.942113</td>
      <td>0.046355</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.227900</td>
    </tr>
    <tr>
      <th>pens_made</th>
      <td>-0.016983</td>
      <td>0.187393</td>
      <td>0.018120</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.045331</td>
    </tr>
    <tr>
      <th>pens_att</th>
      <td>-0.012025</td>
      <td>0.188043</td>
      <td>0.008011</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.045488</td>
    </tr>
    <tr>
      <th>npxg</th>
      <td>0.051818</td>
      <td>0.881529</td>
      <td>0.052811</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.213245</td>
    </tr>
    <tr>
      <th>goals</th>
      <td>0.006784</td>
      <td>0.613660</td>
      <td>0.000146</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.148447</td>
    </tr>
    <tr>
      <th>shots_total</th>
      <td>0.141182</td>
      <td>0.653492</td>
      <td>0.206122</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.158082</td>
    </tr>
    <tr>
      <th>shots_on_target</th>
      <td>0.052371</td>
      <td>0.667652</td>
      <td>0.114568</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.161507</td>
    </tr>
    <tr>
      <th>dribbles</th>
      <td>0.173738</td>
      <td>0.109275</td>
      <td>0.344677</td>
      <td>3</td>
      <td>Creativity</td>
      <td>0.111827</td>
    </tr>
    <tr>
      <th>sca</th>
      <td>0.183629</td>
      <td>0.129986</td>
      <td>0.616743</td>
      <td>3</td>
      <td>Creativity</td>
      <td>0.200096</td>
    </tr>
    <tr>
      <th>assists</th>
      <td>-0.032618</td>
      <td>0.013015</td>
      <td>0.708685</td>
      <td>3</td>
      <td>Creativity</td>
      <td>0.229925</td>
    </tr>
    <tr>
      <th>xa</th>
      <td>0.054075</td>
      <td>0.032768</td>
      <td>0.702174</td>
      <td>3</td>
      <td>Creativity</td>
      <td>0.227813</td>
    </tr>
    <tr>
      <th>gca</th>
      <td>0.018661</td>
      <td>0.059090</td>
      <td>0.709957</td>
      <td>3</td>
      <td>Creativity</td>
      <td>0.230338</td>
    </tr>
  </tbody>
</table>
</div>




```python
viewdf = getplayers(fbrefdata,ldf,positions=["DF","DF,FW","DF,MF"])
viewdf.sort_values("ICT")
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
      <th>playername</th>
      <th>genid</th>
      <th>Threat</th>
      <th>Creativity</th>
      <th>Influence</th>
      <th>mpcount</th>
      <th>ICT</th>
      <th>position</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>121</th>
      <td>Philipp Lienhart</td>
      <td>129</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>11</td>
      <td>0.000000</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>96</th>
      <td>Melayro Bogarde</td>
      <td>288</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>15.430075</td>
      <td>2</td>
      <td>0.302550</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>34</th>
      <td>Georg Teigl</td>
      <td>884</td>
      <td>0.067399</td>
      <td>0.037276</td>
      <td>12.765404</td>
      <td>3</td>
      <td>0.378532</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>66</th>
      <td>Louis Beyer</td>
      <td>801</td>
      <td>0.000000</td>
      <td>0.103974</td>
      <td>14.469454</td>
      <td>3</td>
      <td>0.428630</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>78</th>
      <td>Marcel Schmelzer</td>
      <td>889</td>
      <td>0.127258</td>
      <td>0.129431</td>
      <td>6.354262</td>
      <td>7</td>
      <td>0.453693</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>93</th>
      <td>Matthias Ginter</td>
      <td>122</td>
      <td>0.160916</td>
      <td>0.238869</td>
      <td>74.264329</td>
      <td>31</td>
      <td>22.692035</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>92</th>
      <td>Mats Hummels</td>
      <td>704</td>
      <td>0.165684</td>
      <td>0.251442</td>
      <td>76.098054</td>
      <td>31</td>
      <td>23.254613</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Benjamin Pavard</td>
      <td>855</td>
      <td>0.178305</td>
      <td>0.475883</td>
      <td>74.607182</td>
      <td>32</td>
      <td>23.611410</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>23</th>
      <td>David Alaba</td>
      <td>384</td>
      <td>0.156756</td>
      <td>0.354875</td>
      <td>93.897345</td>
      <td>28</td>
      <td>25.916189</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Achraf Hakimi</td>
      <td>58</td>
      <td>0.350534</td>
      <td>1.112620</td>
      <td>79.723300</td>
      <td>33</td>
      <td>26.266206</td>
      <td>DF</td>
    </tr>
  </tbody>
</table>
<p>153 rows × 8 columns</p>
</div>



Who were the top defenders according to the index? These seem to align with what I might expect:  Hakimi, Alaba, Pavard, Hummels, etc. These are certainly some of the more expensive defenders in Bundesliga fantasy, so I think this passes the eyeball test to an extent.


```python
viewdf.sort_values("ICT").tail(10)
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
      <th>playername</th>
      <th>genid</th>
      <th>Threat</th>
      <th>Creativity</th>
      <th>Influence</th>
      <th>mpcount</th>
      <th>ICT</th>
      <th>position</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>5</th>
      <td>Alphonso Davies</td>
      <td>420</td>
      <td>0.140561</td>
      <td>1.116033</td>
      <td>70.953954</td>
      <td>29</td>
      <td>20.530450</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>123</th>
      <td>Raphaël Guerreiro</td>
      <td>787</td>
      <td>0.404902</td>
      <td>0.848376</td>
      <td>73.760362</td>
      <td>29</td>
      <td>21.327407</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>32</th>
      <td>Filip Kostić</td>
      <td>570</td>
      <td>0.639641</td>
      <td>1.605070</td>
      <td>63.776919</td>
      <td>33</td>
      <td>21.359939</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>24</th>
      <td>Dayot Upamecano</td>
      <td>676</td>
      <td>0.128897</td>
      <td>0.390083</td>
      <td>79.966281</td>
      <td>28</td>
      <td>22.093993</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>138</th>
      <td>Sven Bender</td>
      <td>672</td>
      <td>0.130842</td>
      <td>0.116697</td>
      <td>68.263874</td>
      <td>33</td>
      <td>22.165457</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>93</th>
      <td>Matthias Ginter</td>
      <td>122</td>
      <td>0.160916</td>
      <td>0.238869</td>
      <td>74.264329</td>
      <td>31</td>
      <td>22.692035</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>92</th>
      <td>Mats Hummels</td>
      <td>704</td>
      <td>0.165684</td>
      <td>0.251442</td>
      <td>76.098054</td>
      <td>31</td>
      <td>23.254613</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Benjamin Pavard</td>
      <td>855</td>
      <td>0.178305</td>
      <td>0.475883</td>
      <td>74.607182</td>
      <td>32</td>
      <td>23.611410</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>23</th>
      <td>David Alaba</td>
      <td>384</td>
      <td>0.156756</td>
      <td>0.354875</td>
      <td>93.897345</td>
      <td>28</td>
      <td>25.916189</td>
      <td>DF</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Achraf Hakimi</td>
      <td>58</td>
      <td>0.350534</td>
      <td>1.112620</td>
      <td>79.723300</td>
      <td>33</td>
      <td>26.266206</td>
      <td>DF</td>
    </tr>
  </tbody>
</table>
</div>



# Midfielders


```python
mf= fbrefdata[(fbrefdata['playerposition']=='MF')|(fbrefdata['playerposition']=='MF,FW')|(fbrefdata['playerposition']=='MF,DF')][variables.keys()].copy()
mf.dropna(thresh=6,inplace=True)
mf.fillna(0,inplace=True)
mf_norm=(mf-mf.mean())/mf.std()
Xmf = mf_norm.values
n_factors = 3
fa = FactorAnalyzer(n_factors=n_factors,rotation="varimax")
fa.fit(Xmf)
lmf = pd.DataFrame(fa.loadings_,index=defenders.columns,columns=range(1,n_factors+1))
lmf['MaxFactor'] = lmf[list(range(1,n_factors+1))].idxmax(axis=1)
lmf.sort_values("MaxFactor")
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
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>MaxFactor</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>minutes</th>
      <td>0.779002</td>
      <td>0.275198</td>
      <td>0.014065</td>
      <td>1</td>
    </tr>
    <tr>
      <th>pressures</th>
      <td>0.483913</td>
      <td>0.177320</td>
      <td>0.021377</td>
      <td>1</td>
    </tr>
    <tr>
      <th>carry_progressive_distance</th>
      <td>0.657368</td>
      <td>0.310056</td>
      <td>-0.018011</td>
      <td>1</td>
    </tr>
    <tr>
      <th>passes</th>
      <td>0.935528</td>
      <td>0.155432</td>
      <td>-0.004728</td>
      <td>1</td>
    </tr>
    <tr>
      <th>blocks</th>
      <td>0.364032</td>
      <td>0.063049</td>
      <td>0.010960</td>
      <td>1</td>
    </tr>
    <tr>
      <th>touches</th>
      <td>0.968655</td>
      <td>0.219807</td>
      <td>0.000873</td>
      <td>1</td>
    </tr>
    <tr>
      <th>passes_completed</th>
      <td>0.899946</td>
      <td>0.122830</td>
      <td>-0.006660</td>
      <td>1</td>
    </tr>
    <tr>
      <th>interceptions</th>
      <td>0.379786</td>
      <td>-0.058915</td>
      <td>-0.002342</td>
      <td>1</td>
    </tr>
    <tr>
      <th>carries</th>
      <td>0.906263</td>
      <td>0.249822</td>
      <td>-0.006827</td>
      <td>1</td>
    </tr>
    <tr>
      <th>cards_yellow</th>
      <td>0.124491</td>
      <td>-0.044572</td>
      <td>-0.004899</td>
      <td>1</td>
    </tr>
    <tr>
      <th>tackles</th>
      <td>0.428857</td>
      <td>0.019467</td>
      <td>-0.002074</td>
      <td>1</td>
    </tr>
    <tr>
      <th>npxg</th>
      <td>-0.074334</td>
      <td>0.862221</td>
      <td>0.017063</td>
      <td>2</td>
    </tr>
    <tr>
      <th>dribbles</th>
      <td>0.273575</td>
      <td>0.317401</td>
      <td>-0.021125</td>
      <td>2</td>
    </tr>
    <tr>
      <th>xg</th>
      <td>-0.071731</td>
      <td>0.844436</td>
      <td>0.309347</td>
      <td>2</td>
    </tr>
    <tr>
      <th>shots_total</th>
      <td>0.102939</td>
      <td>0.734892</td>
      <td>-0.025213</td>
      <td>2</td>
    </tr>
    <tr>
      <th>sca</th>
      <td>0.373843</td>
      <td>0.500843</td>
      <td>0.017836</td>
      <td>2</td>
    </tr>
    <tr>
      <th>shots_on_target</th>
      <td>0.003826</td>
      <td>0.708092</td>
      <td>-0.023990</td>
      <td>2</td>
    </tr>
    <tr>
      <th>xa</th>
      <td>0.212795</td>
      <td>0.363994</td>
      <td>-0.012107</td>
      <td>2</td>
    </tr>
    <tr>
      <th>assists</th>
      <td>0.113011</td>
      <td>0.297954</td>
      <td>-0.022530</td>
      <td>2</td>
    </tr>
    <tr>
      <th>goals</th>
      <td>-0.023062</td>
      <td>0.566233</td>
      <td>0.193045</td>
      <td>2</td>
    </tr>
    <tr>
      <th>gca</th>
      <td>0.156927</td>
      <td>0.373668</td>
      <td>0.036101</td>
      <td>2</td>
    </tr>
    <tr>
      <th>pens_made</th>
      <td>0.007857</td>
      <td>0.098202</td>
      <td>0.903337</td>
      <td>3</td>
    </tr>
    <tr>
      <th>pens_att</th>
      <td>0.008449</td>
      <td>0.084958</td>
      <td>0.955446</td>
      <td>3</td>
    </tr>
  </tbody>
</table>
</div>




```python
lmf = loadingsdataframe(lmf,["Influence","Threat","Creativity"])
lmf.sort_values("MaxFactor")
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
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>MaxFactor</th>
      <th>Label</th>
      <th>weight</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>minutes</th>
      <td>0.779002</td>
      <td>0.275198</td>
      <td>0.014065</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.112445</td>
    </tr>
    <tr>
      <th>pressures</th>
      <td>0.483913</td>
      <td>0.177320</td>
      <td>0.021377</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.069850</td>
    </tr>
    <tr>
      <th>carry_progressive_distance</th>
      <td>0.657368</td>
      <td>0.310056</td>
      <td>-0.018011</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.094888</td>
    </tr>
    <tr>
      <th>passes</th>
      <td>0.935528</td>
      <td>0.155432</td>
      <td>-0.004728</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.135039</td>
    </tr>
    <tr>
      <th>blocks</th>
      <td>0.364032</td>
      <td>0.063049</td>
      <td>0.010960</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.052546</td>
    </tr>
    <tr>
      <th>touches</th>
      <td>0.968655</td>
      <td>0.219807</td>
      <td>0.000873</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.139821</td>
    </tr>
    <tr>
      <th>passes_completed</th>
      <td>0.899946</td>
      <td>0.122830</td>
      <td>-0.006660</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.129903</td>
    </tr>
    <tr>
      <th>interceptions</th>
      <td>0.379786</td>
      <td>-0.058915</td>
      <td>-0.002342</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.054820</td>
    </tr>
    <tr>
      <th>carries</th>
      <td>0.906263</td>
      <td>0.249822</td>
      <td>-0.006827</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.130815</td>
    </tr>
    <tr>
      <th>cards_yellow</th>
      <td>0.124491</td>
      <td>-0.044572</td>
      <td>-0.004899</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.017970</td>
    </tr>
    <tr>
      <th>tackles</th>
      <td>0.428857</td>
      <td>0.019467</td>
      <td>-0.002074</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.061903</td>
    </tr>
    <tr>
      <th>npxg</th>
      <td>-0.074334</td>
      <td>0.862221</td>
      <td>0.017063</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.154805</td>
    </tr>
    <tr>
      <th>dribbles</th>
      <td>0.273575</td>
      <td>0.317401</td>
      <td>-0.021125</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.056987</td>
    </tr>
    <tr>
      <th>xg</th>
      <td>-0.071731</td>
      <td>0.844436</td>
      <td>0.309347</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.151611</td>
    </tr>
    <tr>
      <th>shots_total</th>
      <td>0.102939</td>
      <td>0.734892</td>
      <td>-0.025213</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.131944</td>
    </tr>
    <tr>
      <th>sca</th>
      <td>0.373843</td>
      <td>0.500843</td>
      <td>0.017836</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.089922</td>
    </tr>
    <tr>
      <th>shots_on_target</th>
      <td>0.003826</td>
      <td>0.708092</td>
      <td>-0.023990</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.127132</td>
    </tr>
    <tr>
      <th>xa</th>
      <td>0.212795</td>
      <td>0.363994</td>
      <td>-0.012107</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.065352</td>
    </tr>
    <tr>
      <th>assists</th>
      <td>0.113011</td>
      <td>0.297954</td>
      <td>-0.022530</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.053495</td>
    </tr>
    <tr>
      <th>goals</th>
      <td>-0.023062</td>
      <td>0.566233</td>
      <td>0.193045</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.101663</td>
    </tr>
    <tr>
      <th>gca</th>
      <td>0.156927</td>
      <td>0.373668</td>
      <td>0.036101</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.067089</td>
    </tr>
    <tr>
      <th>pens_made</th>
      <td>0.007857</td>
      <td>0.098202</td>
      <td>0.903337</td>
      <td>3</td>
      <td>Creativity</td>
      <td>0.485983</td>
    </tr>
    <tr>
      <th>pens_att</th>
      <td>0.008449</td>
      <td>0.084958</td>
      <td>0.955446</td>
      <td>3</td>
      <td>Creativity</td>
      <td>0.514017</td>
    </tr>
  </tbody>
</table>
</div>




```python
viewmf = getplayers(fbrefdata,lfw,positions=["MF","MF,FW","MF,DF"])

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
      <th>playername</th>
      <th>genid</th>
      <th>Threat</th>
      <th>Creativity</th>
      <th>Influence</th>
      <th>mpcount</th>
      <th>ICT</th>
      <th>position</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>106</th>
      <td>Martin Harnik</td>
      <td>626</td>
      <td>0.008820</td>
      <td>0.000000</td>
      <td>1.426548</td>
      <td>2</td>
      <td>0.028144</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>93</th>
      <td>Mamadou Doucouré</td>
      <td>852</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>2.043588</td>
      <td>2</td>
      <td>0.040070</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>80</th>
      <td>Lazar Samardzic</td>
      <td>128</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>4.042582</td>
      <td>3</td>
      <td>0.118899</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>72</th>
      <td>Kelvin Ofori</td>
      <td>825</td>
      <td>0.090928</td>
      <td>0.000000</td>
      <td>11.203527</td>
      <td>2</td>
      <td>0.221460</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>87</th>
      <td>Lucas</td>
      <td>379</td>
      <td>0.387805</td>
      <td>0.000000</td>
      <td>11.633740</td>
      <td>2</td>
      <td>0.235717</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>139</th>
      <td>Thiago Alcántara</td>
      <td>723</td>
      <td>0.275116</td>
      <td>0.000000</td>
      <td>50.312235</td>
      <td>24</td>
      <td>11.902906</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>67</th>
      <td>Julian Brandt</td>
      <td>856</td>
      <td>0.332270</td>
      <td>0.000000</td>
      <td>37.410594</td>
      <td>33</td>
      <td>12.210927</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>70</th>
      <td>Kai Havertz</td>
      <td>184</td>
      <td>0.706790</td>
      <td>0.033333</td>
      <td>42.129788</td>
      <td>30</td>
      <td>12.608798</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>48</th>
      <td>Florian Grillitsch</td>
      <td>158</td>
      <td>0.124850</td>
      <td>0.000000</td>
      <td>43.373946</td>
      <td>31</td>
      <td>13.220222</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>61</th>
      <td>Joshua Kimmich</td>
      <td>213</td>
      <td>0.269447</td>
      <td>0.000000</td>
      <td>57.036778</td>
      <td>33</td>
      <td>18.540249</td>
      <td>MF</td>
    </tr>
  </tbody>
</table>
<p>149 rows × 8 columns</p>
</div>



Again these pass the sniff test. Alcántara and Havertz have certainly been sought after players during the open transfer window.


```python
viewmf.sort_values("ICT").tail(10)
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
      <th>playername</th>
      <th>genid</th>
      <th>Threat</th>
      <th>Creativity</th>
      <th>Influence</th>
      <th>mpcount</th>
      <th>ICT</th>
      <th>position</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>107</th>
      <td>Maximilian Arnold</td>
      <td>93</td>
      <td>0.499166</td>
      <td>0.000000</td>
      <td>33.768048</td>
      <td>33</td>
      <td>11.086452</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>96</th>
      <td>Marcel Sabitzer</td>
      <td>524</td>
      <td>0.693408</td>
      <td>0.000000</td>
      <td>34.979957</td>
      <td>32</td>
      <td>11.191644</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>115</th>
      <td>Nicolas Höfler</td>
      <td>319</td>
      <td>0.204870</td>
      <td>0.000000</td>
      <td>36.233511</td>
      <td>32</td>
      <td>11.431649</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>108</th>
      <td>Maximilian Eggestein</td>
      <td>307</td>
      <td>0.346587</td>
      <td>0.000000</td>
      <td>36.508989</td>
      <td>32</td>
      <td>11.562534</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>13</th>
      <td>Axel Witsel</td>
      <td>31</td>
      <td>0.288352</td>
      <td>0.000000</td>
      <td>42.844560</td>
      <td>28</td>
      <td>11.840407</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>139</th>
      <td>Thiago Alcántara</td>
      <td>723</td>
      <td>0.275116</td>
      <td>0.000000</td>
      <td>50.312235</td>
      <td>24</td>
      <td>11.902906</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>67</th>
      <td>Julian Brandt</td>
      <td>856</td>
      <td>0.332270</td>
      <td>0.000000</td>
      <td>37.410594</td>
      <td>33</td>
      <td>12.210927</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>70</th>
      <td>Kai Havertz</td>
      <td>184</td>
      <td>0.706790</td>
      <td>0.033333</td>
      <td>42.129788</td>
      <td>30</td>
      <td>12.608798</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>48</th>
      <td>Florian Grillitsch</td>
      <td>158</td>
      <td>0.124850</td>
      <td>0.000000</td>
      <td>43.373946</td>
      <td>31</td>
      <td>13.220222</td>
      <td>MF</td>
    </tr>
    <tr>
      <th>61</th>
      <td>Joshua Kimmich</td>
      <td>213</td>
      <td>0.269447</td>
      <td>0.000000</td>
      <td>57.036778</td>
      <td>33</td>
      <td>18.540249</td>
      <td>MF</td>
    </tr>
  </tbody>
</table>
</div>



# Forward


```python
fw= fbrefdata[(fbrefdata['playerposition']=='FW')|(fbrefdata['playerposition']=='FW,MF')|(fbrefdata['playerposition']=='FW,DF')][variables.keys()].copy()
fw.dropna(thresh=6,inplace=True)
fw.fillna(0,inplace=True)
fw_norm=(fw-fw.mean())/fw.std()
Xfw = fw_norm.values
n_factors = 3
fa = FactorAnalyzer(n_factors=n_factors,rotation="varimax")
fa.fit(Xfw)
lfw = pd.DataFrame(fa.loadings_,index=defenders.columns,columns=range(1,n_factors+1))
lfw['MaxFactor'] = lfw[list(range(1,n_factors+1))].idxmax(axis=1)
lfw.sort_values("MaxFactor")
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
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>MaxFactor</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>minutes</th>
      <td>0.714773</td>
      <td>0.309670</td>
      <td>0.061387</td>
      <td>1</td>
    </tr>
    <tr>
      <th>dribbles</th>
      <td>0.586149</td>
      <td>0.105536</td>
      <td>0.019103</td>
      <td>1</td>
    </tr>
    <tr>
      <th>pressures</th>
      <td>0.476916</td>
      <td>0.152041</td>
      <td>0.057936</td>
      <td>1</td>
    </tr>
    <tr>
      <th>tackles</th>
      <td>0.368905</td>
      <td>-0.019179</td>
      <td>0.009095</td>
      <td>1</td>
    </tr>
    <tr>
      <th>carries</th>
      <td>0.943461</td>
      <td>0.192870</td>
      <td>0.020960</td>
      <td>1</td>
    </tr>
    <tr>
      <th>interceptions</th>
      <td>0.263230</td>
      <td>-0.024448</td>
      <td>0.011216</td>
      <td>1</td>
    </tr>
    <tr>
      <th>passes_completed</th>
      <td>0.891627</td>
      <td>0.159505</td>
      <td>0.026285</td>
      <td>1</td>
    </tr>
    <tr>
      <th>touches</th>
      <td>0.947482</td>
      <td>0.242889</td>
      <td>0.040115</td>
      <td>1</td>
    </tr>
    <tr>
      <th>sca</th>
      <td>0.602390</td>
      <td>0.320099</td>
      <td>0.002632</td>
      <td>1</td>
    </tr>
    <tr>
      <th>passes</th>
      <td>0.922081</td>
      <td>0.160191</td>
      <td>0.029356</td>
      <td>1</td>
    </tr>
    <tr>
      <th>carry_progressive_distance</th>
      <td>0.751659</td>
      <td>0.134326</td>
      <td>-0.016110</td>
      <td>1</td>
    </tr>
    <tr>
      <th>xa</th>
      <td>0.376583</td>
      <td>0.208368</td>
      <td>-0.055827</td>
      <td>1</td>
    </tr>
    <tr>
      <th>assists</th>
      <td>0.275699</td>
      <td>0.128294</td>
      <td>-0.060037</td>
      <td>1</td>
    </tr>
    <tr>
      <th>blocks</th>
      <td>0.340433</td>
      <td>0.065637</td>
      <td>0.032988</td>
      <td>1</td>
    </tr>
    <tr>
      <th>gca</th>
      <td>0.320011</td>
      <td>0.243849</td>
      <td>0.012237</td>
      <td>1</td>
    </tr>
    <tr>
      <th>shots_on_target</th>
      <td>0.199241</td>
      <td>0.769464</td>
      <td>-0.026866</td>
      <td>2</td>
    </tr>
    <tr>
      <th>cards_yellow</th>
      <td>0.026335</td>
      <td>0.072455</td>
      <td>0.042907</td>
      <td>2</td>
    </tr>
    <tr>
      <th>shots_total</th>
      <td>0.326092</td>
      <td>0.746960</td>
      <td>-0.040657</td>
      <td>2</td>
    </tr>
    <tr>
      <th>xg</th>
      <td>0.102496</td>
      <td>0.910550</td>
      <td>0.288081</td>
      <td>2</td>
    </tr>
    <tr>
      <th>goals</th>
      <td>0.099584</td>
      <td>0.675220</td>
      <td>0.224776</td>
      <td>2</td>
    </tr>
    <tr>
      <th>npxg</th>
      <td>0.114034</td>
      <td>0.932782</td>
      <td>-0.047853</td>
      <td>2</td>
    </tr>
    <tr>
      <th>pens_made</th>
      <td>0.002318</td>
      <td>0.150833</td>
      <td>0.930483</td>
      <td>3</td>
    </tr>
    <tr>
      <th>pens_att</th>
      <td>0.008267</td>
      <td>0.148129</td>
      <td>0.942086</td>
      <td>3</td>
    </tr>
  </tbody>
</table>
</div>




```python
lfw = loadingsdataframe(lfw,["Influence","Threat","Creativity"])
lfw.sort_values("MaxFactor")
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
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>MaxFactor</th>
      <th>Label</th>
      <th>weight</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>minutes</th>
      <td>0.714773</td>
      <td>0.309670</td>
      <td>0.061387</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.081396</td>
    </tr>
    <tr>
      <th>dribbles</th>
      <td>0.586149</td>
      <td>0.105536</td>
      <td>0.019103</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.066749</td>
    </tr>
    <tr>
      <th>pressures</th>
      <td>0.476916</td>
      <td>0.152041</td>
      <td>0.057936</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.054310</td>
    </tr>
    <tr>
      <th>tackles</th>
      <td>0.368905</td>
      <td>-0.019179</td>
      <td>0.009095</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.042010</td>
    </tr>
    <tr>
      <th>carries</th>
      <td>0.943461</td>
      <td>0.192870</td>
      <td>0.020960</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.107439</td>
    </tr>
    <tr>
      <th>interceptions</th>
      <td>0.263230</td>
      <td>-0.024448</td>
      <td>0.011216</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.029976</td>
    </tr>
    <tr>
      <th>passes_completed</th>
      <td>0.891627</td>
      <td>0.159505</td>
      <td>0.026285</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.101536</td>
    </tr>
    <tr>
      <th>touches</th>
      <td>0.947482</td>
      <td>0.242889</td>
      <td>0.040115</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.107896</td>
    </tr>
    <tr>
      <th>sca</th>
      <td>0.602390</td>
      <td>0.320099</td>
      <td>0.002632</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.068598</td>
    </tr>
    <tr>
      <th>passes</th>
      <td>0.922081</td>
      <td>0.160191</td>
      <td>0.029356</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.105004</td>
    </tr>
    <tr>
      <th>carry_progressive_distance</th>
      <td>0.751659</td>
      <td>0.134326</td>
      <td>-0.016110</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.085597</td>
    </tr>
    <tr>
      <th>xa</th>
      <td>0.376583</td>
      <td>0.208368</td>
      <td>-0.055827</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.042884</td>
    </tr>
    <tr>
      <th>assists</th>
      <td>0.275699</td>
      <td>0.128294</td>
      <td>-0.060037</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.031396</td>
    </tr>
    <tr>
      <th>blocks</th>
      <td>0.340433</td>
      <td>0.065637</td>
      <td>0.032988</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.038768</td>
    </tr>
    <tr>
      <th>gca</th>
      <td>0.320011</td>
      <td>0.243849</td>
      <td>0.012237</td>
      <td>1</td>
      <td>Influence</td>
      <td>0.036442</td>
    </tr>
    <tr>
      <th>shots_on_target</th>
      <td>0.199241</td>
      <td>0.769464</td>
      <td>-0.026866</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.187335</td>
    </tr>
    <tr>
      <th>cards_yellow</th>
      <td>0.026335</td>
      <td>0.072455</td>
      <td>0.042907</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.017640</td>
    </tr>
    <tr>
      <th>shots_total</th>
      <td>0.326092</td>
      <td>0.746960</td>
      <td>-0.040657</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.181856</td>
    </tr>
    <tr>
      <th>xg</th>
      <td>0.102496</td>
      <td>0.910550</td>
      <td>0.288081</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.221684</td>
    </tr>
    <tr>
      <th>goals</th>
      <td>0.099584</td>
      <td>0.675220</td>
      <td>0.224776</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.164390</td>
    </tr>
    <tr>
      <th>npxg</th>
      <td>0.114034</td>
      <td>0.932782</td>
      <td>-0.047853</td>
      <td>2</td>
      <td>Threat</td>
      <td>0.227096</td>
    </tr>
    <tr>
      <th>pens_made</th>
      <td>0.002318</td>
      <td>0.150833</td>
      <td>0.930483</td>
      <td>3</td>
      <td>Creativity</td>
      <td>0.496902</td>
    </tr>
    <tr>
      <th>pens_att</th>
      <td>0.008267</td>
      <td>0.148129</td>
      <td>0.942086</td>
      <td>3</td>
      <td>Creativity</td>
      <td>0.503098</td>
    </tr>
  </tbody>
</table>
</div>




```python
viewfw = getplayers(fbrefdata,lfw,positions=["FW"])

```

Finally, the forwards. Timo Werner came out on top.


```python
viewfw.sort_values("ICT").tail(10)
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
      <th>playername</th>
      <th>genid</th>
      <th>Threat</th>
      <th>Creativity</th>
      <th>Influence</th>
      <th>mpcount</th>
      <th>ICT</th>
      <th>position</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>25</th>
      <td>Marcus Thuram</td>
      <td>117</td>
      <td>0.747791</td>
      <td>0.000000</td>
      <td>30.509925</td>
      <td>18</td>
      <td>5.516067</td>
      <td>FW</td>
    </tr>
    <tr>
      <th>21</th>
      <td>Karim Onisiwo</td>
      <td>730</td>
      <td>0.421399</td>
      <td>0.000000</td>
      <td>17.340971</td>
      <td>32</td>
      <td>5.572508</td>
      <td>FW</td>
    </tr>
    <tr>
      <th>37</th>
      <td>Rouwen Hennings</td>
      <td>888</td>
      <td>0.711584</td>
      <td>0.125000</td>
      <td>17.117079</td>
      <td>32</td>
      <td>5.632522</td>
      <td>FW</td>
    </tr>
    <tr>
      <th>23</th>
      <td>Kevin Volland</td>
      <td>63</td>
      <td>0.979511</td>
      <td>0.000000</td>
      <td>21.803281</td>
      <td>27</td>
      <td>6.030739</td>
      <td>FW</td>
    </tr>
    <tr>
      <th>38</th>
      <td>Sebastian Andersson</td>
      <td>707</td>
      <td>0.753558</td>
      <td>0.045548</td>
      <td>21.521853</td>
      <td>33</td>
      <td>7.221487</td>
      <td>FW</td>
    </tr>
    <tr>
      <th>45</th>
      <td>Wout Weghorst</td>
      <td>502</td>
      <td>0.948144</td>
      <td>0.125000</td>
      <td>22.669805</td>
      <td>32</td>
      <td>7.448768</td>
      <td>FW</td>
    </tr>
    <tr>
      <th>0</th>
      <td>Alassane Pléa</td>
      <td>819</td>
      <td>0.996086</td>
      <td>0.018633</td>
      <td>27.878135</td>
      <td>27</td>
      <td>7.648108</td>
      <td>FW</td>
    </tr>
    <tr>
      <th>36</th>
      <td>Robert Lewandowski</td>
      <td>482</td>
      <td>1.716676</td>
      <td>0.142857</td>
      <td>27.477443</td>
      <td>28</td>
      <td>8.053288</td>
      <td>FW</td>
    </tr>
    <tr>
      <th>29</th>
      <td>Milot Rashica</td>
      <td>345</td>
      <td>0.756748</td>
      <td>0.089396</td>
      <td>31.935267</td>
      <td>28</td>
      <td>8.998819</td>
      <td>FW</td>
    </tr>
    <tr>
      <th>43</th>
      <td>Timo Werner</td>
      <td>234</td>
      <td>1.364026</td>
      <td>0.088235</td>
      <td>33.187873</td>
      <td>34</td>
      <td>11.546711</td>
      <td>FW</td>
    </tr>
  </tbody>
</table>
</div>



These components seem to match well with what I would expect. The real test would be to use the Threat Creativity and Influence to try and predict the value of a player. Then I could see who is undervalued and transfer for them. That will have to be an exercise for later.


```python

```
