# Step 3 (Process): clean the raw file and save a new file for Power BI.
# Run from the project folder:  python3 scripts/clean_permits.py

import numpy as np
import pandas as pd

# Where to read from and where to save
raw_file = "data/raw/Building_Permits_20261106.csv"
clean_file = "data/processed/building_permits_clean.csv"

# The columns we want to keep. We leave out the long location columns and also the
# names, free-text description and street address, so no personal or company details are shared.
keep_columns = [
    "PermitNum", "StatusCurrent", "AppliedDate", "IssuedDate", "CompletedDate",
    "PermitType", "PermitTypeMapped", "PermitClass", "PermitClassGroup", "PermitClassMapped",
    "WorkClass", "WorkClassGroup", "WorkClassMapped",
    "HousingUnits", "EstProjectCost", "TotalSqFt",
    "CommunityCode", "CommunityName", "Latitude", "Longitude",
]
date_columns = ["AppliedDate", "IssuedDate", "CompletedDate"]
number_columns = ["EstProjectCost", "TotalSqFt", "HousingUnits"]

# Step 1: load the file. Everything is loaded as text.
# keep_default_na=False keeps the text "N/A" (it is a real community name value).
df = pd.read_csv(
    raw_file,
    usecols=keep_columns,
    dtype=str,
    encoding="utf-8-sig",
    keep_default_na=False,
    na_values=[""],
)
df = df[keep_columns]  # put the columns in our order

# Step 2: remove extra spaces at the start and end of every text value
for column in keep_columns:
    df[column] = df[column].str.strip()

# Step 3: turn date text like "2013/07/08" into real dates
for column in date_columns:
    df[column] = pd.to_datetime(df[column], format="%Y/%m/%d")

# Step 4: turn text like "$246,090" into the number 246090
for column in number_columns:
    no_dollar = df[column].str.replace("$", "", regex=False)
    no_comma = no_dollar.str.replace(",", "", regex=False)
    df[column] = pd.to_numeric(no_comma)

# Step 5: make community names look the same (SADDLE RIDGE -> Saddle Ridge)
df["CommunityName"] = df["CommunityName"].str.title()

# Step 6: if WorkClassMapped is empty, write "Unspecified"
df["WorkClassMapped"] = np.where(df["WorkClassMapped"].isna(), "Unspecified", df["WorkClassMapped"])

# Step 7: count rows that look wrong. We keep them in the file; DAX will ignore them.
issued_before_applied = df["IssuedDate"] < df["AppliedDate"]
completed_before_issued = df["CompletedDate"] < df["IssuedDate"]
bad_dates = (issued_before_applied | completed_before_issued).sum()
negative_costs = (df["EstProjectCost"] < 0).sum()
print("Rows:", len(df))
print("Rows with dates in the wrong order:", bad_dates)
print("Rows with negative cost:", negative_costs)

# Step 8: save the clean file. float_format makes 246090.0 print as 246090.
df.to_csv(clean_file, index=False, date_format="%Y-%m-%d", float_format="%.15g")
print("Saved", clean_file)
