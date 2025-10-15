import pandas as pd
import polars as pl
import altair as alt

cs_df = pl.DataFrame(
    pd.read_json(
        "https://raw.githubusercontent.com/APWright/CSC477-Fall2025/refs/heads/main/Assignment-3/csforca-enrollment.json"
    )
)

cs_agg = (
    cs_df
    .group_by("county")
    .agg([
        pl.col("AP CS").sum().alias("AP CS"),
        pl.col("Non-AP CS").sum().alias("Non-AP CS"),
        pl.col("Overall Enrollment").sum().alias("Overall Enrollment"),
    ])
    .with_columns([
        ((pl.col("AP CS") + pl.col("Non-AP CS")) / pl.col("Overall Enrollment")).alias("CS Rate")
    ])
)

income_df = pd.read_excel("gini_place_county_region_st3-26-14-ada.xlsx")

income_df["county_name"] = income_df["county_name"].str.strip()
income_agg = (
    income_df
    .groupby("county_name", as_index=False)["Median_HH_income"]
    .median()
)

cs_pd = cs_agg.to_pandas()
cs_pd["county"] = cs_pd["county"].str.strip()

merged = pd.merge(
    cs_pd,
    income_agg,
    left_on="county",
    right_on="county_name",
    how="inner"
)

chart = (
    alt.Chart(merged)
    .mark_circle(size=100, opacity=0.8)
    .encode(
        x=alt.X("Median_HH_income:Q", title="Median Household Income (USD)", scale=alt.Scale(zero=False)),
        y=alt.Y("CS Rate:Q", title="CS Enrollment Rate (Proportion)", axis=alt.Axis(format=".0%")),
        tooltip=[
            alt.Tooltip("county:N", title="County"),
            alt.Tooltip("Median_HH_income:Q", title="Median Income", format="$.0f"),
            alt.Tooltip("CS Rate:Q", title="CS Rate", format=".2%")
        ]
    )
    .properties(
        title="CS Enrollment Rate vs. Median Household Income by County",
        width=700,
        height=450
    )
)

trend = chart.transform_regression(
    "Median_HH_income", "CS Rate"
).mark_line(color="red")

final_chart = chart + trend

final_chart.save("visualization_four.svg")
print("saved")
