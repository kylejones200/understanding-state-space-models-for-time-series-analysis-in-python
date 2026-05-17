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

def load_your_cleaned_volatility_data_already_create() -> None:
    file_name = '/content/Uk marriage data-unique - Sheet1.csv'

    df = pd.read_csv(file_name)

    df['Year'] = df['Year'].ffill()

    quarter_month_map = {'Mar': 3, 'Jun': 6, 'Sep': 9, 'Dec': 12}

    df['Month'] = df['Quarter'].map(quarter_month_map)

    df['Year'] = df['Year'].astype(int)

    df['Date'] = pd.to_datetime(dict(year=df['Year'], month=df['Month'], day=1))

    df = df.sort_values('Date').set_index('Date')

    df = df[['Births', 'Marriages', 'Deaths']].dropna()

    df_yearly = df.resample('Y').sum()

    df_pct = df_yearly.pct_change() * 100

    df_vol = df_pct.rolling(window=5).std()

    df_vol.columns = ['Births Volatility', 'Marriages Volatility', 'Deaths Volatility']

    df_vol = df_vol.dropna()

    breaks_births = detect_breaks(df_vol['Births Volatility'], penalty=6)

    breaks_deaths = detect_breaks(df_vol['Deaths Volatility'], penalty=6)

    breaks_marriages = detect_breaks(df_vol['Marriages Volatility'], penalty=6)

    plt.figure(figsize=(14, 6))

    plt.plot(df_vol.index, df_vol['Births Volatility'], label='Births Volatility')

    plt.plot(df_vol.index, df_vol['Deaths Volatility'], label='Deaths Volatility')

    plt.plot(df_vol.index, df_vol['Marriages Volatility'], label='Marriages Volatility')

    for idx in breaks_births:
        plt.axvline(df_vol.index[idx], color='blue', linestyle='--', alpha=0.3)

    for idx in breaks_deaths:
        plt.axvline(df_vol.index[idx], color='orange', linestyle='--', alpha=0.3)

    for idx in breaks_marriages:
        plt.axvline(df_vol.index[idx], color='green', linestyle='--', alpha=0.3)

    plt.title('5-Year Rolling Volatility of UK Births, Deaths, and Marriages with Structural Breaks')

    plt.xlabel('Year')

    plt.ylabel('Volatility (% change)')

    plt.legend()

    plt.tight_layout()

    plt.grid(False)

    plt.show()

