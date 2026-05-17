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

def observed_vs_predicted_up_to_index_i() -> None:
    import io

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from PIL import Image
    from sklearn.metrics import (
        mean_absolute_error,
        mean_absolute_percentage_error,
        mean_squared_error,
    )
    from statsmodels.tsa.statespace.structural import UnobservedComponents


    def run_ucm_with_gif(df, series_name, title):
        series = df[series_name].dropna()
        model = UnobservedComponents(series, level="local level")
        results = model.fit(disp=False)

        pred = results.get_prediction()
        mean = pred.predicted_mean
        ci = pred.conf_int()

        smoothed_level = results.smoothed_state[0]
        smoothed_index = series.index

        level_var = results.smoothed_state_cov[0, 0, :]
        level_std = np.sqrt(level_var)
        lower = smoothed_level - 1.96 * level_std
        upper = smoothed_level + 1.96 * level_std

        frames = []
        for i in range(10, len(series)):
            fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
            fig.suptitle(f"State-Space Model for {title}", fontsize=16)

            # Observed vs predicted up to index i
            axes[0].plot(
                series.index[:i],
                series.values[:i],
                label="Observed",
                color="black",
                linewidth=1,
            )
            axes[0].plot(
                mean.index[:i], mean.values[:i], label="Prediction", color="steelblue"
            )
            axes[0].fill_between(
                mean.index[:i], ci.iloc[:i, 0], ci.iloc[:i, 1], color="steelblue", alpha=0.3
            )
            axes[0].legend()
            axes[0].set_title("Predicted vs observed")

            # Smoothed level up to index i
            axes[1].plot(
                smoothed_index[:i],
                smoothed_level[:i],
                label="Level (smoothed)",
                color="steelblue",
            )
            axes[1].fill_between(
                smoothed_index[:i], lower[:i], upper[:i], color="steelblue", alpha=0.3
            )
            axes[1].set_title("Level component")
            axes[1].legend()

            plt.tight_layout()
            plt.subplots_adjust(top=0.90)

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            image = Image.open(buf)
            frames.append(image.convert("RGB"))
            plt.close()

        frames[0].save(
            f"statespace_{series_name.lower()}.gif",
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=150,
            loop=0,
        )

        # Print error metrics
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


    # Load data
    url = "https://raw.githubusercontent.com/kylejones200/time_series/refs/heads/main/Uk%20vital%20statistics%20data%20cleaned_data.csv"
    df = pd.read_csv(url, parse_dates=["Date"], index_col="Date")

    # Run
    run_ucm_with_gif(df, "Births", "Births")

