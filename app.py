import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Tech Job Market & Skill Intelligence Engine", layout="wide")

st.title("📊 Tech Job Market & Skill Intelligence Engine")
st.write("Explore real-time technical skill demand, top hiring companies, and open job listings.")

def get_db_connection():
    return sqlite3.connect('jobs_data.db')

try:
    conn = get_db_connection()

    # --- 1. OVERALL DATA QUERIES ---
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

    total_jobs = pd.read_sql_query("SELECT COUNT(*) as count FROM jobs", conn).iloc[0]['count']
    total_skills = len(skills_df)
    
    # Capitalize skill names for presentation
    skills_df['skill_display'] = skills_df['skill'].str.title()
    skills_df.loc[skills_df['skill_display'] == 'Sql', 'skill_display'] = 'SQL'
    skills_df.loc[skills_df['skill_display'] == 'Aws', 'skill_display'] = 'AWS'

    # --- TOP KPIS ---
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.metric("Total Active Job Listings", total_jobs)
    col_kpi2.metric("Tracked Skills", total_skills)
    col_kpi3.metric("Top Hiring Company", companies_df.iloc[0]['company_name'] if not companies_df.empty else "N/A")

    st.divider()

    # --- CHARTS SECTION (CLEANED UP & HORIZONTAL) ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("💡 Technical Skill Demand")
        fig_skills = px.bar(
            skills_df, 
            x='job_count', 
            y='skill_display', 
            orientation='h',
            labels={'skill_display': 'Skill', 'job_count': 'Job Postings'},
            color='job_count',
            color_continuous_scale='Blues'
        )
        fig_skills.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
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
        fig_comp.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_comp, use_container_width=True)

    st.divider()

    # --- DRILL-DOWN SECTION ---
    st.subheader("🔍 Skill & Company Drill-Down")
    
    selected_skill = st.selectbox(
        "Select a Tech Skill to Inspect:", 
        options=["All Skills"] + list(skills_df['skill'].unique())
    )

    if selected_skill == "All Skills":
        query = "SELECT DISTINCT title, company_name, url, publication_date FROM jobs"
        detailed_jobs = pd.read_sql_query(query, conn)
    else:
        query = '''
            SELECT j.title, j.company_name, j.url, j.publication_date 
            FROM jobs j
            JOIN job_skills js ON j.job_id = js.job_id
            WHERE js.skill = ?
        '''
        detailed_jobs = pd.read_sql_query(query, conn, params=(selected_skill,))

    # Format ISO date strings to clean YYYY-MM-DD format
    if not detailed_jobs.empty and 'publication_date' in detailed_jobs.columns:
        detailed_jobs['publication_date'] = pd.to_datetime(detailed_jobs['publication_date']).dt.strftime('%Y-%m-%d')

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