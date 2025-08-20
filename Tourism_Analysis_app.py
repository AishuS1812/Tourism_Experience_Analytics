# tourism_app.py  — final robust version

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, f1_score
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Optional recommender (graceful fallback if not installed)
try:
    from surprise import Dataset, Reader, SVD
    from surprise.model_selection import train_test_split as surprise_split
    SURPRISE_OK = True
except Exception:
    SURPRISE_OK = False


# ------------------------------- Helpers ------------------------------- #
def normalize_df(df: pd.DataFrame | None) -> pd.DataFrame | None:
    """Lowercase/strip column names; return None untouched."""
    if df is None:
        return None
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def rename_with_aliases(df: pd.DataFrame | None, alias_map: dict[str, list[str]]) -> pd.DataFrame | None:
    """Rename columns in df to their canonical names based on alias_map."""
    if df is None:
        return None
    df = df.copy()
    cols = set(df.columns)
    for canonical, aliases in alias_map.items():
        if canonical in cols:
            continue
        for a in aliases:
            if a in cols:
                df.rename(columns={a: canonical}, inplace=True)
                cols.add(canonical)
                break
    return df


def safe_merge(left: pd.DataFrame, right: pd.DataFrame | None, key: str) -> pd.DataFrame:
    """Merge left and right on key if the key exists in BOTH dataframes."""
    if right is None:
        return left
    k = key.lower()
    if k in left.columns and k in right.columns:
        return left.merge(right.drop_duplicates(), on=k, how="left")
    return left


def load_excel_dict(file) -> dict[str, pd.DataFrame]:
    """Read all sheets into a dict with lowercase sheet names."""
    xls = pd.ExcelFile(file)
    return {s.strip().lower(): pd.read_excel(file, sheet_name=s) for s in xls.sheet_names}


def get_sheet(sheets: dict[str, pd.DataFrame], base: str) -> pd.DataFrame | None:
    """Fetch sheet by singular/plural variants (e.g., 'user' or 'users')."""
    s1 = sheets.get(base.lower())
    if s1 is not None:
        return s1
    s2 = sheets.get(base.lower() + "s")
    if s2 is not None:
        return s2
    return None


