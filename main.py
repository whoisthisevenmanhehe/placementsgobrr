import streamlit as st
import pandas as pd
import plotly.express as px
import time

st.set_page_config(page_title="Placements Dashboard (2023–25)", layout="wide")
st.title("🎓 M.Tech Placements Dashboard (Batch 2023–25)")

tab1, tab2 = st.tabs(["📍 College-wise Comparison", "🏢 IIT Kanpur Company-wise (2025)"])

with tab1:
    df = pd.read_csv("placements.csv")
    df.columns = df.columns.str.strip()
    df["Average Salary (LPA)"] = df["Average Salary (LPA)"].astype(str).str.extract(r"(\d+\.?\d*)").astype(float)
    df["Placement Percentage"] = df["Placement Percentage"].astype(float)

    def group(c): c = c.lower(); return (
        "IIT" if "iit" in c and "iiit" not in c else
        "NIT" if "nit" in c else
        "IIIT" if "iiit" in c else
        "Premier Institute" if any(x in c for x in ["iisc", "isi", "cmi"]) else
        "Others"
    )
    df["Group"] = df["College"].apply(group)
    df["Salary Band"] = df["Average Salary (LPA)"].apply(lambda x: "Above 20 LPA" if x > 20 else "Below 20 LPA")

    with st.sidebar:
        st.markdown("### Filters for College-wise Comparison")
        colgroup = st.multiselect("Group Filter", df["Group"].unique(), default=df["Group"].unique())
        salband = st.radio("Salary Filter", ["All", "Above 20 LPA", "Below 20 LPA"], index=0)

    fdf = df[df["Group"].isin(colgroup)]
    if salband != "All":
        fdf = fdf[fdf["Salary Band"] == salband]

    st.markdown("#### 📊 Summary Stats (Filtered)")
    group_summary = fdf.groupby("Group").agg({'Average Salary (LPA)':'mean','Placement Percentage':'mean'}).reset_index()
    st.dataframe(group_summary.style.format({'Average Salary (LPA)':'{:.2f} LPA','Placement Percentage':'{:.1f}%'}), use_container_width=True)


    if "celebrate_clicked" not in st.session_state:
        st.session_state.celebrate_clicked = False
        st.session_state.celebrate_time = 0

    if st.button("🎉 Celebrate Placements!"):
        st.session_state.celebrate_clicked = True
        st.session_state.celebrate_time = time.time()
        st.balloons()

    if st.session_state.celebrate_clicked:
        st.warning("You really thought this was gonna be all sunshine and rainbows? Maybe you're right")
        st.markdown("""
        <a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ" target="_blank">
            <button style="background-color:#f63366;color:white;border:none;padding:8px 16px;border-radius:8px;font-weight:bold;cursor:pointer;">Keep celebrating 🎉</button>
        </a>
        """, unsafe_allow_html=True)


    fig1 = px.bar(
        fdf.sort_values("Average Salary (LPA)", ascending=True),
        x="Average Salary (LPA)", y="College", color="Group", orientation="h",
        text="Average Salary (LPA)", title="Average Salary (LPA) by College"
    )
    fig1.update_layout(
        height=800,
        title_font_size=20,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        margin=dict(l=150, r=20, t=60, b=40),
    )
    fig1.update_traces(
        textposition="outside",
        texttemplate="%{text:.2f} LPA",
        marker_line_width=0.5,
        marker_line_color='black'
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### 📊 Placement % vs College")
    fig2 = px.bar(
        fdf.sort_values("Placement Percentage", ascending=True),
        x="Placement Percentage", y="College", color="Group", orientation="h",
        text="Placement Percentage", title="Placement Percentage by College"
    )
    fig2.update_layout(
        height=800,
        title_font_size=20,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        margin=dict(l=150, r=20, t=60, b=40),
    )
    fig2.update_traces(
        textposition="outside",
        texttemplate="%{text:.1f}%",
        marker_line_width=0.5,
        marker_line_color='black'
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### 🔬 Scatter: Salary vs Placement %")
    fig3 = px.scatter(fdf, x="Placement Percentage", y="Average Salary (LPA)", hover_name="College",
                     color="Group", size="Average Salary (LPA)", title="Scatter: Salary vs Placement %")
    fig3.update_layout(height=500)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### 📋 Raw Table")
    st.dataframe(fdf.reset_index(drop=True), use_container_width=True)

with tab2:
    st.markdown("### 📍 IIT Kanpur 2025 Placement Stats")

    the_df2 = pd.read_csv("iitk_2025.csv")
    df2 = the_df2.dropna(thresh=3)
    df2.columns = df2.columns.str.strip()
    df2 = df2[df2["Company"].notna()]
    df2["CTC(in L)"] = pd.to_numeric(df2["CTC(in L)"], errors="coerce")
    df2["1st year tc"] = pd.to_numeric(df2["1st year tc"], errors="coerce")
    df2["Students"] = pd.to_numeric(df2["Students"], errors="coerce")

    total_offers = 43 
    avg_ctc = round(df2["CTC(in L)"].mean(), 2)
    med_ctc = round(df2["CTC(in L)"].median(), 2)
    avg_tc = round(df2["1st year tc"].mean(skipna=True), 2)
    med_tc = round(df2["1st year tc"].median(skipna=True), 2)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Offers", total_offers)
    col2.metric("Avg CTC", f"{avg_ctc} L")
    col3.metric("Med CTC", f"{med_ctc} L")
    col4.metric("Avg TC (1st yr)", f"{avg_tc} L")
    col5.metric("Med TC (1st yr)", f"{med_tc} L")

    with st.sidebar:
        st.markdown("### Filters for IIT Kanpur")
        min_salary, max_salary = df2["CTC(in L)"].min(), df2["CTC(in L)"].max()
        salary_range = st.slider("CTC Range (in LPA)", float(min_salary), float(max_salary), (float(min_salary), float(max_salary)))

    df2_filtered = df2[df2["CTC(in L)"].between(*salary_range)]

    st.markdown("### 💰 CTC by Company (You've to get that bag one day)")
    fig4 = px.bar(
        df2_filtered.sort_values("CTC(in L)", ascending=False),
        x="Company", y="CTC(in L)", color="CTC(in L)",
        text="CTC(in L)", title="CTC by Company"
    )
    fig4.update_traces(textposition="outside")
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("### 💰 1st Year TC by Company")
    fig5 = px.bar(
        df2_filtered.sort_values("1st year tc", ascending=False),
        x="Company", y="1st year tc", color="1st year tc",
        text="1st year tc", title="First Year TC"
    )
    fig5.update_traces(textposition="outside")
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("### 👥 Student Count per Company")
    fig6 = px.bar(
        df2_filtered.sort_values("Students", ascending=False),
        x="Company", y="Students", color="Students",
        text="Students", title="No. of Students Placed"
    )
    fig6.update_traces(textposition="outside")
    st.plotly_chart(fig6, use_container_width=True)

    st.markdown("### Raw Offers Table")
    st.dataframe(df2_filtered.reset_index(drop=True), use_container_width=True)

st.markdown("""
---
#### ℹ️ Notes & Sources
- Source 1: [Reddit - College-wise Placements](https://www.reddit.com/r/GATEtard/comments/1lqpe6g/college_by_placement_courses_which_are_related_to/#lightbox)
- Source 2: [Reddit - IIT Kanpur CSE 2024–25 Placement](https://www.reddit.com/r/GATEtard/comments/1lozlzc/iit_kanpur_mtech_cse_202425_placementphase_1/)
- Have taken information from IIIT-Bangalore and IIIT-Hyderabad websites and modified a little based on new data.
""")