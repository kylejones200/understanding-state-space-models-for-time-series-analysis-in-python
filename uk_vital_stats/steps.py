"""Auto-split from legacy monolithic script."""

import matplotlib.pyplot as plt
import pandas as pd
import ruptures as rpt
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
