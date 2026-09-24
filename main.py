import sqlite3
import re
import requests

# 1. API Configuration - Ingesting a larger limit (200 jobs)
API_URL = "https://remotive.com/api/remote-jobs?limit=200"

# Target Technical Skills to Track
TARGET_SKILLS = [
    "python", "java", "javascript", "typescript", "react", "node", 
    "sql", "aws", "azure", "docker", "kubernetes", "spark", "pytorch"
]

# Keywords to filter out non-tech jobs (e.g. Writers, Assistants, Sales)
TECH_KEYWORDS = [
    "developer", "engineer", "data", "software", "architect", 
    "analyst", "qa", "devops", "tech", "frontend", "backend", "full-stack", "ai"
]

def init_db():
    """Create relational database schema with foreign keys."""
    conn = sqlite3.connect('jobs_data.db')
    cursor = conn.cursor()
    
    # Enable Foreign Key Constraints
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Table 1: Primary Job Information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            company_name TEXT NOT NULL,
            category TEXT,
            url TEXT,
            publication_date TEXT
        )
    ''')
    
    # Table 2: Relational Mapping (Skill to Job ID)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            skill TEXT NOT NULL,
            FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def fetch_and_store_jobs():
    """Fetch live jobs from API and populate relational SQLite database."""
    print("Fetching live tech jobs from Remotive API...")
    response = requests.get(API_URL)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch data. Status Code: {response.status_code}")
        return

    jobs_data = response.json().get('jobs', [])
    print(f"Fetched {len(jobs_data)} raw job postings from API...")

    conn = sqlite3.connect('jobs_data.db')
    cursor = conn.cursor()

    # Clear previous snapshot data for fresh load
    cursor.execute("DELETE FROM job_skills")
    cursor.execute("DELETE FROM jobs")

    inserted_jobs = 0
    skill_mappings = 0

    for job in jobs_data:
        job_id = job.get('id')
        title = job.get('title', 'Unknown Title')
        
        # KEYWORD FILTER (Code Improvement): Skip non-tech roles
        if not any(keyword in title.lower() for keyword in TECH_KEYWORDS):
            continue

        company = job.get('company_name', 'Unknown Company')
        category = job.get('category', 'Software Development')
        url = job.get('url', '#')
        pub_date = job.get('publication_date', '')
        description = job.get('description', '').lower()

        # Insert Job Metadata into 'jobs' table
        cursor.execute('''
            INSERT OR REPLACE INTO jobs (job_id, title, company_name, category, url, publication_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (job_id, title, company, category, url, pub_date))
        inserted_jobs += 1

        # Extract skills and map to 'job_skills' table
        for skill in TARGET_SKILLS:
            # Match skill as a discrete word using regex boundary \b
            if re.search(rf'\b{re.escape(skill)}\b', description):
                cursor.execute('''
                    INSERT INTO job_skills (job_id, skill)
                    VALUES (?, ?)
                ''', (job_id, skill))
                skill_mappings += 1

    conn.commit()
    conn.close()
    print(f"✅ Stored {inserted_jobs} tech jobs and {skill_mappings} skill matches in 'jobs_data.db'!")

if __name__ == "__main__":
    init_db()
    fetch_and_store_jobs()