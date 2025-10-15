import pandas as pd
import polars as pl
import altair as alt

df = pl.DataFrame(
    pd.read_json(
        "https://raw.githubusercontent.com/APWright/CSC477-Fall2025/refs/heads/main/Assignment-3/csforca-enrollment.json"
    )
)

agg_df = (
    df
    .group_by("county")
    .agg([
        pl.col("AP CS").sum().alias("AP CS"),
        pl.col("Non-AP CS").sum().alias("Non-AP CS"),
        pl.col("Overall Enrollment").sum().alias("Overall Enrollment"),
    ])
)

agg_df = agg_df.with_columns([
    (pl.col("AP CS") + pl.col("Non-AP CS")).alias("Total CS"),
    ((pl.col("AP CS") + pl.col("Non-AP CS")) / pl.col("Overall Enrollment")).alias("CS Enrollment Rate"),
])

top20 = (
    agg_df
    .sort("CS Enrollment Rate", descending=True)
    .head(20)
)

df_pd = top20.to_pandas()

chart = (
    alt.Chart(df_pd)
    .mark_bar()
    .encode(
        x=alt.X(
            "county:N",
            sort="-y",
            title="County",
            axis=alt.Axis(labelAngle=-40)
        ),
        y=alt.Y(
            "CS Enrollment Rate:Q",
            title="CS Enrollment Rate (Proportion)",
            axis=alt.Axis(format=".0%")
        ),
        tooltip=[
            alt.Tooltip("county:N", title="County"),
            alt.Tooltip("CS Enrollment Rate:Q", title="CS Enrollment Rate", format=".2%"),
            alt.Tooltip("Total CS:Q", title="Total CS Students"),
            alt.Tooltip("Overall Enrollment:Q", title="Total Enrollment")
        ],
    )
    .properties(
        title="Top 20 California Counties by CS Enrollment Rate",
        width=700,
        height=400
    )
    .configure_mark(strokeWidth=0)
)

chart.save("visualization_two.svg")
print("saved")
