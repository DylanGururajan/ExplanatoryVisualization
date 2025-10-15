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
    .group_by(["county", "race"])
    .agg([
        pl.col("AP CS").sum().alias("AP CS"),
        pl.col("Non-AP CS").sum().alias("Non-AP CS"),
        pl.col("Overall Enrollment").sum().alias("Overall Enrollment"),
    ])
)

top5 = (
    agg_df
    .group_by("county")
    .agg(pl.col("Overall Enrollment").sum().alias("total_enrollment"))
    .sort("total_enrollment", descending=True)
    .head(5)
    ["county"]
    .to_list()
)

print("Top 5 counties by overall enrollment:", top5)

filtered = agg_df.filter(pl.col("county").is_in(top5))

long_df = filtered.unpivot(
    on=["AP CS", "Non-AP CS", "Overall Enrollment"],
    index=["county", "race"],
    variable_name="Category",
    value_name="Students"
)

melted = long_df.to_pandas()

abbrev_map = {
    "Hispanic/Latino": "Hispanic",
    "Black or African American": "Black",
    "Native Hawaiian or Pacific Islander": "Pacific Isl.",
    "American Indian or Alaska Native": "Indigenous",
    "Two or More Races": "Multiracial",
}
melted["race_short"] = melted["race"].replace(abbrev_map)

melted["County-Race"] = melted["county"] + " – " + melted["race_short"]

chart = (
    alt.Chart(melted)
    .mark_bar()
    .encode(
        x=alt.X(
            "County-Race:N",
            title="County and Race",
            axis=alt.Axis(labelAngle=-40, labelFontSize=10)
        ),
        y=alt.Y("Students:Q", title="Total Students"),
        color=alt.Color(
            "Category:N",
            scale=alt.Scale(
                domain=["AP CS", "Non-AP CS", "Overall Enrollment"],
                range=["#1f77b4", "#ff7f0e", "#2ca02c"],
            ),
            title="Enrollment Type"
        )
    )
    .properties(
        title="Computer Science Enrollment by County and Race (Top 5 Counties)",
        width=700,
        height=400
    )
)

chart.save("visualization_one.svg")
print("saved")
