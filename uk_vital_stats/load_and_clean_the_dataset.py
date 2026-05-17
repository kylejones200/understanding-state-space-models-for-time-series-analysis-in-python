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

def load_and_clean_the_dataset() -> None:
    file_name = '/content/Uk marriage data-unique - Sheet1.csv'

    df = pd.read_csv(file_name)

    df['Year'] = df['Year'].ffill()

    quarter_month_map = {'Mar': 3, 'Jun': 6, 'Sep': 9, 'Dec': 12}

    df['Month'] = df['Quarter'].map(quarter_month_map)

    df['Year'] = df['Year'].astype(int)

    df['Date'] = pd.to_datetime(dict(year=df['Year'], month=df['Month'], day=1))

    df = df.sort_values('Date').set_index('Date')

    df = df[['Births', 'Marriages', 'Deaths']].dropna()

    df['Births_Smoothed'] = df['Births'].rolling(window=4, center=True).mean()

    df['Marriages_Smoothed'] = df['Marriages'].rolling(window=4, center=True).mean()

    df['Deaths_Smoothed'] = df['Deaths'].rolling(window=4, center=True).mean()

    df['Deaths_per_Birth'] = df['Deaths'] / df['Births'] * 1000

    df['Marriages_per_Birth'] = df['Marriages'] / df['Births'] * 1000

    df['Marriages_per_Death'] = df['Marriages'] / df['Deaths'] * 1000

    plt.figure(figsize=(14, 6))

    plt.plot(df.index, df['Births'], label='Births', alpha=0.3)

    plt.plot(df.index, df['Births_Smoothed'], label='Births (Smoothed)', linewidth=2)

    plt.plot(df.index, df['Deaths'], label='Deaths', alpha=0.3)

    plt.plot(df.index, df['Deaths_Smoothed'], label='Deaths (Smoothed)', linewidth=2)

    plt.plot(df.index, df['Marriages'], label='Marriages', alpha=0.3)

    plt.plot(df.index, df['Marriages_Smoothed'], label='Marriages (Smoothed)', linewidth=2)

    events = {'1847-01-01': 'Famine Peak', '1918-10-01': 'Spanish Flu', '1939-09-01': 'WWII Start', '1945-05-01': 'WWII End', '1947-01-01': 'Baby Boom Begins'}

    for date_str, label in events.items():
        date = pd.to_datetime(date_str)
        plt.axvline(date, color='gray', linestyle='--', alpha=0.5)
        plt.text(date, plt.ylim()[1] * 0.9, label, rotation=90, verticalalignment='top')

    plt.title('UK Quarterly Births, Deaths, and Marriages (1837–1983)')

    plt.xlabel('Year')

    plt.ylabel('Count')

    plt.legend()

    plt.grid(False)

    plt.tight_layout()

    plt.show()

    plt.figure(figsize=(14, 6))

    plt.plot(df.index, df['Deaths_per_Birth'], label='Deaths per 1000 Births')

    plt.plot(df.index, df['Marriages_per_Birth'], label='Marriages per 1000 Births')

    plt.plot(df.index, df['Marriages_per_Death'], label='Marriages per 1000 Deaths')

    plt.title('Demographic Ratios Over Time')

    plt.xlabel('Year')

    plt.ylabel('Ratio')

    plt.legend()

    plt.grid(False)

    plt.tight_layout()

    plt.show()

    df['Year'] = df.index.year

    df['Quarter_Label'] = df.index.to_period('Q').strftime('%q')

    pivot_births = df.pivot_table(values='Births', index='Year', columns='Quarter_Label')

    sns.heatmap(pivot_births, cmap='YlGnBu', linewidths=0.1)

    plt.title('Seasonality of Births by Quarter (1837–1983)')

    plt.ylabel('Year')

    plt.xlabel('Quarter')

    plt.tight_layout()

    plt.show()

