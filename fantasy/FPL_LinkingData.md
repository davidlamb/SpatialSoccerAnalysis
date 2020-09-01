# Using Edit Distance to Match Player Names

One of the challenges of working with publicly available datasets comes when trying to match them or join them together. There are different approaches depending on the type of data. For example, we could match by a location, or a time period, or some commonality between the datasets.

I have a dataset that I've collected from the Bundesliga fantasy website. While there is some interesting information about players, it all revolves around their points in the match. These, of course, reflect their activity, but doesn't include things like: minutes played (or played per game), the player's xG statistics, or xA, etc. All of that is useful information to evaluate the potential of a player on a fantasy team.

Luckily the fantastic website fbref has that information. So how to join them? The only real connection I have is the player's name. I also have the player's team information and position. Fbref's position information is actually more detailed than the Bundesliga's so it will be difficult to match these without a little prior clean up.

This means matching for exact names. There are two challenges: if the spelling or characters are somehow different an exact match won't find anything; if there are two players with the same name.

In the first case, we will use a different metric to find the closest match. In the second, this isn't a problem with this particular dataset. I do know Premier league data might have this problem, and if you collect data over time, you are more likely to find duplicate names that are not the same player.So you might join the name to another commonality like position or team name.


### Scraping

I admit I scraped the data, but it was done in a way that wouldn't burden their servers if I had just gone and done it by "hand" myself. That means it took a long time. I won't be sharing the bundesliga data because I don't know if that would violate their terms, and will keep it for personal use except for sharing visualizations or its use in analysis.

Fbref seems okay with scraping as long as it doesn't but a burden on their servers. I still will hold back this data, but it was relatively easy to set up using Selenium.




```python
import pandas as pd
import numpy as np
```

I'll use nltk for the natural language processing features. There are different metrics available to compare different strings. In this case I will use edit distance. Put simply, it measures the number of changes it would take to make string 2 match string 1. If the words are: bong and bonk; then the edit distance would be 1. It would take one letter change to match bonk to bong.


```python
import nltk
```

This is my fantasy dataset where I've assigned a random unique id to each player. I want to pull this ID to match the FBREF dataset. 


```python
df_ids = pd.read_csv("fantasy_id_name.csv",index_col=0)
df_ids.head()
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
      <th>Name</th>
      <th>genid</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Robert Lewandowski</td>
      <td>482</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Joshua Kimmich</td>
      <td>213</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Jadon Sancho</td>
      <td>86</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Timo Werner</td>
      <td>234</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Serge Gnabry</td>
      <td>121</td>
    </tr>
  </tbody>
</table>
</div>



This is the dataset from fbref.


```python
fbrefdata = pd.read_csv("playermatchstats.csv",index_col=0)
fbrefdata[['squad','playername','position']].head()
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
      <th>squad</th>
      <th>playername</th>
      <th>position</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Bayern Munich</td>
      <td>Manuel Neuer</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Bayern Munich</td>
      <td>Manuel Neuer</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Bayern Munich</td>
      <td>Manuel Neuer</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Bayern Munich</td>
      <td>Manuel Neuer</td>
      <td>GK</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Bayern Munich</td>
      <td>Manuel Neuer</td>
      <td>GK</td>
    </tr>
  </tbody>
</table>
</div>



### Exact match

First I will try an exact match and then use this to identify problem names. This is just a placeholder for the generic id field. I use a simple iterative brute force approach to retrieve the id if the names are equal.

I've run this without doing the str.lower() to remove the capitals and improve comparisons, and it is faster. 


```python
fbrefdata['exactgenid'] = -1
```


```python
#This isn't super efficient since there are duplicate names being processed. But there aren't that many, and only takes a few seconds to run.
#
exactmatchids = []
for idx,row in fbrefdata.iterrows():
    try:
        exactmatchids.append(df_ids[df_ids['Name'].str.lower()==row['playername'].lower()]['genid'].iloc[0])
    except:
        exactmatchids.append(-1)
exactmatchids[:5]
```




    [523, 523, 523, 523, 523]




```python
fbrefdata['exactgenid'] = exactmatchids
```

There is an obvious pattern witht the names. Most of them have accents or use different characters. The matching had problems with this.


