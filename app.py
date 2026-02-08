import streamlit as st
import pandas as pd
import os

# ===================== CONFIGURATION =====================

HQ_PASSWORD = "benchmark@hq"   # change this to something only you know

COMPANY_OPTIONS = [
    "Reliance Retail",
    "Croma",
    "Vijay Sales",
    "Bajaj Electronics",
    "Other"
]

MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

YEARS = [2024, 2025, 2026]

DATA_FILE = "cluster_inputs.csv"

# ===================== APP SETUP =====================

st.set_page_config(
    page_title="Retail Benchmark Data Collection",
    layout="wide"
)

st.title("Cluster Data Entry")

# ===================== LOAD DATA =====================

if os.path.exists(DATA_FILE):
    data = pd.read_csv(DATA_FILE)
else:
    data = pd.DataFrame(columns=[
        "Year",
        "Month",
        "Cluster",
        "Company",
        "Stores",
        "Area_mn_sqft",
        "Revenue_per_store",
        "Margin_per_store",
        "Net_additions",
        "LFL_growth",
        "Bills_per_store",
        "ABV"
    ])

# ===================== INPUT FORM =====================

with st.form("cluster_form"):
    st.subheader("Enter Cluster Data")

    col1, col2 = st.columns(2)

    with col1:
        year = st.selectbox("Year", YEARS)
        month = st.selectbox("Month", MONTHS)
        cluster = st.text_input("Cluster name")
        company = st.selectbox("Company", COMPANY_OPTIONS)
        stores = st.number_input("Total number of stores", min_value=0, step=1)
        area = st.number_input("Retail area (mn sq. ft.)", min_value=0.0)
        net_add = st.number_input("Net store additions", step=1)

    with col2:
        rev_store = st.number_input("Revenue per store (Rs. crore)", min_value=0.0)
        margin_store = st.number_input("Margin per store (Rs. crore)", min_value=0.0)
        lfl = st.number_input(
            "LFL growth in revenue (%)",
            min_value=-100.0,
            max_value=100.0
        )
        bills = st.number_input("# of bills per store", min_value=0, step=1)
        abv = st.number_input("Average bill value (Rs.)", min_value=0.0)

    submitted = st.form_submit_button("Submit")

# ===================== SAVE DATA =====================

if submitted:
    new_row = pd.DataFrame([{
        "Year": year,
        "Month": month,
        "Cluster": cluster,
        "Company": company,
        "Stores": stores,
        "Area_mn_sqft": area,
        "Revenue_per_store": rev_store,
        "Margin_per_store": margin_store,
        "Net_additions": net_add,
        "LFL_growth": lfl,
        "Bills_per_store": bills,
        "ABV": abv
    }])

    data = pd.concat([data, new_row], ignore_index=True)
    data.to_csv(DATA_FILE, index=False)

    st.success("Data submitted successfully")

# ===================== HQ BENCHMARK VIEW =====================

st.divider()
st.subheader("HQ Benchmark View")

hq_access = st.text_input("HQ Access Password", type="password")

if hq_access == HQ_PASSWORD and not data.empty:

    summary_rows = []

    grouped = data.groupby(["Year", "Month", "Company"])

    for (year, month, company), d in grouped:

        total_stores = d["Stores"].sum()
        total_area = d["Area_mn_sqft"].sum()
        total_revenue = (d["Revenue_per_store"] * d["Stores"]).sum()

        summary_rows.append({
            "Year": year,
            "Month": month,
            "Company": company,
            "Total number of stores": total_stores,
            "Retail area (mn sq. ft.)": total_area,
            "Revenue per store (Rs. crore)": (
                total_revenue / total_stores if total_stores else 0
            ),
            "Margin per store (Rs. crore)": (
                (d["Margin_per_store"] * d["Stores"]).sum() / total_stores
                if total_stores else 0
            ),
            "Revenue per sq. ft. (Rs.)": (
                (total_revenue * 1e7) / (total_area * 1e6)
                if total_area else 0
            ),
            "Margin per sq. ft. (Rs.)": (
                ((d["Margin_per_store"] * d["Stores"]).sum() * 1e7)
                / (total_area * 1e6)
                if total_area else 0
            ),
            "Net store additions": d["Net_additions"].sum(),
            "LFL growth in revenue (%)": (
                (d["LFL_growth"] * d["Revenue_per_store"] * d["Stores"]).sum()
                / total_revenue
                if total_revenue else 0
            ),
            "# of bills per store": (
                (d["Bills_per_store"] * d["Stores"]).sum() / total_stores
                if total_stores else 0
            ),
            "Average bill value (Rs.)": (
                (d["ABV"] * d["Stores"]).sum() / total_stores
                if total_stores else 0
            )
        })

    summary_df = pd.DataFrame(summary_rows)
    st.dataframe(summary_df, use_container_width=True)

elif hq_access:
    st.error("Invalid HQ password")
