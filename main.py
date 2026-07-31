import sqlite3
import requests
import pandas as pd
from collections import Counter
import re


conn = sqlite3.connect('jobs_data.db')
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS skill_demand (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill TEXT UNIQUE,
        count INTEGER
    )
''')
conn.commit()


print("Fetching live jobs from Remotive API...")
url = "https://remotive.com/api/remote-jobs?limit=50"
response = requests.get(url)
data = response.json()

jobs = data.get('jobs', [])


target_skills = ['python', 'sql', 'aws', 'docker', 'kubernetes', 'spark', 'react', 'java', 'c++', 'pandas']
skill_counts = Counter()


for job in jobs:
    description = job.get('description', '').lower()
    for skill in target_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', description):
            skill_counts[skill] += 1


for skill, count in skill_counts.items():
    cursor.execute('''
        INSERT INTO skill_demand (skill, count)
        VALUES (?, ?)
        ON CONFLICT(skill) DO UPDATE SET count=excluded.count
    ''', (skill, count))

conn.commit()
conn.close()
print("Data successfully saved to SQLite database ('jobs_data.db')!")