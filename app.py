import streamlit as st
import pandas as pd
import os

# ---------- App Config ----------
st.set_page_config(
    page_title="Retail Benchmark Data Collection",
    layout="wide"
)

st.title("Retail Benchmark – Cluster Manager Input")

DATA_FILE = "cluster_inputs.csv"

# ---------- Load Existing Data ----------
if os.path.exists(DATA_FILE):
    data = pd.read_csv(DATA_FILE)
else:
    data = pd.DataFrame(columns=[
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

# ---------- Input Form ----------
with st.form("cluster_form"):
    st.subheader("Cluster Data Entry")

    colA, colB = st.columns(2)

    with colA:
        cluster = st.text_input("Cluster name")
        company = st.selectbox(
            "Company",
            ["Reliance Retail", "Competitor 1", "Competitor 2"]
        )
        stores = st.number_input("Total number of stores", min_value=0, step=1)
        area = st.number_input("Retail area (mn sq. ft.)", min_value=0.0)
        net_add = st.number_input("Net store additions", step=1)

    with colB:
        rev_store = st.number_input("Revenue per store (Rs. crore)", min_value=0.0)
        margin_store = st.number_input("Margin per store (Rs. crore)", min_value=0.0)
        lfl = st.number_input("LFL growth in revenue (%)", min_value=-100.0, max_value=100.0)
        bills = st.number_input("# of bills per store", min_value=0, step=1)
        abv = st.number_input("Average bill value (Rs.)", min_value=0.0)

    submitted = st.form_submit_button("Submit")

# ---------- Save Data ----------
if submitted:
    new_row = pd.DataFrame([{
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

# ---------- Aggregated Summary ----------
st.divider()
st.subheader("Aggregated Benchmark View")

if not data.empty:
    summary_rows = []

    for company in data["Company"].unique():
        d = data[data["Company"] == company]

        total_stores = d["Stores"].sum()
        total_area = d["Area_mn_sqft"].sum()
        total_revenue = (d["Revenue_per_store"] * d["Stores"]).sum()

        summary_rows.append({
            "Company": company,
            "Total number of stores": total_stores,
            "Retail area (mn sq. ft.)": total_area,
            "Revenue per store (Rs. crore)": total_revenue / total_stores if total_stores else 0,
            "Margin per store (Rs. crore)": (
                (d["Margin_per_store"] * d["Stores"]).sum() / total_stores
                if total_stores else 0
            ),
            "Revenue per sq. ft. (Rs.)": (
                (total_revenue * 1e7) / (total_area * 1e6)
                if total_area else 0
            ),
            "Margin per sq. ft. (Rs.)": (
                ((d["Margin_per_store"] * d["Stores"]).sum() * 1e7) / (total_area * 1e6)
                if total_area else 0
            ),
            "Net store additions": d["Net_additions"].sum(),
            "LFL growth in revenue (%)": (
                (d["LFL_growth"] * d["Revenue_per_store"] * d["Stores"]).sum() / total_revenue
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

else:
    st.info("No data submitted yet.")
