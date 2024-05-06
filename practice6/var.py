import os
import warnings
import pandas as pd
import matplotlib.pyplot as plt
from pylab import rcParams
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
from statsmodels.tools.eval_measures import rmse

# Set plot size
rcParams['figure.figsize'] = (12, 5)

# Suppress warnings
warnings.filterwarnings("ignore")

# Load datasets
ds1_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "M2SLMoneyStock.csv")
ds2_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PCEPersonalSpending.csv")

df = pd.read_csv(ds1_file_path, index_col=0, parse_dates=True)
df.index.freq = 'MS'

sp = pd.read_csv(ds2_file_path, index_col=0, parse_dates=True)
sp.index.freq = 'MS'

df = df.join(sp)

# Plot settings
title = 'M2 Money Stock vs Personal Consumption Expenditures'
ylabel = 'Billions of Dollars'
xlabel = '' 

ax = df['Spending'].plot(legend=True, title=title)
ax.autoscale(axis='x', tight=True)
ax.set(xlabel=xlabel, ylabel=ylabel)
df['Money'].plot(legend=True)

def dickey_fuller(series, title='Your Dataset'):
    print(f'Augmented Dickey Fuller Test for the dataset {title}')
    
    result = adfuller(series.dropna(), autolag='AIC')
    labels = ['ADF test statistics', 'p-value', '#lags', '#observations'] 
    
    outcome = pd.Series(result[0:4], index=labels)
    
    for key, val in result[4].items():
        outcome[f'critical value ({key})'] = val
        
    print(outcome.to_string())
    
    if result[1] <= 0.05:
        print('Strong evidence against the null hypothesis') 
        print('Reject the null hypothesis')
        print('Data is Stationary')
    else:
        print('Weak evidence against the Null hypothesis')
        print('Fail to reject the null hypothesis')
        print('Data has a unit root and is non-stationary')

dickey_fuller(df['Money'], title='Money')
dickey_fuller(df['Spending'], title='Spending')

df_diff = df.diff()
df_diff = df_diff.dropna()

dickey_fuller(df_diff['Money'], title='Money 1st Order Diff')
dickey_fuller(df_diff['Spending'], title='Spending 1st Order Diff')

df_diff = df_diff.diff().dropna()
dickey_fuller(df_diff['Money'], title='Money 2nd Order Diff')
dickey_fuller(df_diff['Spending'], title='Spending 2nd Order Diff')

nobs = 12
train = df_diff[:-nobs]
test = df_diff[-nobs:]

p = [1, 2, 3, 4, 5, 6, 7] 

results = None
for i in p:
    model = VAR(train)
    results = model.fit(i)
    print(f'VAR Order {i}')
    print('AIC {}'.format(results.aic))
    print('BIC {}'.format(results.bic))
    print()

    results = model.fit(5)
    results.summary()

    lag_order = results.k_ar
    z = results.forecast(y=train.values[-lag_order:], steps=12)
    print(z)

idx = pd.date_range(start='1/1/2015', periods=12, freq='MS')
df_forecast = pd.DataFrame(z, index=idx, columns=['Money2D', 'Spending2D'])

df_forecast['Money1D'] = (df['Money'].iloc[-nobs-1] - df['Money'].iloc[-nobs-2]) + df_forecast['Money2D'].cumsum()
df_forecast['MoneyForecast'] = df['Money'].iloc[-nobs-1] + df_forecast['Money1D'].cumsum()

df_forecast['Spending1D'] = (df['Spending'].iloc[-nobs-1] - df['Spending'].iloc[-nobs-2]) + df_forecast['Spending2D'].cumsum()
df_forecast['SpendingForecast'] = df['Spending'].iloc[-nobs-1] + df_forecast['Spending1D'].cumsum()

results.plot()
plt.show()

results.plot_forecast(12)
plt.show()

df['Money'][-nobs:].plot(figsize=(12, 5), legend=True).autoscale(axis='x', tight=True)
df_forecast['MoneyForecast'].plot(legend=True)

df['Spending'][-nobs:].plot(figsize=(12, 5), legend=True).autoscale(axis='x', tight=True)
df_forecast['SpendingForecast'].plot(legend=True)

RMSE1 = rmse(df['Money'][-nobs:], df_forecast['MoneyForecast'])
print(f'Money VAR(5) RMSE: {RMSE1:.3f}')

RMSE2 = rmse(df['Spending'][-nobs:], df_forecast['SpendingForecast'])
print(f'Spending VAR(5) RMSE: {RMSE2:.3f}')

plt.show()
