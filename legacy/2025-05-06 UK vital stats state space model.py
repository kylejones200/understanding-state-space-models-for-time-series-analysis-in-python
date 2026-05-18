"""Generated from Jupyter notebook: 2025-05-06 UK vital stats state space model

Magics and shell lines are commented out. Run with a normal Python interpreter."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ruptures as rpt
import seaborn as sns
from statsmodels.api import OLS
from statsmodels.tools import add_constant
from statsmodels.tsa.statespace.structural import UnobservedComponents


def detect_breaks(series, penalty=5):
    algo = rpt.Pelt(model="l2").fit(series.values)
    result = algo.predict(pen=penalty)
    return result[:-1]


def run_ucm(series_name, title):
    series = df[series_name]
    model = UnobservedComponents(series, level="local level")
    results = model.fit(disp=False)
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle(f"State-Space Model for {title}", fontsize=16)
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
    plt.subplots_adjust(top=0.9)
    plt.show()


def load_and_clean_the_dataset() -> None:
    file_name = "/content/Uk marriage data-unique - Sheet1.csv"
    df = pd.read_csv(file_name)
    df["Year"] = df["Year"].ffill()
    quarter_month_map = {"Mar": 3, "Jun": 6, "Sep": 9, "Dec": 12}
    df["Month"] = df["Quarter"].map(quarter_month_map)
    df["Year"] = df["Year"].astype(int)
    df["Date"] = pd.to_datetime(dict(year=df["Year"], month=df["Month"], day=1))
    df = df.sort_values("Date").set_index("Date")
    df = df[["Births", "Marriages", "Deaths"]].dropna()
    df["Births_Smoothed"] = df["Births"].rolling(window=4, center=True).mean()
    df["Marriages_Smoothed"] = df["Marriages"].rolling(window=4, center=True).mean()
    df["Deaths_Smoothed"] = df["Deaths"].rolling(window=4, center=True).mean()
    df["Deaths_per_Birth"] = df["Deaths"] / df["Births"] * 1000
    df["Marriages_per_Birth"] = df["Marriages"] / df["Births"] * 1000
    df["Marriages_per_Death"] = df["Marriages"] / df["Deaths"] * 1000
    plt.figure(figsize=(14, 6))
    plt.plot(df.index, df["Births"], label="Births", alpha=0.3)
    plt.plot(df.index, df["Births_Smoothed"], label="Births (Smoothed)", linewidth=2)
    plt.plot(df.index, df["Deaths"], label="Deaths", alpha=0.3)
    plt.plot(df.index, df["Deaths_Smoothed"], label="Deaths (Smoothed)", linewidth=2)
    plt.plot(df.index, df["Marriages"], label="Marriages", alpha=0.3)
    plt.plot(
        df.index, df["Marriages_Smoothed"], label="Marriages (Smoothed)", linewidth=2
    )
    events = {
        "1847-01-01": "Famine Peak",
        "1918-10-01": "Spanish Flu",
        "1939-09-01": "WWII Start",
        "1945-05-01": "WWII End",
        "1947-01-01": "Baby Boom Begins",
    }
    for date_str, label in events.items():
        date = pd.to_datetime(date_str)
        plt.axvline(date, color="gray", linestyle="--", alpha=0.5)
        plt.text(date, plt.ylim()[1] * 0.9, label, rotation=90, verticalalignment="top")

    plt.title("UK Quarterly Births, Deaths, and Marriages (1837–1983)")
    plt.xlabel("Year")
    plt.ylabel("Count")
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.show()
    plt.figure(figsize=(14, 6))
    plt.plot(df.index, df["Deaths_per_Birth"], label="Deaths per 1000 Births")
    plt.plot(df.index, df["Marriages_per_Birth"], label="Marriages per 1000 Births")
    plt.plot(df.index, df["Marriages_per_Death"], label="Marriages per 1000 Deaths")
    plt.title("Demographic Ratios Over Time")
    plt.xlabel("Year")
    plt.ylabel("Ratio")
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.show()
    df["Year"] = df.index.year
    df["Quarter_Label"] = df.index.to_period("Q").strftime("%q")
    pivot_births = df.pivot_table(
        values="Births", index="Year", columns="Quarter_Label"
    )
    sns.heatmap(pivot_births, cmap="YlGnBu", linewidths=0.1)
    plt.title("Seasonality of Births by Quarter (1837–1983)")
    plt.ylabel("Year")
    plt.xlabel("Quarter")
    plt.tight_layout()
    plt.show()


def notebook_step_002() -> None:
    df["Deaths_per_Birth_Smoothed"] = (
        df["Deaths_per_Birth"].rolling(window=8, center=True).mean()
    )
    df["Marriages_per_Birth_Smoothed"] = (
        df["Marriages_per_Birth"].rolling(window=8, center=True).mean()
    )
    df["Marriages_per_Death_Smoothed"] = (
        df["Marriages_per_Death"].rolling(window=8, center=True).mean()
    )
    plt.axvspan(
        pd.to_datetime("1914-01-01"),
        pd.to_datetime("1918-12-31"),
        color="gray",
        alpha=0.2,
    )
    plt.axvspan(
        pd.to_datetime("1939-01-01"),
        pd.to_datetime("1945-12-31"),
        color="gray",
        alpha=0.2,
    )
    plt.yscale("log")
    plt.figure(figsize=(14, 6))
    plt.plot(
        df.index,
        df["Deaths_per_Birth_Smoothed"],
        label="Deaths per 1000 Births (Smoothed)",
    )
    plt.plot(
        df.index,
        df["Marriages_per_Birth_Smoothed"],
        label="Marriages per 1000 Births (Smoothed)",
    )
    plt.plot(
        df.index,
        df["Marriages_per_Death_Smoothed"],
        label="Marriages per 1000 Deaths (Smoothed)",
    )
    plt.title("Demographic Ratios Over Time (Smoothed)")
    plt.xlabel("Year")
    plt.ylabel("Ratio")
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.show()


def load_your_original_data() -> None:
    file_name = "Uk marriage data-unique - Sheet1.csv"
    df = pd.read_csv(file_name)
    df["Year"] = df["Year"].ffill()
    quarter_map = {"Mar": "Q1", "Jun": "Q2", "Sep": "Q3", "Dec": "Q4"}
    df["Quarter"] = df["Quarter"].map(quarter_map)
    df["Date"] = pd.to_datetime(
        df["Year"].astype(int).astype(str) + df["Quarter"], format="%YQ%q"
    )
    df = df.sort_values("Date").set_index("Date")
    df = df[["Births", "Marriages", "Deaths"]].dropna()
    df["Births_Smoothed"] = df["Births"].rolling(window=4, center=True).mean()
    df["Marriages_Smoothed"] = df["Marriages"].rolling(window=4, center=True).mean()
    df["Deaths_Smoothed"] = df["Deaths"].rolling(window=4, center=True).mean()
    df["Deaths_per_Birth_Smoothed"] = (
        df["Deaths_Smoothed"] / df["Births_Smoothed"] * 1000
    )
    df["Marriages_per_Birth_Smoothed"] = (
        df["Marriages_Smoothed"] / df["Births_Smoothed"] * 1000
    )
    df["Marriages_per_Death_Smoothed"] = (
        df["Marriages_Smoothed"] / df["Deaths_Smoothed"] * 1000
    )
    df = df.dropna(
        subset=[
            "Deaths_per_Birth_Smoothed",
            "Marriages_per_Birth_Smoothed",
            "Marriages_per_Death_Smoothed",
        ]
    )
    ratios = [
        "Deaths_per_Birth_Smoothed",
        "Marriages_per_Birth_Smoothed",
        "Marriages_per_Death_Smoothed",
    ]
    X = df[ratios].values
    model = rpt.Pelt(model="rbf").fit(X)
    breaks = model.predict(pen=10)
    break_dates = df.index[breaks[:-1]]
    plt.figure(figsize=(14, 6))
    for col in ratios:
        plt.plot(df.index, df[col], label=col)

    for date in break_dates:
        plt.axvline(x=date, color="red", linestyle="--", alpha=0.7)

    plt.title("Smoothed Demographic Ratios with Structural Breaks")
    plt.xlabel("Year")
    plt.ylabel("Ratio")
    plt.legend()
    plt.tight_layout()
    plt.grid(False)
    plt.show()
    print("Detected structural breaks at:")
    for date in break_dates:
        print(date.strftime("%Y-%m"))


def load_your_original_data_2() -> None:
    file_name = "/content/Uk marriage data-unique - Sheet1.csv"
    df = pd.read_csv(file_name)
    df["Year"] = df["Year"].ffill()
    quarter_to_month = {"Mar": "01", "Jun": "04", "Sep": "07", "Dec": "10"}
    df["Month"] = df["Quarter"].map(quarter_to_month)
    df["Date"] = pd.to_datetime(df["Year"].astype(int).astype(str) + "-" + df["Month"])
    df = df.sort_values("Date").set_index("Date")
    df = df[["Births", "Marriages", "Deaths"]].dropna()
    df["Births_Smoothed"] = df["Births"].rolling(window=4, center=True).mean()
    df["Marriages_Smoothed"] = df["Marriages"].rolling(window=4, center=True).mean()
    df["Deaths_Smoothed"] = df["Deaths"].rolling(window=4, center=True).mean()
    df["Deaths_per_Birth_Smoothed"] = (
        df["Deaths_Smoothed"] / df["Births_Smoothed"] * 1000
    )
    df["Marriages_per_Birth_Smoothed"] = (
        df["Marriages_Smoothed"] / df["Births_Smoothed"] * 1000
    )
    df["Marriages_per_Death_Smoothed"] = (
        df["Marriages_Smoothed"] / df["Deaths_Smoothed"] * 1000
    )
    df = df.dropna(
        subset=[
            "Deaths_per_Birth_Smoothed",
            "Marriages_per_Birth_Smoothed",
            "Marriages_per_Death_Smoothed",
        ]
    )
    ratios = [
        "Deaths_per_Birth_Smoothed",
        "Marriages_per_Birth_Smoothed",
        "Marriages_per_Death_Smoothed",
    ]
    X = df[ratios].values
    model = rpt.Pelt(model="rbf").fit(X)
    breaks = model.predict(pen=10)
    break_dates = df.index[breaks[:-1]]
    plt.figure(figsize=(14, 6))
    for col in ratios:
        plt.plot(df.index, df[col], label=col)

    for date in break_dates:
        plt.axvline(x=date, color="red", linestyle="--", alpha=0.7)

    plt.title("Smoothed Demographic Ratios with Structural Breaks")
    plt.xlabel("Year")
    plt.ylabel("Ratio")
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.show()
    print("Detected structural breaks:")
    for date in break_dates:
        print(date.strftime("%Y-%m"))


def yearly_data_assume_your_dataframe_has_year_as_in() -> None:
    yearly_df = df.resample("Y").sum()
    vol_df = yearly_df.pct_change() * 100
    rolling_vol = vol_df.rolling(window=5).std()
    plt.figure(figsize=(14, 6))
    plt.plot(rolling_vol.index.year, rolling_vol["Births"], label="Births Volatility")
    plt.plot(rolling_vol.index.year, rolling_vol["Deaths"], label="Deaths Volatility")
    plt.plot(
        rolling_vol.index.year, rolling_vol["Marriages"], label="Marriages Volatility"
    )
    plt.title("5-Year Rolling Volatility of UK Births, Deaths, and Marriages")
    plt.xlabel("Year")
    plt.ylabel("Volatility (% change)")
    plt.legend()
    plt.tight_layout()
    plt.show()


def load_your_cleaned_volatility_data_already_create() -> None:
    file_name = "/content/Uk marriage data-unique - Sheet1.csv"
    df = pd.read_csv(file_name)
    df["Year"] = df["Year"].ffill()
    quarter_month_map = {"Mar": 3, "Jun": 6, "Sep": 9, "Dec": 12}
    df["Month"] = df["Quarter"].map(quarter_month_map)
    df["Year"] = df["Year"].astype(int)
    df["Date"] = pd.to_datetime(dict(year=df["Year"], month=df["Month"], day=1))
    df = df.sort_values("Date").set_index("Date")
    df = df[["Births", "Marriages", "Deaths"]].dropna()
    df_yearly = df.resample("Y").sum()
    df_pct = df_yearly.pct_change() * 100
    df_vol = df_pct.rolling(window=5).std()
    df_vol.columns = ["Births Volatility", "Marriages Volatility", "Deaths Volatility"]
    df_vol = df_vol.dropna()
    breaks_births = detect_breaks(df_vol["Births Volatility"], penalty=6)
    breaks_deaths = detect_breaks(df_vol["Deaths Volatility"], penalty=6)
    breaks_marriages = detect_breaks(df_vol["Marriages Volatility"], penalty=6)
    plt.figure(figsize=(14, 6))
    plt.plot(df_vol.index, df_vol["Births Volatility"], label="Births Volatility")
    plt.plot(df_vol.index, df_vol["Deaths Volatility"], label="Deaths Volatility")
    plt.plot(df_vol.index, df_vol["Marriages Volatility"], label="Marriages Volatility")
    for idx in breaks_births:
        plt.axvline(df_vol.index[idx], color="blue", linestyle="--", alpha=0.3)

    for idx in breaks_deaths:
        plt.axvline(df_vol.index[idx], color="orange", linestyle="--", alpha=0.3)

    for idx in breaks_marriages:
        plt.axvline(df_vol.index[idx], color="green", linestyle="--", alpha=0.3)

    plt.title(
        "5-Year Rolling Volatility of UK Births, Deaths, and Marriages with Structural Breaks"
    )
    plt.xlabel("Year")
    plt.ylabel("Volatility (% change)")
    plt.legend()
    plt.tight_layout()
    plt.grid(False)
    plt.show()


def assuming_df_vol_contains_volatility_columns_with() -> None:
    trim_years = 10
    df_trimmed = df_vol[
        df_vol.index >= df_vol.index.min() + pd.DateOffset(years=trim_years)
    ]
    algo = rpt.Pelt(model="rbf").fit(df_trimmed["Births Volatility"].values)
    birth_breaks = algo.predict(pen=5)
    algo = rpt.Pelt(model="rbf").fit(df_trimmed["Deaths Volatility"].values)
    death_breaks = algo.predict(pen=5)
    algo = rpt.Pelt(model="rbf").fit(df_trimmed["Marriages Volatility"].values)
    marriage_breaks = algo.predict(pen=5)
    plt.figure(figsize=(16, 6))
    plt.plot(
        df_trimmed.index, df_trimmed["Births Volatility"], label="Births Volatility"
    )
    plt.plot(
        df_trimmed.index, df_trimmed["Deaths Volatility"], label="Deaths Volatility"
    )
    plt.plot(
        df_trimmed.index,
        df_trimmed["Marriages Volatility"],
        label="Marriages Volatility",
    )
    for idx in birth_breaks:
        if idx < len(df_trimmed):
            plt.axvline(df_trimmed.index[idx], color="blue", linestyle="--", alpha=0.3)

    for idx in death_breaks:
        if idx < len(df_trimmed):
            plt.axvline(
                df_trimmed.index[idx], color="orange", linestyle="--", alpha=0.3
            )

    for idx in marriage_breaks:
        if idx < len(df_trimmed):
            plt.axvline(df_trimmed.index[idx], color="green", linestyle="--", alpha=0.3)

    plt.title(
        "5-Year Rolling Volatility of UK Births, Deaths, and Marriages with Structural Breaks (Trimmed)"
    )
    plt.ylabel("Volatility (% change)")
    plt.xlabel("Year")
    plt.legend()
    plt.tight_layout()
    plt.show()


def notebook_step_009() -> None:
    df_vol.head()


def load_and_clean_the_dataset_2() -> None:
    file_name = "/content/Uk marriage data-unique - Sheet1.csv"
    df = pd.read_csv(file_name)
    df["Year"] = df["Year"].ffill()
    quarter_month_map = {"Mar": 3, "Jun": 6, "Sep": 9, "Dec": 12}
    df["Month"] = df["Quarter"].map(quarter_month_map)
    df["Year"] = df["Year"].astype(int)
    df["Date"] = pd.to_datetime(dict(year=df["Year"], month=df["Month"], day=1))
    df = df.sort_values("Date").set_index("Date")
    df = df[["Births", "Marriages", "Deaths"]].dropna()
    df["births_z"] = (df["Births"] - df["Births"].mean()) / df["Births"].std()
    df["deaths_z"] = (df["Deaths"] - df["Deaths"].mean()) / df["Deaths"].std()
    df["marriages_z"] = (df["Marriages"] - df["Marriages"].mean()) / df[
        "Marriages"
    ].std()


def reshape_into_panel_format_index_year_variable() -> None:
    panel_df = df.set_index("year")[["Births", "Deaths", "Marriages"]]
    panel_data = panel_df.copy()
    panel_data["const"] = 1
    panel_data = panel_data.reset_index()
    panel_data = panel_data.set_index(["year"])
    X = panel_data[["Births", "Marriages"]]
    y = panel_data["Deaths"]
    X = add_constant(X)
    ols_model = OLS(y, X).fit()
    print(ols_model.summary())


def notebook_step_012() -> None:
    df.head()


def we_ll_model_deaths_as_trend_regression_on_births() -> None:
    mod = UnobservedComponents(
        endog=df["Deaths"], level="local level", exog=df[["Births", "Marriages"]]
    )
    res = mod.fit()
    print(res.summary())
    res.plot_components(legend_loc="lower right", figsize=(12, 8))
    plt.tight_layout()
    plt.show()


def load_and_clean_the_dataset_3() -> None:
    file_name = "/content/Uk marriage data-unique - Sheet1.csv"
    df = pd.read_csv(file_name)
    df["Year"] = df["Year"].ffill()
    quarter_month_map = {"Mar": 3, "Jun": 6, "Sep": 9, "Dec": 12}
    df["Month"] = df["Quarter"].map(quarter_month_map)
    df["Year"] = df["Year"].astype(int)
    df["Date"] = pd.to_datetime(dict(year=df["Year"], month=df["Month"], day=1))
    df = df.sort_values("Date").set_index("Date")
    df = df[["Births", "Marriages", "Deaths"]].dropna()
    model_births = UnobservedComponents(
        df["Births"], level="local level", exog=df[["Deaths", "Marriages"]]
    )
    model_marriages = UnobservedComponents(
        df["Marriages"], level="local level", exog=df[["Births", "Deaths"]]
    )
    results_births = model_births.fit(disp=False)
    results_marriages = model_marriages.fit(disp=False)
    fig_births = results_births.plot_components(
        legend_loc="lower right", figsize=(12, 8)
    )
    fig_births.suptitle("State-Space Model for Births", fontsize=14)
    fig_marriages = results_marriages.plot_components(
        legend_loc="lower right", figsize=(12, 8)
    )
    fig_marriages.suptitle("State-Space Model for Marriages", fontsize=14)
    plt.show()


def load_and_clean_the_dataset_4() -> None:
    file_name = "/content/Uk marriage data-unique - Sheet1.csv"
    df = pd.read_csv(file_name)
    df["Year"] = df["Year"].ffill()
    quarter_month_map = {"Mar": 3, "Jun": 6, "Sep": 9, "Dec": 12}
    df["Month"] = df["Quarter"].map(quarter_month_map)
    df["Year"] = df["Year"].astype(int)
    df["Date"] = pd.to_datetime(dict(year=df["Year"], month=df["Month"], day=1))
    df = df.sort_values("Date").set_index("Date")
    df = df[["Births", "Marriages", "Deaths"]].dropna()
    df = df.asfreq("QE")
    df.interpolate(method="linear", inplace=True)
    run_ucm("Births", "Births")
    run_ucm("Deaths", "Deaths")
    run_ucm("Marriages", "Marriages")


def fit_the_local_level_model() -> None:
    import matplotlib.pyplot as plt
    from statsmodels.tsa.statespace.structural import UnobservedComponents

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

    # Example usage:
    # df = pd.read_csv('your_data.csv', parse_dates=['Date'], index_col='Date')
    # df = df.asfreq('Q')
    # run_ucm(df, 'Births', 'Births')
    # run_ucm(df, 'Deaths', 'Deaths')
    # run_ucm(df, 'Marriages', 'Marriages')


def one_step_ahead_predictions() -> None:
    import matplotlib.pyplot as plt
    import numpy as np
    from sklearn.metrics import (
        mean_absolute_error,
        mean_absolute_percentage_error,
        mean_squared_error,
    )
    from statsmodels.tsa.statespace.structural import UnobservedComponents

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

    run_ucm(df, "Births", "Births")


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


def load_and_clean_the_dataset_5() -> None:
    file_name = "/content/Uk marriage data-unique - Sheet1.csv"
    df = pd.read_csv(file_name)
    df["Year"] = df["Year"].ffill()
    quarter_month_map = {"Mar": 3, "Jun": 6, "Sep": 9, "Dec": 12}
    df["Month"] = df["Quarter"].map(quarter_month_map)
    df["Year"] = df["Year"].astype(int)
    df["Date"] = pd.to_datetime(dict(year=df["Year"], month=df["Month"], day=1))
    df = df.sort_values("Date").set_index("Date")
    df = df[["Births", "Marriages", "Deaths"]].dropna()
    df.to_csv("Uk vital statistics data cleaned_data.csv")


def one_step_ahead_predictions_2() -> None:
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from sklearn.metrics import (
        mean_absolute_error,
        mean_absolute_percentage_error,
        mean_squared_error,
    )
    from statsmodels.tsa.statespace.structural import UnobservedComponents

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
                mean.index[:i],
                ci.iloc[:i, 0],
                ci.iloc[:i, 1],
                color="steelblue",
                alpha=0.3,
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


def main() -> None:
    load_and_clean_the_dataset()
    notebook_step_002()
    load_your_original_data()
    load_your_original_data_2()
    yearly_data_assume_your_dataframe_has_year_as_in()
    load_your_cleaned_volatility_data_already_create()
    assuming_df_vol_contains_volatility_columns_with()
    notebook_step_009()
    load_and_clean_the_dataset_2()
    reshape_into_panel_format_index_year_variable()
    notebook_step_012()
    we_ll_model_deaths_as_trend_regression_on_births()
    load_and_clean_the_dataset_3()
    load_and_clean_the_dataset_4()
    fit_the_local_level_model()
    one_step_ahead_predictions()
    ensure_datetime_index()
    load_and_clean_the_dataset_5()
    one_step_ahead_predictions_2()
    observed_vs_predicted_up_to_index_i()


if __name__ == "__main__":
    main()
