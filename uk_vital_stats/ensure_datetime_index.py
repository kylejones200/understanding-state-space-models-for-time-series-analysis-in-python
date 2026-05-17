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

def ensure_datetime_index() -> None:
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from statsmodels.tsa.statespace.structural import UnobservedComponents


    def run_ucm(df, series_name, title):
        # Ensure datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("The DataFrame index must be a DatetimeIndex.")

        # Ensure quarterly frequency
        df = df.asfreq("Q")

        # Clean the series: drop NaNs and ensure it's float
        series = df[series_name].copy()
        series = pd.to_numeric(series, errors="coerce")  # force conversion
        series = series.fillna(method="ffill").fillna(method="bfill")  # handle NaNs

        if series.isnull().any() or len(series) < 10:
            raise ValueError(
                f"{series_name} still has missing or insufficient data after cleaning."
            )

        # Fit the state-space model
        model = UnobservedComponents(series, level="local level")
        results = model.fit(disp=False)

        # One-step-ahead predictions
        pred = results.get_prediction()
        mean = pred.predicted_mean
        ci = pred.conf_int()

        # Smoothed level
        level = results.level_smoothed
        level_ci = results.get_smoothed_conf_int(alpha=0.05)

        # Plot
        fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        fig.suptitle(f"State-Space Model for {title}", fontsize=16)

        # Observed vs predicted
        axes[0].plot(series.index, series, label="Observed", color="black", linewidth=1)
        axes[0].plot(mean.index, mean, label="One-step prediction", color="blue")
        axes[0].fill_between(
            mean.index, ci.iloc[:, 0], ci.iloc[:, 1], color="blue", alpha=0.3
        )
        axes[0].legend()
        axes[0].set_title("Observed vs Predicted")

        # Level component
        axes[1].plot(series.index, level, label="Smoothed Level", color="blue")
        axes[1].fill_between(
            series.index,
            level_ci["level_smoothed_lower"],
            level_ci["level_smoothed_upper"],
            color="blue",
            alpha=0.3,
        )
        axes[1].legend()
        axes[1].set_title("Smoothed Level Component")

        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
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

