# Step 2 (Prepare): look at the raw data before changing anything.
# Run from the project folder:  python3 scripts/profile_permits.py

import numpy as np
import pandas as pd

# Where the raw file is
raw_file = "data/raw/Building_Permits_20261106.csv"

# These columns are very long and we do not need them, so we skip them when loading
skip_columns = ["LocationsWKT", "LocationsGeoJSON", "Point", "LocationAddresses", "LocationTypes"]

# Load every column as text first (dtype=str) so pandas does not guess types.
# keep_default_na=False means the text "N/A" stays as text; only empty cells become missing.
df = pd.read_csv(
    raw_file,
    dtype=str,
    keep_default_na=False,
    na_values=[""],
    usecols=lambda name: name not in skip_columns,
)

# 1. How big is the table? (rows, columns)
print("Rows and columns:", df.shape)

# 2. Is every PermitNum unique?
print("Duplicate PermitNum:", df["PermitNum"].duplicated().sum())

# 3. How much is missing in each column, and how many different values does it have?
missing_percent = (df.isna().mean() * 100).round(1)
distinct_values = df.nunique()
print(pd.DataFrame({"missing_percent": missing_percent, "distinct_values": distinct_values}))

# 4. Count the values in the main category columns
for column in ["StatusCurrent", "PermitType", "PermitClassMapped", "WorkClassMapped"]:
    print(df[column].value_counts(dropna=False).head(8))
    print()

# 5. Earliest and latest date in each date column
for column in ["AppliedDate", "IssuedDate", "CompletedDate"]:
    dates = pd.to_datetime(df[column], format="%Y/%m/%d")
    print(column, "from", dates.min().date(), "to", dates.max().date())

# 6. Look at project cost. It is text like "$246,090", so remove "$" and "," first.
cost_text = df["EstProjectCost"].str.replace("$", "", regex=False).str.replace(",", "", regex=False)
cost = pd.to_numeric(cost_text)
print("Negative costs:", np.sum(cost < 0))
print(cost.quantile([0.5, 0.9, 0.99]))
