import pandas as pd

path = "source/gyunyu_doko_2512.xlsx"

df_raw = pd.read_excel(
    path,
    sheet_name="3地域別生乳生産量",
    header=None)

df_raw.head(6)

df = df_raw.iloc[3:,[0,1,5]] 
df.columns = ["year", "japan", "hokkaido"]

df["japan"] = pd.to_numeric(df["japan"], errors="coerce")
df["hokkaido"] = pd.to_numeric(df["hokkaido"], errors="coerce")

df = df.dropna(subset=["japan", "hokkaido"])

df = df[df["year"].notna()]

# for col in ["japan", "hokkaido"]:
#     df[col] = (
#         df[col]
#         .astype(str)
#         .str.replace("－", "")
#         .astype(float)
#     )

print(df.head())
print(df.dtypes)