```python
fbrefdata[fbrefdata['exactgenid']==-1]['playername'].unique()
```




    array(['Jérôme Boateng', 'Thiago Alcántara', 'Ivan Perišić',
           'Lucas Hernández', 'Javi Martínez', 'Mickaël Cuisance',
           'Raphaël Guerreiro', 'Łukasz Piszczek', 'Julian Weigl',
           'Erling Braut Håland', 'Paco Alcácer', 'Marwin Hitz',
           'Péter Gulácsi', 'Diego Demme', 'Angeliño', 'Ibrahima Konaté',
           'Yvon Mvogo', 'Marcelo Saracchi', 'Alassane Pléa', 'László Bénes',
           'Ibrahima Traoré', 'Louis Beyer', 'Mamadou Doucouré',
           'Lukáš Hrádecký', 'Charles Aránguiz', 'Aleksandar Dragović',
           'Panagiotis Retsos', 'Pavel Kadeřábek', 'Diadie Samassékou',
           'Andrej Kramarić', 'Ermin Bičakčić', 'Moanes Dabour',
           'Håvard Nordtveit', 'Jürgen Locadia', 'Kostas Stafylidis',
           'Lukas Rupp', 'Lucas', 'Jérôme Roussillon', 'John Brooks',
           'João Victor Santos Sá', 'Marcel Tisserand', 'Marin Pongračić',
           'Paulo Otávio', 'Lukas Nmecha', 'Roland Sallai', 'Amir Abrashi',
           'Kwon Chang-hoon', 'Jérôme Gondorf', 'Filip Kostić',
           "Obite N'Dicka", 'Almamy Touré', 'André Silva',
           'Gonçalo Paciência', 'Mijat Gaćinović', 'Frederik Rønnow',
           'Lucas Torró', 'Dejan Joveljić', 'Jonathan de Guzmán',
           'Marko Grujić', 'Vladimír Darida', 'Per Ciljan Skjelbred',
           'Javairô Dilrosun', 'Vedad Ibišević', 'Krzysztof Piątek',
           'Peter Pekarík', 'Santiago Ascacíbar', 'Ondrej Duda',
           'Rafał Gikiewicz', 'Neven Subotić', 'Yunus Mallı',
           'Matija Nastasić', 'Salif Sané', 'Fabian Reese', 'Levent Mercan',
           'Malick Thiaw', 'Jean-Paul Boëtius', 'Jerry St. Juste',
           'Pierre Kunde', 'Aarón Martín', 'Levin Öztunalı', 'Ádám Szalai',
           'Leandro Barreiro Martins', 'Alexandru Maxim', 'Jhon Córdoba',
           'Elvis Rexhbeçaj', 'Louis Schaub', 'Jorge Meré', 'Tomáš Koubek',
           'Ohis Felix Uduokhai', 'Alfreð Finnbogason', 'André Hahn',
           'Marek Suchý', 'Reece Oxford', 'Mads Pedersen', 'Julian Schieber',
           'Jiří Pavlenka', 'Miloš Veljković', 'Nuri Şahin', 'Josh Sargent',
           'Ömer Toprak', 'Michael Lang', 'Martin Harnik', 'André Hoffmann',
           'Markus Suttner', 'Kasim Nuhu', 'Lewis Baker', 'Opoku Ampomah',
           'Mathias Jørgensen', 'Abdelhamid Sabiri', 'Cauly Oliveira Souza',
           'Samúel Friðjónsson', 'Babacar Guèye', 'Khiry Shelton'],
          dtype=object)



That means my fantasy data may not have the correct character encoding or there may be some spelling differences. I'm going to use edit distance to compare the names in the fbref dataset to those in the fantasy dataset. The match with the smallest edit distance will be considered a match. To compare these, I'm going to vectorize the edit distance function , and pass it the array of fantasy names, and the current fbref name. THen use argmin to find the index of the smallest value.

Admitedly this is a little slower than I would like it to be.


```python
fbrefnames = fbrefdata['playername'].unique()
fantasynames = df_ids['Name'].values
```


```python
def checknames(name1,name2):
    return nltk.edit_distance(name1,name2)
```


```python
editids = []
for nm in fbrefnames:
    eds = np.vectorize(nltk.edit_distance)(nm,fantasynames)
    idxs = np.argmin(eds)
    editids.append(df_ids.iloc[idxs]['genid'])
#editids
```


