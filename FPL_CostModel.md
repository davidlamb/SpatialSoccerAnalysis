
# Fantasy Premier League Value Models

I'm relatively new to the world of fantasy premier league. I only played it once during the season (the last week). I didn't have much time, but I took a data visualization approach to grab a handful of decent players for the last match. You can view it here if you would like [tableau data vis](https://public.tableau.com/views/FantasyPremierLeague2019-2020/FPLDashboard?:language=en&:display_count=y&:origin=viz_share_link).

The data for the "dashboard" came from this repo: [https://github.com/vaastav/Fantasy-Premier-League](https://github.com/vaastav/Fantasy-Premier-League).

I wanted to take this a step further and build a model. My logic behind the model is that I want to find players that fall into a few categories:

1. Their position. This changes the value\cost of the player, but you need to select a different number of these to fill your team. You don't want to price out a player that is a defender based on forward level prices.
2. Their cost\value. The millions you spend on a specific player to fill your team.
3. Their points. This is what you receive in return for buying the player.

The idea is you want to find players that give you a lot of points but are currently undervalued. As you will see, forwards tend to be expensive (they score the goals afterall). So if you can find a defender or midfielder that is good value you can save your money to be spent on substitutes and forwards.

What is good value? Let's say player x gets you 4 points per game, and player y gets you 4 points per game. They are equal, but player x costs .5 million pounds more than y. Which has better value? Player y, because they cost less.

Another way to think about this is that you estimate player y to be a 4.5 million pound player, and player x to be a 4 million pound player. They both 4 million pounds, but your model is predicting that player y should actually be more expensive. Then FPL currently undervalues player y, and they are probably a good deal. Assuming they get about the same number of points per game, and number of minutes.

There is a lot of factors that can go into this, such as playing time. If a player only plays one game and scores a goal, their points per game is massive, but that player is useless to you because they may never get to play again.

## Notes on the data

In part 2 I will create some of my own metrics from the player's data. For now I am using "players_raw" because it includes position information coded as such:

Positions:
1. goal keeper
2. defender
3. midfield
4. forward

This data is for the entire season, so we can see everything. And prepare for next season's lineup.


```python
import numpy as np
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import pandas as pd
sns.set()

%matplotlib inline
```


```python
df = pd.read_csv("players_raw.csv")
df.head()
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
      <th>assists</th>
      <th>bonus</th>
      <th>bps</th>
      <th>chance_of_playing_next_round</th>
      <th>chance_of_playing_this_round</th>
      <th>clean_sheets</th>
      <th>code</th>
      <th>cost_change_event</th>
      <th>cost_change_event_fall</th>
      <th>cost_change_start</th>
      <th>...</th>
      <th>threat_rank_type</th>
      <th>total_points</th>
      <th>transfers_in</th>
      <th>transfers_in_event</th>
      <th>transfers_out</th>
      <th>transfers_out_event</th>
      <th>value_form</th>
      <th>value_season</th>
      <th>web_name</th>
      <th>yellow_cards</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2</td>
      <td>2</td>
      <td>242</td>
      <td>0</td>
      <td>0</td>
      <td>4</td>
      <td>69140</td>
      <td>0</td>
      <td>0</td>
      <td>-4</td>
      <td>...</td>
      <td>58</td>
      <td>43</td>
      <td>25007</td>
      <td>0</td>
      <td>47630</td>
      <td>0</td>
      <td>0.3</td>
      <td>8.4</td>
      <td>Mustafi</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>4</td>
      <td>204</td>
      <td>100</td>
      <td>100</td>
      <td>4</td>
      <td>98745</td>
      <td>0</td>
      <td>0</td>
      <td>-3</td>
      <td>...</td>
      <td>81</td>
      <td>44</td>
      <td>206616</td>
      <td>0</td>
      <td>159819</td>
      <td>0</td>
      <td>0.3</td>
      <td>8.5</td>
      <td>Bellerín</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>1</td>
      <td>331</td>
      <td>100</td>
      <td>100</td>
      <td>4</td>
      <td>111457</td>
      <td>0</td>
      <td>0</td>
      <td>-3</td>
      <td>...</td>
      <td>98</td>
      <td>55</td>
      <td>65194</td>
      <td>0</td>
      <td>134275</td>
      <td>0</td>
      <td>0.5</td>
      <td>10.6</td>
      <td>Kolasinac</td>
      <td>4</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2</td>
      <td>3</td>
      <td>244</td>
      <td>100</td>
      <td>100</td>
      <td>3</td>
      <td>154043</td>
      <td>0</td>
      <td>0</td>
      <td>-5</td>
      <td>...</td>
      <td>119</td>
      <td>41</td>
      <td>610816</td>
      <td>0</td>
      <td>653555</td>
      <td>0</td>
      <td>0.1</td>
      <td>9.1</td>
      <td>Maitland-Niles</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0</td>
      <td>5</td>
      <td>305</td>
      <td>100</td>
      <td>100</td>
      <td>4</td>
      <td>39476</td>
      <td>0</td>
      <td>0</td>
      <td>-2</td>
      <td>...</td>
      <td>76</td>
      <td>57</td>
      <td>182201</td>
      <td>0</td>
      <td>231413</td>
      <td>0</td>
      <td>0.0</td>
      <td>11.9</td>
      <td>Sokratis</td>
      <td>6</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 61 columns</p>
</div>



Player position will be dummy coded for the model. We will use goalkeeper as the base category.


```python
element_types = df['element_type'].values
df = pd.get_dummies(df,columns=["element_type"],prefix="pos")
df['element_type'] = element_types
df.head()

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
      <th>assists</th>
      <th>bonus</th>
      <th>bps</th>
      <th>chance_of_playing_next_round</th>
      <th>chance_of_playing_this_round</th>
      <th>clean_sheets</th>
      <th>code</th>
      <th>cost_change_event</th>
      <th>cost_change_event_fall</th>
      <th>cost_change_start</th>
      <th>...</th>
      <th>transfers_out_event</th>
      <th>value_form</th>
      <th>value_season</th>
      <th>web_name</th>
      <th>yellow_cards</th>
      <th>pos_1</th>
      <th>pos_2</th>
      <th>pos_3</th>
      <th>pos_4</th>
      <th>element_type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2</td>
      <td>2</td>
      <td>242</td>
      <td>0</td>
      <td>0</td>
      <td>4</td>
      <td>69140</td>
      <td>0</td>
      <td>0</td>
      <td>-4</td>
      <td>...</td>
      <td>0</td>
      <td>0.3</td>
      <td>8.4</td>
      <td>Mustafi</td>
      <td>2</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>4</td>
      <td>204</td>
      <td>100</td>
      <td>100</td>
      <td>4</td>
      <td>98745</td>
      <td>0</td>
      <td>0</td>
      <td>-3</td>
      <td>...</td>
      <td>0</td>
      <td>0.3</td>
      <td>8.5</td>
      <td>Bellerín</td>
      <td>2</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>1</td>
      <td>331</td>
      <td>100</td>
      <td>100</td>
      <td>4</td>
      <td>111457</td>
      <td>0</td>
      <td>0</td>
      <td>-3</td>
      <td>...</td>
      <td>0</td>
      <td>0.5</td>
      <td>10.6</td>
      <td>Kolasinac</td>
      <td>4</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>2</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2</td>
      <td>3</td>
      <td>244</td>
      <td>100</td>
      <td>100</td>
      <td>3</td>
      <td>154043</td>
      <td>0</td>
      <td>0</td>
      <td>-5</td>
      <td>...</td>
      <td>0</td>
      <td>0.1</td>
      <td>9.1</td>
      <td>Maitland-Niles</td>
      <td>4</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>2</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0</td>
      <td>5</td>
      <td>305</td>
      <td>100</td>
      <td>100</td>
      <td>4</td>
      <td>39476</td>
      <td>0</td>
      <td>0</td>
      <td>-2</td>
      <td>...</td>
      <td>0</td>
      <td>0.0</td>
      <td>11.9</td>
      <td>Sokratis</td>
      <td>6</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>2</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 65 columns</p>
</div>



This includes all the fields I think I might use in the model, but the model will become much simpler. The dependent variable is the current cost of the player.


```python
# multilevel model teams = 'team_code'
x_fields = ['points_per_game','creativity','influence','red_cards','threat','yellow_cards','minutes','pos_2','pos_3','pos_4']
y_fields = ['now_cost']
```

The simplified dataframe for use in the model.


```python
df_copy = df[x_fields+y_fields].copy()
df_copy.head()
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
      <th>points_per_game</th>
      <th>creativity</th>
      <th>influence</th>
      <th>red_cards</th>
      <th>threat</th>
      <th>yellow_cards</th>
      <th>minutes</th>
      <th>pos_2</th>
      <th>pos_2</th>
      <th>pos_3</th>
      <th>pos_3</th>
      <th>pos_4</th>
      <th>pos_4</th>
      <th>team_code</th>
      <th>now_cost</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2.9</td>
      <td>45.5</td>
      <td>277.2</td>
      <td>0</td>
      <td>155.0</td>
      <td>2</td>
      <td>1205</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>3</td>
      <td>51</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2.9</td>
      <td>76.9</td>
      <td>187.8</td>
      <td>0</td>
      <td>103.0</td>
      <td>2</td>
      <td>1156</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>3</td>
      <td>52</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2.1</td>
      <td>182.5</td>
      <td>269.6</td>
      <td>0</td>
      <td>81.0</td>
      <td>4</td>
      <td>1694</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>3</td>
      <td>52</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2.0</td>
      <td>182.0</td>
      <td>301.8</td>
      <td>1</td>
      <td>58.0</td>
      <td>4</td>
      <td>1382</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>3</td>
      <td>45</td>
    </tr>
    <tr>
      <th>4</th>
      <td>3.0</td>
      <td>36.8</td>
      <td>436.2</td>
      <td>0</td>
      <td>110.0</td>
      <td>6</td>
      <td>1696</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>3</td>
      <td>48</td>
    </tr>
  </tbody>
</table>
</div>



It's worth doing a deeper dive into the distributions of the different variables. As we can see cost is highly skewed. This may affect the results of this model.


```python
ax = df_copy['now_cost'].hist()
ax.set_title("Cost");
```


![png](images/fpl/1output_10_0.png)


Most ofthe data is actually skewed. Red cards and yellow cards don't look to be that useful given their unbalanced in favor of no cards.


```python
for x in x_fields:
    ax = df_copy[x].hist()
    ax.set_title(x)
    plt.show()
```


![png](images/fpl/1output_12_0.png)



![png](images/fpl/1output_12_1.png)



![png](images/fpl/1output_12_2.png)



![png](images/fpl/1output_12_3.png)



![png](images/fpl/1output_12_4.png)



![png](images/fpl/1output_12_5.png)



![png](images/fpl/1output_12_6.png)



    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    <ipython-input-302-f705e735fd02> in <module>()
          1 for x in x_fields:
          2     ax = df_copy[x].hist()
    ----> 3     ax.set_title(x)
          4     plt.show()
    

    AttributeError: 'numpy.ndarray' object has no attribute 'set_title'



![png](images/fpl/1output_12_8.png)


I'll set up some transformations on a few of the variables. You might use these, but I didn't find them to be necessary in the fit of the model.


```python
x_trans = ['points_per_game','creativity','influence','red_cards','threat','yellow_cards','minutes']
for x in x_trans:
    df_copy[x+"_t"] = np.log(df_copy[x].values+1)
    ax = df_copy[x+"_t"].hist()
    ax.set_title(x)
    plt.show()

df_copy["now_cost_t"] = np.log(df_copy['now_cost'].values)
ax = df_copy["now_cost_t"].hist()
ax.set_title("Cost")
plt.show()
```


![png](images/fpl/1output_14_0.png)



![png](images/fpl/1output_14_1.png)



![png](images/fpl/1output_14_2.png)



![png](images/fpl/1output_14_3.png)



![png](images/fpl/1output_14_4.png)



![png](images/fpl/1output_14_5.png)



![png](images/fpl/1output_14_6.png)



![png](images/fpl/1output_14_7.png)


I'll also center the numeric variables for interprative reasons.


```python
x_trans = ['points_per_game','creativity','influence','threat','minutes']
for x in x_trans:
    df_copy[x+"_c"] = df_copy[x].values - df_copy[x].mean()
```


```python
results = smf.ols('now_cost ~ points_per_game + creativity + influence + red_cards + threat + yellow_cards + minutes + pos_2 + pos_3 + pos_4', data=df_copy).fit()
```

We can see the overall fit statistics of the model are pretty good. The adjusted R-Squared is relatively high, and the F-Statistic is significant. We need to review the residuals before interpreting the coefficients.


```python
print(results.summary())
```

                                OLS Regression Results                            
    ==============================================================================
    Dep. Variable:               now_cost   R-squared:                       0.666
    Model:                            OLS   Adj. R-squared:                  0.661
    Method:                 Least Squares   F-statistic:                     130.5
    Date:                Sun, 02 Aug 2020   Prob (F-statistic):          1.32e-148
    Time:                        11:14:25   Log-Likelihood:                -2229.8
    No. Observations:                 666   AIC:                             4482.
    Df Residuals:                     655   BIC:                             4531.
    Df Model:                          10                                         
    Covariance Type:            nonrobust                                         
    ===================================================================================
                          coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------
    Intercept          41.6297      0.938     44.365      0.000      39.787      43.472
    points_per_game     1.8917      0.328      5.771      0.000       1.248       2.535
    creativity          0.0065      0.002      3.585      0.000       0.003       0.010
    influence           0.0290      0.004      7.828      0.000       0.022       0.036
    red_cards           1.3642      1.008      1.354      0.176      -0.614       3.343
    threat              0.0167      0.001     11.349      0.000       0.014       0.020
    yellow_cards        0.0408      0.165      0.247      0.805      -0.284       0.365
    minutes            -0.0078      0.001     -8.835      0.000      -0.010      -0.006
    pos_2[0]           -0.3223      0.497     -0.648      0.517      -1.299       0.654
    pos_2[1]           -0.3223      0.497     -0.648      0.517      -1.299       0.654
    pos_3[0]            2.0937      0.524      3.992      0.000       1.064       3.124
    pos_3[1]            2.0937      0.524      3.992      0.000       1.064       3.124
    pos_4[0]            2.1428      0.632      3.391      0.001       0.902       3.383
    pos_4[1]            2.1428      0.632      3.391      0.001       0.902       3.383
    ==============================================================================
    Omnibus:                      246.835   Durbin-Watson:                   1.575
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1274.396
    Skew:                           1.590   Prob(JB):                    1.86e-277
    Kurtosis:                       8.984   Cond. No.                     4.74e+19
    ==============================================================================
    
    Warnings:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
    [2] The smallest eigenvalue is 8.08e-31. This might indicate that there are
    strong multicollinearity problems or that the design matrix is singular.
    

Residuals are nearly normal, but show some skewing. I don't think this is terrible, but we might experiment to see if transformations help fix this issue.


```python
sns.distplot(results.resid);
```

    C:\Users\David\Anaconda3\lib\site-packages\scipy\stats\stats.py:1713: FutureWarning: Using a non-tuple sequence for multidimensional indexing is deprecated; use `arr[tuple(seq)]` instead of `arr[seq]`. In the future this will be interpreted as an array index, `arr[np.array(seq)]`, which will result either in an error or a different result.
      return np.add.reduce(sorted[indexer] * weights, axis=axis) / sumval
    


![png](images/fpl/1output_21_1.png)



```python
sm.graphics.qqplot(results.resid)
```




![png](images/fpl/1output_22_0.png)




![png](images/fpl/1output_22_1.png)


I think we have a little heteroskedasticity here. It seems like the points are spreading out a little bit from left to right. Although, it isn't terrible.


```python
sns.scatterplot(x=results.fittedvalues,y=results.resid_pearson);
```


![png](images/fpl/1output_24_0.png)


The outliers are clearly affecting the results of the model, but can we really get rid of these players? It isn't surprising that these are going to have influence in the model. De Bruyne had a career season in 2019-2020 so it shouldn't be surprising he is an outlier. 


```python
fig, ax = plt.subplots(figsize=(12,8))
fig = sm.graphics.influence_plot(results, ax=ax, criterion="cooks")
```


![png](images/fpl/1output_26_0.png)



```python
df.iloc[[333,338,339,365]][['now_cost','web_name']]
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
      <th>now_cost</th>
      <th>web_name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>333</th>
      <td>116</td>
      <td>Agüero</td>
    </tr>
    <tr>
      <th>338</th>
      <td>106</td>
      <td>De Bruyne</td>
    </tr>
    <tr>
      <th>339</th>
      <td>91</td>
      <td>Sané</td>
    </tr>
    <tr>
      <th>365</th>
      <td>85</td>
      <td>Lukaku</td>
    </tr>
  </tbody>
</table>
</div>



The multicolinearity issues mentioned in the warnings in the results is not surprising, since I believe that measures like influence, creativity and threat are derived from the other variables. We can see this by the scatterplot between influence and minutes for example, or influence and points_per_game. So I think it wouldn't be bad to remove some of these variables. Minutes overlaps heavily with influence, and my initial inclination was that minutes was more important. But when I dived a little deeper, there is not a strong relationship between the cost of a player and the number minutes played. There is a stronger relationship with points per game. So maybe influence should be kept...

As suspected, red cards and yellow cards were not very helpful given the small number of red cards handed out compared to not handed out. These can probably be eliminated.


```python
g = sns.pairplot(df_copy[x_trans])
```


![png](images/fpl/1output_29_0.png)



```python
sns.scatterplot(x=df_copy['minutes'],y=df_copy['now_cost']);
```


![png](images/fpl/1output_30_0.png)


Two other things to consider is using the transformed variables for response and predictors.
Let's remove some of the variables and only consider the transformed cost variable to maybe remove some of the problems with the variance in the residual vs fitted values plot. This may be more due to the outliers though.


```python
results = smf.ols('now_cost_t ~ points_per_game + creativity  + threat  + influence + minutes+ pos_2 + pos_3 + pos_4', data=df_copy).fit()

```


```python
print(results.summary())
sns.distplot(results.resid);
```

                                OLS Regression Results                            
    ==============================================================================
    Dep. Variable:             now_cost_t   R-squared:                       0.650
    Model:                            OLS   Adj. R-squared:                  0.645
    Method:                 Least Squares   F-statistic:                     152.2
    Date:                Sun, 02 Aug 2020   Prob (F-statistic):          4.25e-144
    Time:                        11:18:58   Log-Likelihood:                 494.79
    No. Observations:                 666   AIC:                            -971.6
    Df Residuals:                     657   BIC:                            -931.1
    Df Model:                           8                                         
    Covariance Type:            nonrobust                                         
    ===================================================================================
                          coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------
    Intercept           3.7286      0.016    240.327      0.000       3.698       3.759
    points_per_game     0.0339      0.005      6.278      0.000       0.023       0.044
    creativity          0.0001   2.97e-05      3.846      0.000    5.58e-05       0.000
    threat              0.0002   2.45e-05      9.062      0.000       0.000       0.000
    influence           0.0004   6.12e-05      5.810      0.000       0.000       0.000
    minutes          -8.69e-05   1.27e-05     -6.827      0.000      -0.000   -6.19e-05
    pos_2[0]           -0.0035      0.008     -0.439      0.661      -0.019       0.012
    pos_2[1]           -0.0035      0.008     -0.439      0.661      -0.019       0.012
    pos_3[0]            0.0465      0.009      5.432      0.000       0.030       0.063
    pos_3[1]            0.0465      0.009      5.432      0.000       0.030       0.063
    pos_4[0]            0.0529      0.010      5.072      0.000       0.032       0.073
    pos_4[1]            0.0529      0.010      5.072      0.000       0.032       0.073
    ==============================================================================
    Omnibus:                      156.803   Durbin-Watson:                   1.490
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              442.162
    Skew:                           1.157   Prob(JB):                     9.68e-97
    Kurtosis:                       6.252   Cond. No.                     1.21e+20
    ==============================================================================
    
    Warnings:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
    [2] The smallest eigenvalue is 1.23e-31. This might indicate that there are
    strong multicollinearity problems or that the design matrix is singular.
    

    C:\Users\David\Anaconda3\lib\site-packages\scipy\stats\stats.py:1713: FutureWarning: Using a non-tuple sequence for multidimensional indexing is deprecated; use `arr[tuple(seq)]` instead of `arr[seq]`. In the future this will be interpreted as an array index, `arr[np.array(seq)]`, which will result either in an error or a different result.
      return np.add.reduce(sorted[indexer] * weights, axis=axis) / sumval
    


![png](images/fpl/1output_33_2.png)


Transforming does not change things too much. So we might need to decide if we are okay with how the residuals look. There are some problems, and I suspect they are caused by the outliers. I don't really want to remove the outliers because they tend to be the top players.


```python
sns.scatterplot(x=results.fittedvalues,y=results.resid_pearson);
sm.graphics.qqplot(results.resid);
```


![png](images/fpl/1output_35_0.png)



![png](images/fpl/1output_35_1.png)



```python
fig, ax = plt.subplots(figsize=(12,8))
fig = sm.graphics.influence_plot(results, ax=ax, criterion="cooks")
```


![png](images/fpl/1output_36_0.png)


Transforming also lowers the R-Squared, especially when we transform all the variables.


```python
results = smf.ols('now_cost_t ~ points_per_game_t  + creativity_t  + threat_t  + influence_t + pos_2 + pos_3 + pos_4', data=df_copy).fit()
#df_copy[df_copy['now_cost']>0]
print(results.summary())
```

                                OLS Regression Results                            
    ==============================================================================
    Dep. Variable:             now_cost_t   R-squared:                       0.468
    Model:                            OLS   Adj. R-squared:                  0.462
    Method:                 Least Squares   F-statistic:                     82.58
    Date:                Sun, 02 Aug 2020   Prob (F-statistic):           7.42e-86
    Time:                        12:53:27   Log-Likelihood:                 355.57
    No. Observations:                 666   AIC:                            -695.1
    Df Residuals:                     658   BIC:                            -659.1
    Df Model:                           7                                         
    Covariance Type:            nonrobust                                         
    =====================================================================================
                            coef    std err          t      P>|t|      [0.025      0.975]
    -------------------------------------------------------------------------------------
    Intercept             3.7473      0.021    176.768      0.000       3.706       3.789
    points_per_game_t     0.2123      0.026      8.124      0.000       0.161       0.264
    creativity_t          0.0115      0.007      1.644      0.101      -0.002       0.025
    threat_t              0.0280      0.006      4.510      0.000       0.016       0.040
    influence_t          -0.0423      0.008     -5.566      0.000      -0.057      -0.027
    pos_2[0]             -0.0445      0.011     -3.983      0.000      -0.066      -0.023
    pos_2[1]             -0.0445      0.011     -3.983      0.000      -0.066      -0.023
    pos_3[0]              0.0123      0.012      1.009      0.314      -0.012       0.036
    pos_3[1]              0.0123      0.012      1.009      0.314      -0.012       0.036
    pos_4[0]              0.0283      0.014      1.998      0.046       0.000       0.056
    pos_4[1]              0.0283      0.014      1.998      0.046       0.000       0.056
    ==============================================================================
    Omnibus:                      157.469   Durbin-Watson:                   1.254
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              409.312
    Skew:                           1.194   Prob(JB):                     1.32e-89
    Kurtosis:                       6.007   Cond. No.                     2.61e+17
    ==============================================================================
    
    Warnings:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
    [2] The smallest eigenvalue is 5.57e-31. This might indicate that there are
    strong multicollinearity problems or that the design matrix is singular.
    

And it introduces more problems with the residuals.


```python
sns.scatterplot(x=results.fittedvalues,y=results.resid_pearson);
sm.graphics.qqplot(results.resid);
```


![png](images/fpl/1output_40_0.png)



![png](images/fpl/1output_40_1.png)


Let's see how things look when we center the variables, and add in some interaction terms between the points and indices.


```python
results = smf.ols('now_cost_t ~ points_per_game_c + creativity_c + threat_c + influence_c  + points_per_game_c*influence_c+ points_per_game_c*creativity_c + points_per_game_c*threat_c+ pos_2 + pos_3 + pos_4 ', data=df_copy).fit()
print(results.summary())
sns.distplot(results.resid);
```

                                OLS Regression Results                            
    ==============================================================================
    Dep. Variable:             now_cost_t   R-squared:                       0.669
    Model:                            OLS   Adj. R-squared:                  0.664
    Method:                 Least Squares   F-statistic:                     132.6
    Date:                Sun, 02 Aug 2020   Prob (F-statistic):          3.82e-150
    Time:                        12:53:30   Log-Likelihood:                 514.18
    No. Observations:                 666   AIC:                            -1006.
    Df Residuals:                     655   BIC:                            -956.8
    Df Model:                          10                                         
    Covariance Type:            nonrobust                                         
    ==================================================================================================
                                         coef    std err          t      P>|t|      [0.025      0.975]
    --------------------------------------------------------------------------------------------------
    Intercept                          3.7967      0.016    237.949      0.000       3.765       3.828
    points_per_game_c                  0.0498      0.005      9.078      0.000       0.039       0.061
    creativity_c                       0.0002   4.68e-05      4.428      0.000       0.000       0.000
    threat_c                           0.0001   4.38e-05      2.956      0.003    4.35e-05       0.000
    influence_c                       -0.0001   4.56e-05     -3.107      0.002      -0.000   -5.21e-05
    points_per_game_c:influence_c      0.0001   2.77e-05      5.018      0.000    8.45e-05       0.000
    points_per_game_c:creativity_c -6.815e-05   2.15e-05     -3.164      0.002      -0.000   -2.59e-05
    points_per_game_c:threat_c      1.719e-05   1.73e-05      0.995      0.320   -1.67e-05    5.11e-05
    pos_2[0]                           0.0054      0.008      0.671      0.503      -0.010       0.021
    pos_2[1]                           0.0054      0.008      0.671      0.503      -0.010       0.021
    pos_3[0]                           0.0539      0.008      6.365      0.000       0.037       0.071
    pos_3[1]                           0.0539      0.008      6.365      0.000       0.037       0.071
    pos_4[0]                           0.0633      0.010      6.143      0.000       0.043       0.084
    pos_4[1]                           0.0633      0.010      6.143      0.000       0.043       0.084
    ==============================================================================
    Omnibus:                      173.780   Durbin-Watson:                   1.439
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              526.627
    Skew:                           1.255   Prob(JB):                    4.41e-115
    Kurtosis:                       6.561   Cond. No.                     6.75e+19
    ==============================================================================
    
    Warnings:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
    [2] The smallest eigenvalue is 1.87e-31. This might indicate that there are
    strong multicollinearity problems or that the design matrix is singular.
    

    C:\Users\David\Anaconda3\lib\site-packages\scipy\stats\stats.py:1713: FutureWarning: Using a non-tuple sequence for multidimensional indexing is deprecated; use `arr[tuple(seq)]` instead of `arr[seq]`. In the future this will be interpreted as an array index, `arr[np.array(seq)]`, which will result either in an error or a different result.
      return np.add.reduce(sorted[indexer] * weights, axis=axis) / sumval
    


![png](images/fpl/1output_42_2.png)



```python
sns.scatterplot(x=results.fittedvalues,y=results.resid_pearson);
sm.graphics.qqplot(results.resid);
```


![png](images/fpl/1output_43_0.png)



![png](images/fpl/1output_43_1.png)


I'll leave in the transformed dependent variable, because I think it helps a little with the residual constant variance assumption.

The nice thing about centering the variables is it aids with interpretation. For example, we can tell what the expected price for an average player would be for each of the positions.

These are log costs, so we need to take the exponent of the final variable.

- Average Goal keper: 3.7967 = $exp(3.7967)$ = 44.55 = ~ about 4.4 million
- Average Defender: 3.7967 + 0.0054 = $exp(3.8021)$ = 44.80 = ~ 4.4 million
- Average Midfielder: 3.7967 + 0.0539 = $exp(3.8506)$ = 47.02 = ~ 4.7 million
- Average Forward:  3.7967 + 0.0633 = $exp(3.86)$ = 47.47 = ~ 4.7 million

The binary position variables can be interpreted a little bit too. They are comparing the cost of the position to the base goal kepper. Basically, midfield and forward positions are significantly different from goalkeeprs, and defenders are not significantly different from goalkeepers.

Let's see what the model says about who would be undervalued. This is the players that cost is lower than the predicted cost.


```python
df['predictedcost'] = np.exp(results.fittedvalues)
df['residuals'] = df['now_cost'] - df['predictedcost']
undervalued = df.iloc[df[df['residuals']<0].sort_values("residuals",ascending=True).index]
undervalued['web_name'][0:20]
```




    499            Ings
    642         Jiménez
    218            Ayew
    442        Cantwell
    372         Martial
    126          Maupay
    305           Salah
    44         Grealish
    460         Mousset
    471           Fleck
    128        Connolly
    406         Shelvey
    270           Vardy
    28       Martinelli
    367       Greenwood
    62     Douglas Luiz
    467       Lundstram
    501            Long
    385        Williams
    19        Guendouzi
    Name: web_name, dtype: object



Ings and Jiménez come as two of the most undervalued players. A residual of -20 and -15 (2 and 1.5 million undervalued).

We should consider some things. They cost 7.6 and 8.0 million, and they are forwards. The get 5 points per game, and play well over 2000 minutes. These seem like they would be good value players.


```python
df[df['web_name']=='Ings'][x_fields+y_fields+['residuals','predictedcost']]
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
      <th>points_per_game</th>
      <th>creativity</th>
      <th>influence</th>
      <th>red_cards</th>
      <th>threat</th>
      <th>yellow_cards</th>
      <th>minutes</th>
      <th>pos_2</th>
      <th>pos_2</th>
      <th>pos_3</th>
      <th>pos_3</th>
      <th>pos_4</th>
      <th>pos_4</th>
      <th>team_code</th>
      <th>now_cost</th>
      <th>residuals</th>
      <th>predictedcost</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>499</th>
      <td>5.2</td>
      <td>458.3</td>
      <td>1010.0</td>
      <td>0</td>
      <td>1558.0</td>
      <td>3</td>
      <td>2800</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>1</td>
      <td>20</td>
      <td>76</td>
      <td>-20.26107</td>
      <td>96.26107</td>
    </tr>
  </tbody>
</table>
</div>




```python
df[df['web_name']=='Jiménez'][x_fields+y_fields+['residuals','predictedcost']]
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
      <th>points_per_game</th>
      <th>creativity</th>
      <th>influence</th>
      <th>red_cards</th>
      <th>threat</th>
      <th>yellow_cards</th>
      <th>minutes</th>
      <th>pos_2</th>
      <th>pos_3</th>
      <th>pos_4</th>
      <th>now_cost</th>
      <th>residuals</th>
      <th>predictedcost</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>642</th>
      <td>5.1</td>
      <td>668.2</td>
      <td>911.6</td>
      <td>0</td>
      <td>1680.0</td>
      <td>3</td>
      <td>3241</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>80</td>
      <td>-15.20407</td>
      <td>95.20407</td>
    </tr>
  </tbody>
</table>
</div>



Let's look at the distributions of these undervalued players by cost and points per game. Not surprisingly the players on the lowerend tend to be undervalued. Big names who get a lot of points will already be highly valued, so you won't find gems in there. 


```python
undervalued.hist("now_cost",by="element_type");
```


![png](images/fpl/1output_50_0.png)



```python
undervalued.hist("points_per_game",by="element_type");
```


![png](images/fpl/1output_51_0.png)


We can filter by cost to get a sense of what players we might want within a certain price range, or by the points per game. Here we see "Thomas" (there are more than one, so we would need to delve deeper into which Thomas) is undervalued by almost a 1 million pounds, and gets 5 points per game. Not a bad pick for that price.


```python
undervalued[(undervalued['element_type']==2) & (undervalued['now_cost'] < 60)].sort_values("points_per_game",ascending=False)[['web_name','points_per_game','now_cost','predictedcost']]
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
      <th>web_name</th>
      <th>points_per_game</th>
      <th>now_cost</th>
      <th>predictedcost</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>292</th>
      <td>Thomas</td>
      <td>5.0</td>
      <td>40</td>
      <td>49.114904</td>
    </tr>
    <tr>
      <th>570</th>
      <td>Janmaat</td>
      <td>4.5</td>
      <td>40</td>
      <td>49.265382</td>
    </tr>
    <tr>
      <th>638</th>
      <td>Boly</td>
      <td>4.4</td>
      <td>49</td>
      <td>53.257040</td>
    </tr>
    <tr>
      <th>467</th>
      <td>Lundstram</td>
      <td>4.2</td>
      <td>46</td>
      <td>57.848503</td>
    </tr>
    <tr>
      <th>265</th>
      <td>Chilwell</td>
      <td>4.2</td>
      <td>54</td>
      <td>55.671437</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>160</th>
      <td>Koiki</td>
      <td>0.0</td>
      <td>40</td>
      <td>42.083903</td>
    </tr>
    <tr>
      <th>351</th>
      <td>Harwood-Bellis</td>
      <td>0.0</td>
      <td>40</td>
      <td>42.083903</td>
    </tr>
    <tr>
      <th>162</th>
      <td>Dunne</td>
      <td>0.0</td>
      <td>40</td>
      <td>42.083903</td>
    </tr>
    <tr>
      <th>323</th>
      <td>Phillips</td>
      <td>0.0</td>
      <td>39</td>
      <td>42.083903</td>
    </tr>
    <tr>
      <th>163</th>
      <td>Thomas</td>
      <td>0.0</td>
      <td>40</td>
      <td>42.083903</td>
    </tr>
  </tbody>
</table>
<p>132 rows × 4 columns</p>
</div>



# Team game?

Hot take: soccer is a team game. FPL we build a team, but we are picking individuals who score individual points. I think there is an argument to be made that a player's points is influenced by their teammates. A player on a better team may be boosted by that fact. Of course, who they are playing against may also affect things. 

Next we will consider a model that treats players clustered on a team. This means we will use a hiearchical linear model, or mixed effects model. I will use a simple random intercept model where a player is nested within a team code. 


```python
from statsmodels.regression.mixed_linear_model import MixedLM
```


```python
# multilevel model teams = 'team_code'
x_fields = ['points_per_game','creativity','influence','red_cards','threat','yellow_cards','minutes','pos_2','pos_3','pos_4','team_code']
y_fields = ['now_cost']
print(x_fields)
df_lmm = df[x_fields+y_fields].copy()
x_trans = ['points_per_game','creativity','influence','threat','minutes']
for x in x_trans:
    df_lmm[x+"_c"] = df_lmm[x].values - df_lmm[x].mean()
df_lmm['now_cost_t'] = np.log(df_lmm['now_cost'])
df_lmm
```

    ['points_per_game', 'creativity', 'influence', 'red_cards', 'threat', 'yellow_cards', 'minutes', 'pos_2', 'pos_3', 'pos_4', 'team_code']
    




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
      <th>points_per_game</th>
      <th>creativity</th>
      <th>influence</th>
      <th>red_cards</th>
      <th>threat</th>
      <th>yellow_cards</th>
      <th>minutes</th>
      <th>pos_2</th>
      <th>pos_3</th>
      <th>pos_4</th>
      <th>team_code</th>
      <th>now_cost</th>
      <th>points_per_game_c</th>
      <th>creativity_c</th>
      <th>influence_c</th>
      <th>threat_c</th>
      <th>minutes_c</th>
      <th>now_cost_t</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2.9</td>
      <td>45.5</td>
      <td>277.2</td>
      <td>0</td>
      <td>155.0</td>
      <td>2</td>
      <td>1205</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>3</td>
      <td>51</td>
      <td>0.929429</td>
      <td>-118.311111</td>
      <td>27.309009</td>
      <td>-33.858859</td>
      <td>80.166667</td>
      <td>3.931826</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2.9</td>
      <td>76.9</td>
      <td>187.8</td>
      <td>0</td>
      <td>103.0</td>
      <td>2</td>
      <td>1156</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>3</td>
      <td>52</td>
      <td>0.929429</td>
      <td>-86.911111</td>
      <td>-62.090991</td>
      <td>-85.858859</td>
      <td>31.166667</td>
      <td>3.951244</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2.1</td>
      <td>182.5</td>
      <td>269.6</td>
      <td>0</td>
      <td>81.0</td>
      <td>4</td>
      <td>1694</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>3</td>
      <td>52</td>
      <td>0.129429</td>
      <td>18.688889</td>
      <td>19.709009</td>
      <td>-107.858859</td>
      <td>569.166667</td>
      <td>3.951244</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2.0</td>
      <td>182.0</td>
      <td>301.8</td>
      <td>1</td>
      <td>58.0</td>
      <td>4</td>
      <td>1382</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>3</td>
      <td>45</td>
      <td>0.029429</td>
      <td>18.188889</td>
      <td>51.909009</td>
      <td>-130.858859</td>
      <td>257.166667</td>
      <td>3.806662</td>
    </tr>
    <tr>
      <th>4</th>
      <td>3.0</td>
      <td>36.8</td>
      <td>436.2</td>
      <td>0</td>
      <td>110.0</td>
      <td>6</td>
      <td>1696</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>3</td>
      <td>48</td>
      <td>1.029429</td>
      <td>-127.011111</td>
      <td>186.309009</td>
      <td>-78.858859</td>
      <td>571.166667</td>
      <td>3.871201</td>
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
      <td>...</td>
      <td>...</td>
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
      <th>661</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0</td>
      <td>0.0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>39</td>
      <td>40</td>
      <td>-1.970571</td>
      <td>-163.811111</td>
      <td>-249.890991</td>
      <td>-188.858859</td>
      <td>-1124.833333</td>
      <td>3.688879</td>
    </tr>
    <tr>
      <th>662</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0</td>
      <td>0.0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>39</td>
      <td>39</td>
      <td>-1.970571</td>
      <td>-163.811111</td>
      <td>-249.890991</td>
      <td>-188.858859</td>
      <td>-1124.833333</td>
      <td>3.663562</td>
    </tr>
    <tr>
      <th>663</th>
      <td>1.0</td>
      <td>10.4</td>
      <td>2.6</td>
      <td>0</td>
      <td>0.0</td>
      <td>0</td>
      <td>6</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>39</td>
      <td>45</td>
      <td>-0.970571</td>
      <td>-153.411111</td>
      <td>-247.290991</td>
      <td>-188.858859</td>
      <td>-1118.833333</td>
      <td>3.806662</td>
    </tr>
    <tr>
      <th>664</th>
      <td>2.8</td>
      <td>73.3</td>
      <td>62.4</td>
      <td>0</td>
      <td>148.0</td>
      <td>0</td>
      <td>285</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>39</td>
      <td>49</td>
      <td>0.829429</td>
      <td>-90.511111</td>
      <td>-187.490991</td>
      <td>-40.858859</td>
      <td>-839.833333</td>
      <td>3.891820</td>
    </tr>
    <tr>
      <th>665</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0</td>
      <td>0.0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>39</td>
      <td>45</td>
      <td>-1.970571</td>
      <td>-163.811111</td>
      <td>-249.890991</td>
      <td>-188.858859</td>
      <td>-1124.833333</td>
      <td>3.806662</td>
    </tr>
  </tbody>
</table>
<p>666 rows × 18 columns</p>
</div>



First let's see if this even necessary. We can fit an intercept only model and check the ICC to see if it shows evidence of clustering within each team.


```python
model = sm.MixedLM.from_formula("now_cost ~ 1", data=df_lmm, groups=df_lmm['team_code'].values)
result = model.fit()
print(result.summary())
```

             Mixed Linear Model Regression Results
    ========================================================
    Model:            MixedLM Dependent Variable: now_cost  
    No. Observations: 666     Method:             REML      
    No. Groups:       20      Scale:              126.7795  
    Min. group size:  28      Likelihood:         -2573.0225
    Max. group size:  39      Converged:          Yes       
    Mean group size:  33.3                                  
    --------------------------------------------------------
                  Coef.  Std.Err.   z    P>|z| [0.025 0.975]
    --------------------------------------------------------
    Intercept     50.471    1.018 49.580 0.000 48.476 52.466
    Group Var     16.895    0.614                           
    ========================================================
    
    


```python
icc = result.cov_re / (result.cov_re + result.scale)
icc
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
      <th>Group</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Group</th>
      <td>0.117593</td>
    </tr>
  </tbody>
</table>
</div>



The ICC is .12 and is not a high number, but there is some evidence of nesting. I think it is worth building a random intercept model to look at the predicted costs from this model.


```python
strmodel = 'now_cost ~ points_per_game_c  + creativity_c + threat_c + influence_c  + pos_2 + pos_3 + pos_4 + points_per_game_c*influence_c+ points_per_game_c*creativity_c + points_per_game_c*threat_c'
model = sm.MixedLM.from_formula(strmodel, data=df_lmm, groups=df_lmm['team_code'].values)
result = model.fit()
print(result.summary())
```

                      Mixed Linear Model Regression Results
    =========================================================================
    Model:                   MixedLM      Dependent Variable:      now_cost  
    No. Observations:        666          Method:                  REML      
    No. Groups:              20           Scale:                   37.3435   
    Min. group size:         28           Likelihood:              -2197.5553
    Max. group size:         39           Converged:               Yes       
    Mean group size:         33.3                                            
    -------------------------------------------------------------------------
                                   Coef.  Std.Err.   z    P>|z| [0.025 0.975]
    -------------------------------------------------------------------------
    Intercept                      44.381    1.028 43.178 0.000 42.366 46.395
    points_per_game_c               2.805    0.306  9.170 0.000  2.205  3.404
    creativity_c                    0.011    0.003  4.223 0.000  0.006  0.016
    threat_c                        0.004    0.002  1.837 0.066 -0.000  0.009
    influence_c                    -0.007    0.003 -2.831 0.005 -0.012 -0.002
    pos_2                           0.469    0.887  0.528 0.597 -1.270  2.207
    pos_3                           5.417    0.922  5.872 0.000  3.609  7.224
    pos_4                           7.010    1.124  6.234 0.000  4.806  9.214
    points_per_game_c:influence_c   0.007    0.002  4.604 0.000  0.004  0.010
    points_per_game_c:creativity_c -0.004    0.001 -2.974 0.003 -0.006 -0.001
    points_per_game_c:threat_c      0.004    0.001  3.918 0.000  0.002  0.006
    Group Var                       5.913    0.386                           
    =========================================================================
    
    

In terms of the top players that are undervalued (in defense at least) they are the same in both models.


```python
df['predictedcostlmm'] = result.fittedvalues
df['residualslmm'] = df['now_cost'] - df['predictedcostlmm']

undervalued = df.iloc[df[df['residualslmm']<0].sort_values("residualslmm",ascending=True).index]
undervalued[(undervalued['element_type']==2) & (undervalued['now_cost'] < 60)].sort_values("points_per_game",ascending=False)[['web_name','points_per_game','now_cost','predictedcostlmm']]

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
      <th>web_name</th>
      <th>points_per_game</th>
      <th>now_cost</th>
      <th>predictedcostlmm</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>292</th>
      <td>Thomas</td>
      <td>5.0</td>
      <td>40</td>
      <td>46.634021</td>
    </tr>
    <tr>
      <th>570</th>
      <td>Janmaat</td>
      <td>4.5</td>
      <td>40</td>
      <td>46.906263</td>
    </tr>
    <tr>
      <th>638</th>
      <td>Boly</td>
      <td>4.4</td>
      <td>49</td>
      <td>51.061554</td>
    </tr>
    <tr>
      <th>467</th>
      <td>Lundstram</td>
      <td>4.2</td>
      <td>46</td>
      <td>54.595430</td>
    </tr>
    <tr>
      <th>33</th>
      <td>Marí</td>
      <td>4.0</td>
      <td>44</td>
      <td>47.928752</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>160</th>
      <td>Koiki</td>
      <td>0.0</td>
      <td>40</td>
      <td>40.931390</td>
    </tr>
    <tr>
      <th>163</th>
      <td>Thomas</td>
      <td>0.0</td>
      <td>40</td>
      <td>40.931390</td>
    </tr>
    <tr>
      <th>223</th>
      <td>Woods</td>
      <td>0.0</td>
      <td>39</td>
      <td>41.020978</td>
    </tr>
    <tr>
      <th>260</th>
      <td>Cuco Martina</td>
      <td>0.0</td>
      <td>40</td>
      <td>43.895857</td>
    </tr>
    <tr>
      <th>251</th>
      <td>Gibson</td>
      <td>0.0</td>
      <td>42</td>
      <td>43.895857</td>
    </tr>
  </tbody>
</table>
<p>127 rows × 4 columns</p>
</div>



But are quite a bit different in terms of the top 20 overall undervalued players. Consider Salah, and Vardy are not on this list. The best value, despite costing 8.5 million, would be Martial. Ings would be second and Jimenez third. In terms of the points they tend to get per game.


```python
undervalued[['web_name','points_per_game','now_cost','predictedcostlmm','predictedcost']][0:20]
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
      <th>web_name</th>
      <th>points_per_game</th>
      <th>now_cost</th>
      <th>predictedcostlmm</th>
      <th>predictedcost</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>499</th>
      <td>Ings</td>
      <td>5.2</td>
      <td>76</td>
      <td>92.811625</td>
      <td>96.261070</td>
    </tr>
    <tr>
      <th>372</th>
      <td>Martial</td>
      <td>6.2</td>
      <td>85</td>
      <td>99.831702</td>
      <td>98.198425</td>
    </tr>
    <tr>
      <th>367</th>
      <td>Greenwood</td>
      <td>3.3</td>
      <td>48</td>
      <td>62.004713</td>
      <td>57.555496</td>
    </tr>
    <tr>
      <th>218</th>
      <td>Ayew</td>
      <td>3.6</td>
      <td>51</td>
      <td>64.959374</td>
      <td>64.764447</td>
    </tr>
    <tr>
      <th>28</th>
      <td>Martinelli</td>
      <td>2.8</td>
      <td>42</td>
      <td>54.950203</td>
      <td>52.097068</td>
    </tr>
    <tr>
      <th>126</th>
      <td>Maupay</td>
      <td>3.5</td>
      <td>57</td>
      <td>69.610972</td>
      <td>69.897145</td>
    </tr>
    <tr>
      <th>442</th>
      <td>Cantwell</td>
      <td>3.0</td>
      <td>45</td>
      <td>57.426216</td>
      <td>58.567996</td>
    </tr>
    <tr>
      <th>385</th>
      <td>Williams</td>
      <td>3.0</td>
      <td>38</td>
      <td>50.339086</td>
      <td>46.966798</td>
    </tr>
    <tr>
      <th>642</th>
      <td>Jiménez</td>
      <td>5.1</td>
      <td>80</td>
      <td>92.106519</td>
      <td>94.017099</td>
    </tr>
    <tr>
      <th>128</th>
      <td>Connolly</td>
      <td>2.5</td>
      <td>42</td>
      <td>53.165266</td>
      <td>54.129899</td>
    </tr>
    <tr>
      <th>44</th>
      <td>Grealish</td>
      <td>4.1</td>
      <td>59</td>
      <td>69.725409</td>
      <td>71.684460</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Guendouzi</td>
      <td>2.0</td>
      <td>41</td>
      <td>51.722389</td>
      <td>49.582194</td>
    </tr>
    <tr>
      <th>406</th>
      <td>Shelvey</td>
      <td>4.0</td>
      <td>49</td>
      <td>59.687702</td>
      <td>60.611419</td>
    </tr>
    <tr>
      <th>379</th>
      <td>Pereira</td>
      <td>2.4</td>
      <td>47</td>
      <td>57.580906</td>
      <td>54.337985</td>
    </tr>
    <tr>
      <th>460</th>
      <td>Mousset</td>
      <td>2.8</td>
      <td>43</td>
      <td>53.538045</td>
      <td>55.269229</td>
    </tr>
    <tr>
      <th>552</th>
      <td>Parrott</td>
      <td>1.0</td>
      <td>43</td>
      <td>53.415579</td>
      <td>48.327146</td>
    </tr>
    <tr>
      <th>12</th>
      <td>Nketiah</td>
      <td>1.9</td>
      <td>43</td>
      <td>53.280647</td>
      <td>50.713177</td>
    </tr>
    <tr>
      <th>471</th>
      <td>Fleck</td>
      <td>3.4</td>
      <td>47</td>
      <td>57.022550</td>
      <td>59.166286</td>
    </tr>
    <tr>
      <th>312</th>
      <td>Henderson</td>
      <td>3.9</td>
      <td>52</td>
      <td>61.796491</td>
      <td>58.943983</td>
    </tr>
    <tr>
      <th>550</th>
      <td>Skipp</td>
      <td>1.0</td>
      <td>42</td>
      <td>51.632504</td>
      <td>47.251395</td>
    </tr>
  </tbody>
</table>
</div>



When we split this up we can see some flaws with this approach. For one, there are players that are valued higher even though they don't get any points in a game.

# Goalkeepers


```python
undervalued[(undervalued['element_type']==1)][['web_name','points_per_game','now_cost','predictedcostlmm','predictedcost','minutes']][0:20]
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
      <th>web_name</th>
      <th>points_per_game</th>
      <th>now_cost</th>
      <th>predictedcostlmm</th>
      <th>predictedcost</th>
      <th>minutes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>539</th>
      <td>Gazzaniga</td>
      <td>3.2</td>
      <td>41</td>
      <td>49.184254</td>
      <td>45.434304</td>
      <td>1612</td>
    </tr>
    <tr>
      <th>350</th>
      <td>Carson</td>
      <td>0.0</td>
      <td>40</td>
      <td>46.734416</td>
      <td>41.611713</td>
      <td>0</td>
    </tr>
    <tr>
      <th>624</th>
      <td>Martin</td>
      <td>4.0</td>
      <td>39</td>
      <td>45.678199</td>
      <td>46.339488</td>
      <td>435</td>
    </tr>
    <tr>
      <th>317</th>
      <td>Adrián</td>
      <td>2.5</td>
      <td>40</td>
      <td>45.949224</td>
      <td>43.679538</td>
      <td>873</td>
    </tr>
    <tr>
      <th>556</th>
      <td>Whiteman</td>
      <td>0.0</td>
      <td>40</td>
      <td>45.504607</td>
      <td>41.611713</td>
      <td>0</td>
    </tr>
    <tr>
      <th>558</th>
      <td>Austin</td>
      <td>0.0</td>
      <td>40</td>
      <td>45.504607</td>
      <td>41.611713</td>
      <td>0</td>
    </tr>
    <tr>
      <th>436</th>
      <td>McGovern</td>
      <td>5.5</td>
      <td>41</td>
      <td>46.419492</td>
      <td>48.298663</td>
      <td>158</td>
    </tr>
    <tr>
      <th>240</th>
      <td>Stekelenburg</td>
      <td>0.0</td>
      <td>39</td>
      <td>43.427206</td>
      <td>41.611713</td>
      <td>0</td>
    </tr>
    <tr>
      <th>97</th>
      <td>Ramsdale</td>
      <td>3.4</td>
      <td>44</td>
      <td>48.348582</td>
      <td>47.684742</td>
      <td>3330</td>
    </tr>
    <tr>
      <th>21</th>
      <td>Martínez</td>
      <td>3.7</td>
      <td>44</td>
      <td>48.310466</td>
      <td>46.465858</td>
      <td>770</td>
    </tr>
    <tr>
      <th>13</th>
      <td>Leno</td>
      <td>3.8</td>
      <td>48</td>
      <td>52.041203</td>
      <td>49.927185</td>
      <td>2649</td>
    </tr>
    <tr>
      <th>538</th>
      <td>Lloris</td>
      <td>4.7</td>
      <td>53</td>
      <td>56.699816</td>
      <td>53.009297</td>
      <td>1808</td>
    </tr>
    <tr>
      <th>35</th>
      <td>Macey</td>
      <td>0.0</td>
      <td>40</td>
      <td>43.640280</td>
      <td>41.611713</td>
      <td>0</td>
    </tr>
    <tr>
      <th>557</th>
      <td>Vorm</td>
      <td>0.0</td>
      <td>42</td>
      <td>45.504607</td>
      <td>41.611713</td>
      <td>0</td>
    </tr>
    <tr>
      <th>261</th>
      <td>Virgínia</td>
      <td>0.0</td>
      <td>40</td>
      <td>43.427206</td>
      <td>41.611713</td>
      <td>0</td>
    </tr>
    <tr>
      <th>630</th>
      <td>Randolph</td>
      <td>1.5</td>
      <td>39</td>
      <td>42.080484</td>
      <td>42.630968</td>
      <td>180</td>
    </tr>
    <tr>
      <th>145</th>
      <td>Pope</td>
      <td>4.5</td>
      <td>52</td>
      <td>54.408238</td>
      <td>55.809474</td>
      <td>3420</td>
    </tr>
    <tr>
      <th>336</th>
      <td>Bravo</td>
      <td>2.8</td>
      <td>47</td>
      <td>49.189954</td>
      <td>44.308978</td>
      <td>346</td>
    </tr>
    <tr>
      <th>318</th>
      <td>Lonergan</td>
      <td>0.0</td>
      <td>42</td>
      <td>44.136688</td>
      <td>41.611713</td>
      <td>0</td>
    </tr>
    <tr>
      <th>66</th>
      <td>Reina</td>
      <td>3.4</td>
      <td>42</td>
      <td>43.725165</td>
      <td>45.790763</td>
      <td>1080</td>
    </tr>
  </tbody>
</table>
</div>



# Defenders


```python
undervalued[(undervalued['element_type']==2)][['web_name','points_per_game','now_cost','predictedcostlmm','predictedcost','minutes']][0:20]
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
      <th>web_name</th>
      <th>points_per_game</th>
      <th>now_cost</th>
      <th>predictedcostlmm</th>
      <th>predictedcost</th>
      <th>minutes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>385</th>
      <td>Williams</td>
      <td>3.0</td>
      <td>38</td>
      <td>50.339086</td>
      <td>46.966798</td>
      <td>1003</td>
    </tr>
    <tr>
      <th>559</th>
      <td>Tanganga</td>
      <td>2.8</td>
      <td>39</td>
      <td>48.618892</td>
      <td>44.949032</td>
      <td>525</td>
    </tr>
    <tr>
      <th>77</th>
      <td>Rico</td>
      <td>3.1</td>
      <td>42</td>
      <td>50.621881</td>
      <td>49.739882</td>
      <td>2333</td>
    </tr>
    <tr>
      <th>467</th>
      <td>Lundstram</td>
      <td>4.2</td>
      <td>46</td>
      <td>54.595430</td>
      <td>55.527695</td>
      <td>2452</td>
    </tr>
    <tr>
      <th>322</th>
      <td>Williams</td>
      <td>2.3</td>
      <td>40</td>
      <td>47.508045</td>
      <td>45.172556</td>
      <td>228</td>
    </tr>
    <tr>
      <th>535</th>
      <td>Aurier</td>
      <td>3.8</td>
      <td>51</td>
      <td>58.288171</td>
      <td>53.672117</td>
      <td>2699</td>
    </tr>
    <tr>
      <th>351</th>
      <td>Harwood-Bellis</td>
      <td>0.0</td>
      <td>40</td>
      <td>47.203066</td>
      <td>42.067352</td>
      <td>0</td>
    </tr>
    <tr>
      <th>331</th>
      <td>Otamendi</td>
      <td>3.4</td>
      <td>48</td>
      <td>55.087734</td>
      <td>49.354478</td>
      <td>1710</td>
    </tr>
    <tr>
      <th>570</th>
      <td>Janmaat</td>
      <td>4.5</td>
      <td>40</td>
      <td>46.906263</td>
      <td>48.363314</td>
      <td>606</td>
    </tr>
    <tr>
      <th>292</th>
      <td>Thomas</td>
      <td>5.0</td>
      <td>40</td>
      <td>46.634021</td>
      <td>48.326860</td>
      <td>267</td>
    </tr>
    <tr>
      <th>262</th>
      <td>Branthwaite</td>
      <td>2.8</td>
      <td>40</td>
      <td>46.358605</td>
      <td>44.799335</td>
      <td>299</td>
    </tr>
    <tr>
      <th>22</th>
      <td>Chambers</td>
      <td>3.0</td>
      <td>43</td>
      <td>49.347649</td>
      <td>47.183709</td>
      <td>1102</td>
    </tr>
    <tr>
      <th>563</th>
      <td>Cirkin</td>
      <td>0.0</td>
      <td>40</td>
      <td>45.973257</td>
      <td>42.067352</td>
      <td>0</td>
    </tr>
    <tr>
      <th>193</th>
      <td>Tomori</td>
      <td>3.2</td>
      <td>42</td>
      <td>47.857754</td>
      <td>46.663640</td>
      <td>1291</td>
    </tr>
    <tr>
      <th>465</th>
      <td>Egan</td>
      <td>3.7</td>
      <td>47</td>
      <td>52.724272</td>
      <td>53.695002</td>
      <td>3187</td>
    </tr>
    <tr>
      <th>323</th>
      <td>Phillips</td>
      <td>0.0</td>
      <td>39</td>
      <td>44.605338</td>
      <td>42.067352</td>
      <td>0</td>
    </tr>
    <tr>
      <th>325</th>
      <td>Hoever</td>
      <td>0.0</td>
      <td>39</td>
      <td>44.605338</td>
      <td>42.067352</td>
      <td>0</td>
    </tr>
    <tr>
      <th>107</th>
      <td>Dunk</td>
      <td>3.6</td>
      <td>48</td>
      <td>53.390750</td>
      <td>53.645496</td>
      <td>3230</td>
    </tr>
    <tr>
      <th>349</th>
      <td>Garcia</td>
      <td>2.9</td>
      <td>45</td>
      <td>50.261745</td>
      <td>45.324716</td>
      <td>790</td>
    </tr>
    <tr>
      <th>413</th>
      <td>Willems</td>
      <td>3.4</td>
      <td>43</td>
      <td>47.930352</td>
      <td>48.868512</td>
      <td>1492</td>
    </tr>
  </tbody>
</table>
</div>



# Midfielders


```python
undervalued[(undervalued['element_type']==3)][['web_name','points_per_game','now_cost','predictedcostlmm','predictedcost','minutes']][0:20]
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
      <th>web_name</th>
      <th>points_per_game</th>
      <th>now_cost</th>
      <th>predictedcostlmm</th>
      <th>predictedcost</th>
      <th>minutes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>372</th>
      <td>Martial</td>
      <td>6.2</td>
      <td>85</td>
      <td>99.831702</td>
      <td>98.198425</td>
      <td>2625</td>
    </tr>
    <tr>
      <th>442</th>
      <td>Cantwell</td>
      <td>3.0</td>
      <td>45</td>
      <td>57.426216</td>
      <td>58.567996</td>
      <td>2484</td>
    </tr>
    <tr>
      <th>44</th>
      <td>Grealish</td>
      <td>4.1</td>
      <td>59</td>
      <td>69.725409</td>
      <td>71.684460</td>
      <td>3233</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Guendouzi</td>
      <td>2.0</td>
      <td>41</td>
      <td>51.722389</td>
      <td>49.582194</td>
      <td>1744</td>
    </tr>
    <tr>
      <th>406</th>
      <td>Shelvey</td>
      <td>4.0</td>
      <td>49</td>
      <td>59.687702</td>
      <td>60.611419</td>
      <td>2118</td>
    </tr>
    <tr>
      <th>379</th>
      <td>Pereira</td>
      <td>2.4</td>
      <td>47</td>
      <td>57.580906</td>
      <td>54.337985</td>
      <td>1478</td>
    </tr>
    <tr>
      <th>471</th>
      <td>Fleck</td>
      <td>3.4</td>
      <td>47</td>
      <td>57.022550</td>
      <td>59.166286</td>
      <td>2515</td>
    </tr>
    <tr>
      <th>312</th>
      <td>Henderson</td>
      <td>3.9</td>
      <td>52</td>
      <td>61.796491</td>
      <td>58.943983</td>
      <td>2234</td>
    </tr>
    <tr>
      <th>550</th>
      <td>Skipp</td>
      <td>1.0</td>
      <td>42</td>
      <td>51.632504</td>
      <td>47.251395</td>
      <td>74</td>
    </tr>
    <tr>
      <th>382</th>
      <td>Chong</td>
      <td>1.0</td>
      <td>42</td>
      <td>51.251793</td>
      <td>47.457588</td>
      <td>34</td>
    </tr>
    <tr>
      <th>191</th>
      <td>Mount</td>
      <td>3.7</td>
      <td>60</td>
      <td>69.228616</td>
      <td>67.527331</td>
      <td>2865</td>
    </tr>
    <tr>
      <th>194</th>
      <td>Gilmour</td>
      <td>1.5</td>
      <td>41</td>
      <td>49.953056</td>
      <td>48.331524</td>
      <td>191</td>
    </tr>
    <tr>
      <th>345</th>
      <td>Gündogan</td>
      <td>2.1</td>
      <td>51</td>
      <td>59.462217</td>
      <td>54.649388</td>
      <td>2012</td>
    </tr>
    <tr>
      <th>30</th>
      <td>Saka</td>
      <td>2.7</td>
      <td>47</td>
      <td>55.271710</td>
      <td>53.049182</td>
      <td>1746</td>
    </tr>
    <tr>
      <th>383</th>
      <td>Garner</td>
      <td>1.0</td>
      <td>43</td>
      <td>51.260063</td>
      <td>47.437024</td>
      <td>8</td>
    </tr>
    <tr>
      <th>381</th>
      <td>McTominay</td>
      <td>2.7</td>
      <td>48</td>
      <td>56.137263</td>
      <td>52.626102</td>
      <td>1765</td>
    </tr>
    <tr>
      <th>353</th>
      <td>Doyle</td>
      <td>1.0</td>
      <td>45</td>
      <td>53.034000</td>
      <td>47.443153</td>
      <td>15</td>
    </tr>
    <tr>
      <th>613</th>
      <td>Snodgrass</td>
      <td>3.6</td>
      <td>50</td>
      <td>57.927329</td>
      <td>57.879544</td>
      <td>1504</td>
    </tr>
    <tr>
      <th>31</th>
      <td>Smith Rowe</td>
      <td>2.0</td>
      <td>43</td>
      <td>50.861344</td>
      <td>48.529242</td>
      <td>96</td>
    </tr>
    <tr>
      <th>62</th>
      <td>Douglas Luiz</td>
      <td>2.5</td>
      <td>43</td>
      <td>50.691031</td>
      <td>52.541722</td>
      <td>2604</td>
    </tr>
  </tbody>
</table>
</div>



# Forwards


```python
undervalued[(undervalued['element_type']==4)][['web_name','points_per_game','now_cost','predictedcostlmm','predictedcost','minutes']][0:20]
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
      <th>web_name</th>
      <th>points_per_game</th>
      <th>now_cost</th>
      <th>predictedcostlmm</th>
      <th>predictedcost</th>
      <th>minutes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>499</th>
      <td>Ings</td>
      <td>5.2</td>
      <td>76</td>
      <td>92.811625</td>
      <td>96.261070</td>
      <td>2800</td>
    </tr>
    <tr>
      <th>367</th>
      <td>Greenwood</td>
      <td>3.3</td>
      <td>48</td>
      <td>62.004713</td>
      <td>57.555496</td>
      <td>1303</td>
    </tr>
    <tr>
      <th>218</th>
      <td>Ayew</td>
      <td>3.6</td>
      <td>51</td>
      <td>64.959374</td>
      <td>64.764447</td>
      <td>3148</td>
    </tr>
    <tr>
      <th>28</th>
      <td>Martinelli</td>
      <td>2.8</td>
      <td>42</td>
      <td>54.950203</td>
      <td>52.097068</td>
      <td>656</td>
    </tr>
    <tr>
      <th>126</th>
      <td>Maupay</td>
      <td>3.5</td>
      <td>57</td>
      <td>69.610972</td>
      <td>69.897145</td>
      <td>2763</td>
    </tr>
    <tr>
      <th>642</th>
      <td>Jiménez</td>
      <td>5.1</td>
      <td>80</td>
      <td>92.106519</td>
      <td>94.017099</td>
      <td>3241</td>
    </tr>
    <tr>
      <th>128</th>
      <td>Connolly</td>
      <td>2.5</td>
      <td>42</td>
      <td>53.165266</td>
      <td>54.129899</td>
      <td>1250</td>
    </tr>
    <tr>
      <th>460</th>
      <td>Mousset</td>
      <td>2.8</td>
      <td>43</td>
      <td>53.538045</td>
      <td>55.269229</td>
      <td>1223</td>
    </tr>
    <tr>
      <th>552</th>
      <td>Parrott</td>
      <td>1.0</td>
      <td>43</td>
      <td>53.415579</td>
      <td>48.327146</td>
      <td>6</td>
    </tr>
    <tr>
      <th>12</th>
      <td>Nketiah</td>
      <td>1.9</td>
      <td>43</td>
      <td>53.280647</td>
      <td>50.713177</td>
      <td>628</td>
    </tr>
    <tr>
      <th>316</th>
      <td>Brewster</td>
      <td>0.0</td>
      <td>42</td>
      <td>51.146531</td>
      <td>47.230816</td>
      <td>0</td>
    </tr>
    <tr>
      <th>238</th>
      <td>Calvert-Lewin</td>
      <td>3.5</td>
      <td>61</td>
      <td>69.803872</td>
      <td>66.585025</td>
      <td>2621</td>
    </tr>
    <tr>
      <th>143</th>
      <td>Wood</td>
      <td>4.2</td>
      <td>62</td>
      <td>70.506130</td>
      <td>69.449357</td>
      <td>2436</td>
    </tr>
    <tr>
      <th>501</th>
      <td>Long</td>
      <td>2.4</td>
      <td>46</td>
      <td>53.929473</td>
      <td>55.430053</td>
      <td>1386</td>
    </tr>
    <tr>
      <th>537</th>
      <td>Janssen</td>
      <td>0.0</td>
      <td>45</td>
      <td>52.514450</td>
      <td>47.230816</td>
      <td>0</td>
    </tr>
    <tr>
      <th>258</th>
      <td>Gordon</td>
      <td>1.5</td>
      <td>45</td>
      <td>52.337608</td>
      <td>49.535491</td>
      <td>436</td>
    </tr>
    <tr>
      <th>206</th>
      <td>Wickham</td>
      <td>2.5</td>
      <td>43</td>
      <td>50.331543</td>
      <td>50.561961</td>
      <td>90</td>
    </tr>
    <tr>
      <th>82</th>
      <td>Surridge</td>
      <td>1.0</td>
      <td>43</td>
      <td>50.213401</td>
      <td>48.554661</td>
      <td>25</td>
    </tr>
    <tr>
      <th>366</th>
      <td>Rashford</td>
      <td>5.7</td>
      <td>89</td>
      <td>96.027890</td>
      <td>93.549209</td>
      <td>2645</td>
    </tr>
    <tr>
      <th>32</th>
      <td>John-Jules</td>
      <td>0.0</td>
      <td>44</td>
      <td>50.650123</td>
      <td>47.230816</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>


