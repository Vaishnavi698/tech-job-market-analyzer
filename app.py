import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Live Tech Job-Market Analyzer", layout="wide")

st.title("📊 Live Tech Job-Market Analyzer")
st.write("Real-time technical skill demand fetched from live API and queried from a SQLite database backend.")

# Connect to SQLite Database and Read Data
def load_data():
    conn = sqlite3.connect('jobs_data.db')
    df = pd.read_sql_query("SELECT skill, count FROM skill_demand ORDER BY count DESC", conn)
    conn.close()
    return df

try:
    df = load_data()

    if not df.empty:
        # Top Skills Bar Chart
        fig = px.bar(
            df, 
            x='skill', 
            y='count', 
            title="Most Demanded Technical Skills",
            labels={'skill': 'Technical Skill', 'count': 'Number of Job Postings'},
            color='count',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Raw Database Table View
        st.subheader("💾 Database Table View (`jobs_data.db`)")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Database is empty. Please run `python main.py` first.")

except Exception as e:
    st.error(f"Error loading database: {e}")