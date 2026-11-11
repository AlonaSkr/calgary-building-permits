# Step 4 (Analyze): check the Power BI numbers with pandas.
# The definitions match the DAX measures in dax/measures.dax.
# Run from the project folder:  python3 scripts/verify_findings.py

import numpy as np
import pandas as pd

df = pd.read_csv(
    "data/processed/building_permits_clean.csv",
    parse_dates=["AppliedDate", "IssuedDate", "CompletedDate"],
)
df["Year"] = df["AppliedDate"].dt.year

# Same rules as the DAX calculated columns
df["DaysToIssue"] = (df["IssuedDate"] - df["AppliedDate"]).dt.days
df.loc[df["DaysToIssue"] < 0, "DaysToIssue"] = np.nan
df["DaysIssueToComplete"] = (df["CompletedDate"] - df["IssuedDate"]).dt.days
df.loc[df["DaysIssueToComplete"] < 0, "DaysIssueToComplete"] = np.nan
df["ValidCost"] = df["EstProjectCost"].where(df["EstProjectCost"] >= 0)

print("=== Q1: permits and cost per year ===")
by_year = df.groupby("Year").agg(
    permits=("PermitNum", "count"),
    total_cost_bn=("ValidCost", lambda s: round(s.sum() / 1e9, 2)),
    median_cost=("ValidCost", "median"),
    average_cost=("ValidCost", lambda s: round(s.mean())),
)
print(by_year)

print("=== Q2: days to issue ===")
print("Overall median days to issue:", df["DaysToIssue"].median())
print("Share issued same day (%):", round((df["DaysToIssue"] == 0).mean() * 100, 1))
print(df.groupby("PermitType")["DaysToIssue"].agg(["median", "mean", "count"]).round(1))
print(df.groupby("Year")["DaysToIssue"].median().loc[[2000, 2005, 2010, 2015, 2020, 2023, 2024, 2025]])
print("Avg days issue to complete by year:")
print(df.groupby("Year")["DaysIssueToComplete"].mean().round(0).loc[[2000, 2005, 2010, 2015, 2020, 2022, 2023, 2024, 2025]])

print("=== Q3 and Q6: communities and new housing ===")
new_homes = df[(df["WorkClassMapped"] == "New") & (df["PermitClassMapped"] == "Residential")]
print("Top 10 communities by permits:")
print(df.groupby("CommunityName").size().sort_values(ascending=False).head(10))
print("Top 10 communities by new housing units (all years):")
print(new_homes.groupby("CommunityName")["HousingUnits"].sum().sort_values(ascending=False).head(10))
recent = new_homes[new_homes["Year"].between(2021, 2025)].groupby("CommunityName")["HousingUnits"].sum()
print("Top 10 communities by new housing units 2021-2025:")
print(recent.sort_values(ascending=False).head(10))
first_year = new_homes.groupby("CommunityName")["Year"].min()
newest = first_year[first_year >= 2015].index
print("Communities whose first new housing permit is 2015 or later:", len(newest))
print(new_homes[new_homes["CommunityName"].isin(newest) & new_homes["Year"].between(2021, 2025)]
      .groupby("CommunityName")["HousingUnits"].sum().sort_values(ascending=False).head(8))
share_top10 = recent.sort_values(ascending=False).head(10).sum() / recent.sum() * 100
print("Top 10 share of 2021-2025 new units (%):", round(share_top10, 1))

print("=== Q4: outcomes ===")
print((df["StatusCurrent"].value_counts(normalize=True) * 100).round(1).head(6))
df["CancelledOrExpired"] = df["StatusCurrent"].isin(["Cancelled", "Expired"])
print("Cancel/expire rate (%):", round(df["CancelledOrExpired"].mean() * 100, 1))
print((df.groupby("PermitType")["CancelledOrExpired"].mean() * 100).round(1))
print((df.groupby("Year")["CancelledOrExpired"].mean() * 100).round(1).loc[[2000, 2005, 2010, 2015, 2020, 2023, 2024, 2025]])

print("=== Q5: mix ===")
mix = df.groupby("Year").agg(
    residential_pct=("PermitClassMapped", lambda s: round((s == "Residential").mean() * 100, 1)),
    new_work_pct=("WorkClassMapped", lambda s: round((s == "New").mean() * 100, 1)),
)
print(mix.loc[[2000, 2005, 2010, 2015, 2020, 2025]])

print("=== Cost mix effect (2006 vs 2007) ===")
for year in [2006, 2007]:
    part = df[df["Year"] == year]
    print(year, (part["PermitType"].value_counts(normalize=True) * 100).round(1).to_dict())
    print(year, part.groupby("PermitType")["ValidCost"].median().round(0).to_dict())
