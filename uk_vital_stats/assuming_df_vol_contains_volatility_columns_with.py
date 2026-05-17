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

def assuming_df_vol_contains_volatility_columns_with() -> None:
    trim_years = 10

    df_trimmed = df_vol[df_vol.index >= df_vol.index.min() + pd.DateOffset(years=trim_years)]

    algo = rpt.Pelt(model='rbf').fit(df_trimmed['Births Volatility'].values)

    birth_breaks = algo.predict(pen=5)

    algo = rpt.Pelt(model='rbf').fit(df_trimmed['Deaths Volatility'].values)

    death_breaks = algo.predict(pen=5)

    algo = rpt.Pelt(model='rbf').fit(df_trimmed['Marriages Volatility'].values)

    marriage_breaks = algo.predict(pen=5)

    plt.figure(figsize=(16, 6))

    plt.plot(df_trimmed.index, df_trimmed['Births Volatility'], label='Births Volatility')

    plt.plot(df_trimmed.index, df_trimmed['Deaths Volatility'], label='Deaths Volatility')

    plt.plot(df_trimmed.index, df_trimmed['Marriages Volatility'], label='Marriages Volatility')

    for idx in birth_breaks:
        if idx < len(df_trimmed):
            plt.axvline(df_trimmed.index[idx], color='blue', linestyle='--', alpha=0.3)

    for idx in death_breaks:
        if idx < len(df_trimmed):
            plt.axvline(df_trimmed.index[idx], color='orange', linestyle='--', alpha=0.3)

    for idx in marriage_breaks:
        if idx < len(df_trimmed):
            plt.axvline(df_trimmed.index[idx], color='green', linestyle='--', alpha=0.3)

    plt.title('5-Year Rolling Volatility of UK Births, Deaths, and Marriages with Structural Breaks (Trimmed)')

    plt.ylabel('Volatility (% change)')

    plt.xlabel('Year')

    plt.legend()

    plt.tight_layout()

    plt.show()