```python
fbrefdata['editgenid'] = -1
fbrefdata['editname'] = ""
```


```python
for nm,gid in zip(fbrefnames,editids):
    fbrefdata.loc[fbrefdata['playername']==nm,'editgenid'] = gid
    fbrefdata.loc[fbrefdata['playername']==nm,'editname'] = df_ids[df_ids['genid'] == gid]['Name'].values[0]
```

The edit distance approache results in an id for all of the players.


```python
fbrefdata[(fbrefdata['editgenid']==-1)]
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
      <th>passes_length_avg_gk</th>
      <th>comp</th>
      <th>interceptions</th>
      <th>passes_pct</th>
      <th>dribbles</th>
      <th>match_report</th>
      <th>passes_completed_launched_gk</th>
      <th>dayofweek</th>
      <th>assists</th>
      <th>minutes</th>
      <th>...</th>
      <th>crosses_stopped_pct_gk</th>
      <th>bench_explain</th>
      <th>carries</th>
      <th>goal_kick_length_avg</th>
      <th>shots_total</th>
      <th>playername</th>
      <th>playerposition</th>
      <th>exactgenid</th>
      <th>editgenid</th>
      <th>editname</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
<p>0 rows × 66 columns</p>
</div>



We can see it did pretty well matching the player name.


```python
fbrefdata[(fbrefdata['exactgenid']==-1)][['playername','exactgenid','editgenid','editname']]
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
      <th>exactgenid</th>
      <th>editgenid</th>
      <th>editname</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>258</th>
      <td>Jérôme Boateng</td>
      <td>-1</td>
      <td>817</td>
      <td>Jerome Boateng</td>
    </tr>
    <tr>
      <th>259</th>
      <td>Jérôme Boateng</td>
      <td>-1</td>
      <td>817</td>
      <td>Jerome Boateng</td>
    </tr>
    <tr>
      <th>260</th>
      <td>Jérôme Boateng</td>
      <td>-1</td>
      <td>817</td>
      <td>Jerome Boateng</td>
    </tr>
    <tr>
      <th>261</th>
      <td>Jérôme Boateng</td>
      <td>-1</td>
      <td>817</td>
      <td>Jerome Boateng</td>
    </tr>
    <tr>
      <th>262</th>
      <td>Jérôme Boateng</td>
      <td>-1</td>
      <td>817</td>
      <td>Jerome Boateng</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>10979</th>
      <td>Khiry Shelton</td>
      <td>-1</td>
      <td>184</td>
      <td>Kai Havertz</td>
    </tr>
    <tr>
      <th>10980</th>
      <td>Khiry Shelton</td>
      <td>-1</td>
      <td>184</td>
      <td>Kai Havertz</td>
    </tr>
    <tr>
      <th>10981</th>
      <td>Khiry Shelton</td>
      <td>-1</td>
      <td>184</td>
      <td>Kai Havertz</td>
    </tr>
    <tr>
      <th>10982</th>
      <td>Khiry Shelton</td>
      <td>-1</td>
      <td>184</td>
      <td>Kai Havertz</td>
    </tr>
    <tr>
      <th>10983</th>
      <td>Khiry Shelton</td>
      <td>-1</td>
      <td>184</td>
      <td>Kai Havertz</td>
    </tr>
  </tbody>
</table>
<p>2602 rows × 4 columns</p>
</div>



The ones that don't match are just the -1 values that it could not find the exact name match.


```python
fbrefdata[(fbrefdata['editgenid']!=fbrefdata['exactgenid'])]['exactgenid'].unique()
```




    array([-1], dtype=int64)



Finally some cleanup to export with the generic id that I can then use to join the data.


```python
fbrefdata.loc[fbrefdata['editgenid']!=fbrefdata['exactgenid'],'genid'] = fbrefdata[(fbrefdata['editgenid']!=fbrefdata['exactgenid'])]['editgenid'].values
fbrefdata.loc[fbrefdata['editgenid']==fbrefdata['exactgenid'],'genid'] = fbrefdata[(fbrefdata['editgenid']==fbrefdata['exactgenid'])]['exactgenid'].values
```


```python
fbrefdata.to_csv("playermatchstatswithid.csv")
```
