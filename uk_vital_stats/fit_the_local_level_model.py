"""Auto-split from legacy monolithic script."""

import matplotlib.pyplot as plt
import numpy as np
from statsmodels.tsa.statespace.structural import UnobservedComponents


def fit_the_local_level_model() -> None:

    def run_ucm(df, series_name, title):
        series = df[series_name]
        # Fit the local level model
        model = UnobservedComponents(series, level="local level")
        results = model.fit(disp=False)
        # Plot predicted vs observed
        fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        fig.suptitle(f"State-Space Model for {title}", fontsize=16)
        # One-step-ahead predictions
        pred = results.get_prediction()
        mean = pred.predicted_mean
        ci = pred.conf_int()
        axes[0].plot(series.index, series, label="Observed", color="black", linewidth=1)
        axes[0].plot(
            mean.index, mean, label="One-step-ahead predictions", color="steelblue"
        )
        axes[0].fill_between(
            mean.index, ci.iloc[:, 0], ci.iloc[:, 1], color="steelblue", alpha=0.3
        )
        axes[0].legend()
        axes[0].set_title("Predicted vs observed")
        # Smoothed level
        level = results.level_smoothed
        level_ci = results.get_smoothed_conf_int(alpha=0.05)
        axes[1].plot(series.index, level, label="Level (smoothed)", color="steelblue")
        axes[1].fill_between(
            series.index,
            level_ci["level_smoothed_lower"],
            level_ci["level_smoothed_upper"],
            color="steelblue",
            alpha=0.3,
        )
        axes[1].set_title("Level component")
        axes[1].legend()
        plt.tight_layout()
        plt.subplots_adjust(top=0.90)
        plt.savefig(f"statespace_{series_name.lower()}.png")
        plt.show()
        from sklearn.metrics import (
            mean_absolute_error,
            mean_absolute_percentage_error,
            mean_squared_error,
        )

        # Drop any NaNs before calculating metrics
        observed = series.loc[mean.index].dropna()
        predicted = mean.loc[observed.index].dropna()
        # Align lengths
        observed, predicted = observed.align(predicted, join="inner")
        # Compute metrics
        mae = mean_absolute_error(observed, predicted)
        mse = mean_squared_error(observed, predicted)
        rmse = np.sqrt(mse)
        mape = mean_absolute_percentage_error(observed, predicted)
        print(f"\nError Metrics for {title}:")
        print(f"MAE  = {mae:,.0f}")
        print(f"RMSE = {rmse:,.0f}")
        print(f"MAPE = {mape:.2%}")
