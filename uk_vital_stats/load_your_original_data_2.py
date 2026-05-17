"""Auto-split from legacy monolithic script."""

from linearmodels.panel import PanelOLS
from statsmodels.api import OLS
from statsmodels.tools import add_constant
from statsmodels.tsa.statespace.structural import UnobservedComponents
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ruptures as rpt
import seaborn as sns

def load_your_original_data_2() -> None:
    file_name = '/content/Uk marriage data-unique - Sheet1.csv'

    df = pd.read_csv(file_name)

    df['Year'] = df['Year'].ffill()

    quarter_to_month = {'Mar': '01', 'Jun': '04', 'Sep': '07', 'Dec': '10'}

    df['Month'] = df['Quarter'].map(quarter_to_month)

    df['Date'] = pd.to_datetime(df['Year'].astype(int).astype(str) + '-' + df['Month'])

    df = df.sort_values('Date').set_index('Date')

    df = df[['Births', 'Marriages', 'Deaths']].dropna()

    df['Births_Smoothed'] = df['Births'].rolling(window=4, center=True).mean()

    df['Marriages_Smoothed'] = df['Marriages'].rolling(window=4, center=True).mean()

    df['Deaths_Smoothed'] = df['Deaths'].rolling(window=4, center=True).mean()

    df['Deaths_per_Birth_Smoothed'] = df['Deaths_Smoothed'] / df['Births_Smoothed'] * 1000

    df['Marriages_per_Birth_Smoothed'] = df['Marriages_Smoothed'] / df['Births_Smoothed'] * 1000

    df['Marriages_per_Death_Smoothed'] = df['Marriages_Smoothed'] / df['Deaths_Smoothed'] * 1000

    df = df.dropna(subset=['Deaths_per_Birth_Smoothed', 'Marriages_per_Birth_Smoothed', 'Marriages_per_Death_Smoothed'])

    ratios = ['Deaths_per_Birth_Smoothed', 'Marriages_per_Birth_Smoothed', 'Marriages_per_Death_Smoothed']

    X = df[ratios].values

    model = rpt.Pelt(model='rbf').fit(X)

    breaks = model.predict(pen=10)

    break_dates = df.index[breaks[:-1]]

    plt.figure(figsize=(14, 6))

    for col in ratios:
        plt.plot(df.index, df[col], label=col)

    for date in break_dates:
        plt.axvline(x=date, color='red', linestyle='--', alpha=0.7)

    plt.title('Smoothed Demographic Ratios with Structural Breaks')

    plt.xlabel('Year')

    plt.ylabel('Ratio')

    plt.legend()

    plt.grid(False)

    plt.tight_layout()

    plt.show()

    print('Detected structural breaks:')

    for date in break_dates:
        print(date.strftime('%Y-%m'))