def find_local_excel() -> str | None:
    """Try to auto-locate a local Excel file."""
    candidates = [
        os.path.join(os.getcwd(), "Tourism Dataset.xlsx"),
        os.path.join(os.path.dirname(__file__), "Tourism Dataset.xlsx") if "__file__" in globals() else "",
        r"C:\Users\HP\Tourism\Tourism Dataset.xlsx",
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return None


# ------------------------- Data preparation (cached) ------------------------- #
@st.cache_data(show_spinner=True)
def prepare_data_from_excel(file) -> pd.DataFrame:
    """Load, normalize, canonicalize, and merge all sheets into one dataframe."""
    sheets = load_excel_dict(file)

    # 1) Normalize every sheet’s column headers
    sheets = {name: normalize_df(df) for name, df in sheets.items()}

    # 2) Pull sheets with singular/plural fallbacks
    txn   = normalize_df(get_sheet(sheets, "transaction"))
    user  = normalize_df(get_sheet(sheets, "user"))
    city  = normalize_df(get_sheet(sheets, "city"))
    typ   = normalize_df(get_sheet(sheets, "type"))
    mode  = normalize_df(get_sheet(sheets, "visitmode")) or normalize_df(get_sheet(sheets, "mode"))
    cont  = normalize_df(get_sheet(sheets, "continent"))
    cntry = normalize_df(get_sheet(sheets, "country"))
    regn  = normalize_df(get_sheet(sheets, "region"))
    item  = normalize_df(get_sheet(sheets, "item"))

    if txn is None:
        raise ValueError("Transaction sheet is missing — cannot proceed.")

    # 3) Canonicalize likely column names (conservative aliases)
    # Transaction
    txn = rename_with_aliases(txn, {
        "transactionid": ["transaction_id", "txn_id", "id"],
        "userid": ["user_id", "user"],
        "attractionid": ["attraction_id", "itemid", "item_id", "item"],
        "cityid": ["city_id"],
        "countryid": ["country_id", "countrycode", "country_code"],
        "regionid": ["region_id"],
        "continentid": ["continent_id"],
        "typeid": ["type_id"],
        # many files store code as "visitmode" but it is actually the id
        "visitmodeid": ["modeid", "mode_id", "visitmode_id", "visitmode"],
        "rating": ["ratings", "score"],
        "visityear": ["year"],
        "visitmonth": ["month"],
    })

    # User
    user = rename_with_aliases(user, {
        "userid": ["user_id", "user"],
        "continentid": ["continent_id"],
        "regionid": ["region_id"],
        "countryid": ["country_id", "countrycode", "country_code"],
        "cityid": ["city_id"],
    })

    # City
    city = rename_with_aliases(city, {
        "cityid": ["city_id"],
        "city": ["city_name"],
        "countryid": ["country_id", "countrycode", "country_code"],
    })

    # Type
    typ = rename_with_aliases(typ, {
        "typeid": ["type_id"],
        "type": ["typename", "category"],
    })

    # Mode / VisitMode
    mode = rename_with_aliases(mode, {
        "visitmodeid": ["modeid", "mode_id"],
        "visitmode": ["mode", "name"],
    })

    # Continent
    cont = rename_with_aliases(cont, {
        "continentid": ["continent_id"],
        "continent": ["continentname", "name"],
    })

    # Country
    cntry = rename_with_aliases(cntry, {
        "countryid": ["country_id", "countrycode", "country_code"],
        "country": ["countryname", "name"],
        "regionid": ["region_id"],
    })

    # Region
    regn = rename_with_aliases(regn, {
        "regionid": ["region_id"],
        "region": ["regionname", "name"],
        "continentid": ["continent_id"],
    })

    # Item / Attraction
    item = rename_with_aliases(item, {
        "attractionid": ["attraction_id", "itemid", "item_id"],
        "attraction": ["name", "item", "title"],
        "typeid": ["type_id"],
        "cityid": ["city_id"],
        "countryid": ["country_id", "countrycode", "country_code"],
    })

    # 4) Merge chain (only if key is present on both sides)
    df = txn.copy()
    df = safe_merge(df, user,  "userid")
    df = safe_merge(df, city,  "cityid")
    df = safe_merge(df, cntry, "countryid")
    df = safe_merge(df, regn,  "regionid")
    df = safe_merge(df, cont,  "continentid")
    df = safe_merge(df, typ,   "typeid")
    df = safe_merge(df, mode,  "visitmodeid")
    df = safe_merge(df, item,  "attractionid")

    # 5) Light cleaning
    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    # provide a single label for visit mode if available
    if "visitmode" not in df.columns and "visitmodeid" in df.columns:
        df["visitmode"] = df["visitmodeid"].astype(str)

    return df


# ------------------------------- EDA ------------------------------- #
def eda_section(df: pd.DataFrame):
    st.subheader("📊 Exploratory Data Analysis")

    c1, c2 = st.columns(2)

    with c1:
        if "rating" in df.columns:
            st.write("Ratings distribution")
            fig, ax = plt.subplots()
            sns.histplot(df["rating"].dropna(), bins=10, kde=True, ax=ax)
            st.pyplot(fig)

        if "attractionid" in df.columns:
            st.write("Top 10 most-rated attractions")
            top = df["attractionid"].value_counts().head(10)
            fig, ax = plt.subplots()
            top.plot(kind="bar", ax=ax)
            ax.set_xlabel("AttractionId")
            ax.set_ylabel("Count")
            st.pyplot(fig)

    with c2:
        if "visitmode" in df.columns:
            st.write("Visit mode distribution")
            fig, ax = plt.subplots()
            df["visitmode"].astype(str).value_counts().plot(kind="bar", ax=ax)
            st.pyplot(fig)

        # Heatmap
        num = df.select_dtypes(include=[np.number])
        if num.shape[1] >= 2:
            st.write("Correlation heatmap")
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(num.corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)


# -------------------------- Models (ML) -------------------------- #
def regression_section(df: pd.DataFrame):
    st.subheader("🎯 Regression: Predict Rating")
    if "rating" not in df.columns:
        st.warning("No 'rating' column available.")
        return

    data = df.dropna(subset=["rating"]).copy()

    # Encode categorical features
    le = LabelEncoder()
    for col in data.select_dtypes(include=["object"]).columns:
        data[col] = le.fit_transform(data[col].astype(str))

    X = data.drop(columns=["rating"])
    y = data["rating"]

    if X.empty:
        st.warning("Not enough features to train.")
        return

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(random_state=42)
    model.fit(Xtr, ytr)
    pred = model.predict(Xte)

    # ✅ FIX: compute RMSE manually
    mse = mean_squared_error(yte, pred)
    rmse = float(np.sqrt(mse))

    st.write("MSE:", float(mse))
    st.write("RMSE:", rmse)
    st.write("R²:", float(r2_score(yte, pred)))



def classification_section(df: pd.DataFrame):
    st.subheader("🧭 Classification: Predict Visit Mode")
    target = "visitmode" if "visitmode" in df.columns else ("visitmodeid" if "visitmodeid" in df.columns else None)
    if target is None:
        st.warning("No visit mode column available.")
        return
    data = df.dropna(subset=[target]).copy()
    le = LabelEncoder()
    data[target] = le.fit_transform(data[target].astype(str))
    for col in data.select_dtypes(include=["object"]).columns:
        if col != target:
            data[col] = le.fit_transform(data[col].astype(str))
    X = data.drop(columns=[target])
    y = data[target]
    if X.empty:
        st.warning("Not enough features to train.")
        return
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(random_state=42)
    model.fit(Xtr, ytr)
    pred = model.predict(Xte)
    st.write("Accuracy:", float(accuracy_score(yte, pred)))
    st.write("F1 (weighted):", float(f1_score(yte, pred, average="weighted")))


def recommendation_section(df: pd.DataFrame):
    st.subheader("💡 Recommendation Engine")
    needed = {"userid", "attractionid", "rating"}
    if not needed.issubset(df.columns):
        st.warning("Need columns: 'UserId', 'AttractionId', 'Rating' to recommend.")
        return

    df_rec = df[["userid", "attractionid", "rating"]].dropna().copy()
    if df_rec.empty:
        st.warning("No user-item-rating rows found.")
        return

    # convert ids to strings (Surprise works with strings too)
    df_rec["userid"] = df_rec["userid"].astype(str)
    df_rec["attractionid"] = df_rec["attractionid"].astype(str)

    if SURPRISE_OK:
        try:
            reader = Reader(rating_scale=(float(df_rec["rating"].min()), float(df_rec["rating"].max())))
            data = Dataset.load_from_df(df_rec, reader)
            trainset, _ = surprise_split(data, test_size=0.2, random_state=42)
            algo = SVD(random_state=42)
            algo.fit(trainset)

            user_choices = sorted(df_rec["userid"].unique().tolist())
            user_id = st.selectbox("Select a User ID", user_choices)
            # predict for items the user hasn't rated
            rated_items = set(df_rec.loc[df_rec["userid"] == user_id, "attractionid"])
            all_items = set(df_rec["attractionid"].unique().tolist())
            candidates = list(all_items - rated_items) or list(all_items)
            preds = [(iid, algo.predict(user_id, iid).est) for iid in candidates]
            topk = sorted(preds, key=lambda x: x[1], reverse=True)[:5]
            st.write("Top 5 recommendations (item, estimated rating):")
            st.write(topk)
        except Exception as e:
            st.error(f"SVD failed; falling back to popularity. Reason: {e}")
            SURPRISE_FALLBACK = True
    else:
        SURPRISE_FALLBACK = True

    if not SURPRISE_OK or 'SURPRISE_FALLBACK' in locals():
        top_items = (
            df_rec.groupby("attractionid")["rating"]
            .mean()
            .sort_values(ascending=False)
            .head(5)
        )
        st.write("Top attractions by average rating:")
        st.write(top_items)


# ------------------------------- UI / App ------------------------------- #
def main():
    st.title("🌍 Tourism Experience Analytics — Final App")

    # Data source
    st.sidebar.header("Data Source")
    use_local = st.sidebar.checkbox("Auto-load local 'Tourism Dataset.xlsx' (if found)", value=True)
    uploaded = st.sidebar.file_uploader("…or upload an Excel file", type=["xlsx"])

    df = None
    sheets_debug = None

    if uploaded is not None:
        sheets_debug = load_excel_dict(uploaded)
        df = prepare_data_from_excel(uploaded)
    elif use_local:
        local_path = find_local_excel()
        if local_path:
            st.sidebar.success(f"Loaded: {local_path}")
            sheets_debug = load_excel_dict(local_path)
            df = prepare_data_from_excel(local_path)
        else:
            st.sidebar.warning("No local Excel found. Please upload your file.")

    if sheets_debug is not None:
        st.sidebar.write("Sheets detected:", list(sheets_debug.keys()))

    if df is None:
        st.info("Upload or auto-load your Excel to begin.")
        return

    # Preview
    st.write("### Data preview")
    st.dataframe(df.head())

    # Task selector
    task = st.sidebar.radio("Choose a section", ["EDA", "Regression", "Classification", "Recommendation"])

    if task == "EDA":
        eda_section(df)
    elif task == "Regression":
        regression_section(df)
    elif task == "Classification":
        classification_section(df)
    elif task == "Recommendation":
        recommendation_section(df)


if __name__ == "__main__":
    main()
