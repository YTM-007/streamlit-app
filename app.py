import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="生乳生産量の推移", layout="wide")

st.title("日本全国と北海道の生乳生産量の推移")

@st.cache_data()
def load_date():
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

    # print(df.to_string()) 確認用
    # print(df.dtypes)
    return df


df = load_date()

st.sidebar.header("表示条件")

year_min, year_max = st.sidebar.select_slider(
    "表示年範囲",
    options=sorted(df["year"].unique()),
    value=(int(df["year"].min()),int(df["year"].max()))
)

df_view = df[
    (df["year"] >= year_min) &
    (df["year"] <= year_max)
]

df_view = df_view.copy()
df_view["hokkaido_ratio"] = (df_view["hokkaido"] / df_view["japan"])*100

latest = df_view.sort_values("year").iloc[-1]
prev = df_view.sort_values("year").iloc[-2]

ratio_latest = latest["hokkaido"] / latest["japan"] * 100
ratio_prev = prev["hokkaido"] / prev["japan"] * 100

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "全国生産量（最新年）",
        f"{latest['japan']:.0f} 千t",
        delta=f"{latest['japan'] - prev['japan']:+.0f}"
    )

with col2:
    st.metric(
        "北海道生産量（最新年）",
        f"{latest['hokkaido']:.0f} 千t",
        delta=f"{latest['hokkaido'] - prev['hokkaido']:+.0f}"
    )

with col3:
    st.metric(
        "北海道依存率（最新年）",
        f"{ratio_latest:.1f} %",
        delta=f"{ratio_latest - ratio_prev:+.1f} %"
    )
st.markdown("---")

graph_col, _ = st.columns([4,1])

with graph_col:
    tab1, tab2, tab3 = st.tabs(
    ["生乳生産量の推移", "北海道依存率", "使用データ"]
    )
    with tab1:
        st.subheader("生乳生産量の推移")
        st.write("単位：千t")

        st.line_chart(
            df_view.set_index("year")[["japan", "hokkaido"]]
        )

    with tab2:
        st.subheader("北海道生乳生産量の全国依存率")

        st.write("単位：%")

        st.line_chart(
            df_view.set_index("year")[["hokkaido_ratio"]]
        )
        st.caption("※ 北海道の比率は全国生乳生産量に占める割合を示す")
    with tab3:
        st.subheader("使用データ")
        st.dataframe(df, use_container_width=True)



