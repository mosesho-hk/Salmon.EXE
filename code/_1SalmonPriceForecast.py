# Jason: This entire code is made by Moses. I do not know what anything in this file means. I am in agony. Send eye bleach.

import pandas as pd
from datetime import date


raw = pd.read_excel(
    "Salmon.EXE\data\Salmon_data.xlsx",
    sheet_name="Vekt",
    header=None,
    engine="openpyxl"
)

# Keep weekly observations, excluding headers and footnotes.
is_week = raw[1].astype(str).str.fullmatch(r"\d{4}U\d{2}")

df = raw.loc[is_week, [1, 2, 3]].copy()
df.columns = ["week", "volume_tonnes", "price_nok_kg"]

# Convert ISO week labels into the Monday of each week.
df["date"] = pd.to_datetime(
    df["week"].map(
        lambda w: date.fromisocalendar(
            int(w[:4]), int(w[5:]), 1
        )
    )
)

for col in ["volume_tonnes", "price_nok_kg"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.sort_values("date").set_index("date")

assert not df.index.duplicated().any(), "Duplicate weeks found"

# Preserve a regular weekly index so shifts always mean weeks.
df = df.asfreq("W-MON")

print("Rows:", len(df), "\n")
print("Missing values:")
print(df[["volume_tonnes", "price_nok_kg"]].isna().sum())

