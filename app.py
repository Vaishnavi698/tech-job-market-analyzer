import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Tech Job Market & Skill Intelligence", layout="wide")

st.title("📊 Tech Job Market & Skill Intelligence Engine")
st.write("Explore real-time technical skill demand, top hiring companies, and open job listings.")

# Database Connection Helper
def get_db_connection():
    conn = sqlite3.connect('jobs_data.db')
    return conn

try:
    conn = get_db_connection()

    # --- 1. OVERALL SKILL DEMAND ANALYSIS ---
    skills_df = pd.read_sql_query('''
        SELECT skill, COUNT(job_id) as job_count 
        FROM job_skills 
        GROUP BY skill 
        ORDER BY job_count DESC
    ''', conn)

    companies_df = pd.read_sql_query('''
        SELECT company_name, COUNT(job_id) as open_positions 
        FROM jobs 
        GROUP BY company_name 
        ORDER BY open_positions DESC 
        LIMIT 10
    ''', conn)

    # --- TOP KPIS ---
    total_jobs = pd.read_sql_query("SELECT COUNT(*) as count FROM jobs", conn).iloc[0]['count']
    total_skills = len(skills_df)
    
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.metric("Total Active Job Listings", total_jobs)
    col_kpi2.metric("Tracked Skills", total_skills)
    col_kpi3.metric("Top Hiring Company", companies_df.iloc[0]['company_name'] if not companies_df.empty else "N/A")

    st.divider()

    # --- CHARTS SECTION ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("💡 Technical Skill Demand")
        fig_skills = px.bar(
            skills_df, 
            x='skill', 
            y='job_count', 
            color='job_count',
            labels={'skill': 'Skill', 'job_count': 'Job Postings'},
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_skills, use_container_width=True)

    with col_right:
        st.subheader("🏢 Top Hiring Companies")
        fig_comp = px.bar(
            companies_df, 
            x='open_positions', 
            y='company_name', 
            orientation='h',
            labels={'company_name': 'Company', 'open_positions': 'Open Roles'},
            color='open_positions',
            color_continuous_scale='Blues'
        )
        fig_comp.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_comp, use_container_width=True)

    st.divider()

    # --- 2. GRANULAR DRILL-DOWN SECTION ---
    st.subheader("🔍 Skill & Company Drill-Down")
    st.write("Filter to see specific companies hiring for your target skill with direct application links.")

    selected_skill = st.selectbox(
        "Select a Tech Skill to Inspect:", 
        options=["All Skills"] + list(skills_df['skill'].unique())
    )

    # SQL Relational JOIN Query to Fetch Job Details for Selected Skill
    if selected_skill == "All Skills":
        query = '''
            SELECT DISTINCT j.title, j.company_name, j.url, j.publication_date 
            FROM jobs j
        '''
        detailed_jobs = pd.read_sql_query(query, conn)
    else:
        query = '''
            SELECT j.title, j.company_name, j.url, j.publication_date 
            FROM jobs j
            JOIN job_skills js ON j.job_id = js.job_id
            WHERE js.skill = ?
        '''
        detailed_jobs = pd.read_sql_query(query, conn, params=(selected_skill,))

    # Format Table Display
    st.write(f"Showing **{len(detailed_jobs)}** open positions requiring **'{selected_skill}'**:")
    
    st.dataframe(
        detailed_jobs, 
        column_config={
            "title": "Job Title",
            "company_name": "Company Name",
            "url": st.column_config.LinkColumn("Application Link", display_text="Apply Now 🔗"),
            "publication_date": "Date Posted"
        },
        use_container_width=True
    )

    conn.close()

except Exception as e:
    st.error(f"Error reading from database: {e}")