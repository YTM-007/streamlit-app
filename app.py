import pandas as pd
import re

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

df["year"] = df["year"].astype(str)
df = df[~df["year"].str.contains("月", na=False)]
df = df[~df["year"].str.contains("累", na=False)]

def to_seireki(x):
    x = x.strip()

    if "昭和" in x:
        y = int(re.sub(r"\D","",x))
        return y + 1925
    if "平成" in x:
        if "元" in x:
            return 1989
        y = int(re.sub(r"\D","",x))
        return y + 1988
    if "令和" in x:
        if "元" in x:
            return 2019
        y = int(re.sub(r"\D","",x))
        return y + 2018
    
    return None

df["era"] = (
    df["year"]
    .where(df["year"].str.contains("昭和|平成|令和"))
    .ffill()
)

def normalize_year_text(x):
    x = x.strip()
    x = x.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    return x

df["year"] = df["year"].apply(normalize_year_text)

df["year_full"] = df["era"].str.extract("(昭和|平成|令和)",expand=False) + df["year"]
df["year"] = df["year_full"].apply(to_seireki)

df = df.drop(columns=["era", "year_full"])

df = df[df["japan"] > 1000]

print(df.to_string())
print(df.dtypes)
