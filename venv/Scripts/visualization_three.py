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
    .group_by("race")
    .agg([
        pl.col("AP CS").sum().alias("AP CS"),
        pl.col("Non-AP CS").sum().alias("Non-AP CS"),
        pl.col("Overall Enrollment").sum().alias("Overall Enrollment"),
    ])
)

agg_df = agg_df.with_columns([
    ((pl.col("AP CS") + pl.col("Non-AP CS")) / pl.col("Overall Enrollment")).alias("Overall CS Rate"),
    (pl.col("AP CS") / pl.col("Overall Enrollment")).alias("AP CS Rate"),
    (pl.col("Non-AP CS") / pl.col("Overall Enrollment")).alias("Non-AP CS Rate"),
])

agg_df = agg_df.sort("Overall CS Rate", descending=False)

df_pd = agg_df.to_pandas()

melted = df_pd.melt(
    id_vars=["race", "Overall Enrollment", "Overall CS Rate"],
    value_vars=["AP CS Rate", "Non-AP CS Rate"],
    var_name="Category",
    value_name="Rate"
)

melted["Category"] = melted["Category"].replace({
    "AP CS Rate": "AP CS",
    "Non-AP CS Rate": "Non-AP CS"
})

color_scale = alt.Scale(
    domain=["Non-AP CS", "AP CS"],
    range=["#1f77b4", "#ff7f0e"]
)

chart = (
    alt.Chart(melted)
    .mark_bar()
    .encode(
        x=alt.X(
            "Rate:Q",
            title="CS Enrollment Rate",
            axis=alt.Axis(
                format=".0%",
                tickCount=8,
                values=[i / 100 for i in range(0, 15, 2)]
            ),
            scale=alt.Scale(domain=[0, 0.14])
        ),
        y=alt.Y(
            "race:N",
            title="Race / Ethnicity",
            sort=melted["race"].tolist()
        ),
        color=alt.Color(
            "Category:N",
            title="Course Type",
            scale=color_scale
        ),
        tooltip=[
            alt.Tooltip("race:N", title="Race"),
            alt.Tooltip("Category:N", title="Course Type"),
            alt.Tooltip("Rate:Q", title="Enrollment Rate", format=".2%"),
            alt.Tooltip("Overall CS Rate:Q", title="Overall CS Rate", format=".2%")
        ]
    )
    .properties(
        title="CS Enrollment Rates by Race",
        width=650,
        height=350
    )
    .configure_axis(
        labelFontSize=11,
        titleFontSize=12
    )
    .configure_title(
        fontSize=14,
        anchor="middle"
    )
)

chart.save("visualization_three.svg")
print("saved")
