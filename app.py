import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Tech Job Market Analyzer", layout="wide")
st.title("📊 Live Tech Job Market Analyzer")
st.markdown("Visualizing real-time skill demand across live developer job postings.")


try:
    df = pd.read_csv("skill_demand.csv")

   
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Skills Tracked", value=len(df))
    with col2:
        st.metric(label="Top Demanded Skill", value=df.iloc[0]['Skill'])
    with col3:
        st.metric(label="Top Skill Coverage", value=f"{df.iloc[0]['Demand_Percentage']}%")

    st.markdown("---")

   
    st.subheader("🔥 Skill Demand Frequency")
    
    fig = px.bar(
        df,
        x='Skill',
        y='Mentions',
        text='Demand_Percentage',
        labels={'Mentions': 'Number of Job Postings', 'Skill': 'Technology / Skill'},
        color='Mentions',
        color_continuous_scale='Viridis'
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    
    st.subheader("📋 Raw Skill Demand Data")
    st.dataframe(df, use_container_width=True)

except FileNotFoundError:
    st.error("⚠️ `skill_demand.csv` not found! Please run `python main.py` first to generate data.")