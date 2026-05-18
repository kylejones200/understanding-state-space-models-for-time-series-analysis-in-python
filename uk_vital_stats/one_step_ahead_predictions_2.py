"""Auto-split from legacy monolithic script."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.structural import UnobservedComponents


def one_step_ahead_predictions_2() -> None:
    from sklearn.metrics import (
        mean_absolute_error,
        mean_absolute_percentage_error,
        mean_squared_error,
    )

    def run_ucm(df, series_name, title):
        series = df[series_name].dropna()
        model = UnobservedComponents(series, level="local level")
        results = model.fit(disp=False)
        # One-step-ahead predictions
        pred = results.get_prediction()
        mean = pred.predicted_mean
        ci = pred.conf_int()
        fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        fig.suptitle(f"State-Space Model for {title}", fontsize=16)
        # Plot observed vs predicted
        axes[0].plot(series.index, series, label="Observed", color="black", linewidth=1)
        axes[0].plot(
            mean.index, mean, label="One-step-ahead predictions", color="steelblue"
        )
        axes[0].fill_between(
            mean.index, ci.iloc[:, 0], ci.iloc[:, 1], color="steelblue", alpha=0.3
        )
        axes[0].legend()
        axes[0].set_title("Predicted vs observed")
        # Extract smoothed level from results.smoothed_state
        smoothed_level = results.smoothed_state[0]  # Index 0 is level component
        smoothed_index = series.index
        # Smoothed level confidence intervals
        level_var = results.smoothed_state_cov[0, 0, :]  # variance of level
        level_std = np.sqrt(level_var)
        lower = smoothed_level - 1.96 * level_std
        upper = smoothed_level + 1.96 * level_std
        axes[1].plot(
            smoothed_index, smoothed_level, label="Level (smoothed)", color="steelblue"
        )
        axes[1].fill_between(smoothed_index, lower, upper, color="steelblue", alpha=0.3)
        axes[1].set_title("Level component")
        axes[1].legend()
        plt.tight_layout()
        plt.subplots_adjust(top=0.90)
        plt.savefig(f"statespace_{series_name.lower()}.png")
        plt.show()
        # Error metrics
        observed = series.loc[mean.index].dropna()
        predicted = mean.loc[observed.index].dropna()
        observed, predicted = observed.align(predicted, join="inner")
        mae = mean_absolute_error(observed, predicted)
        rmse = np.sqrt(mean_squared_error(observed, predicted))
        mape = mean_absolute_percentage_error(observed, predicted)
        print(f"\nError Metrics for {title}:")
        print(f"MAE  = {mae:,.0f}")
        print(f"RMSE = {rmse:,.0f}")
        print(f"MAPE = {mape:.2%}")

    url = "https://raw.githubusercontent.com/kylejones200/time_series/refs/heads/main/Uk%20vital%20statistics%20data%20cleaned_data.csv"
    df = pd.read_csv(url)
    run_ucm(df, "Births", "Births")
