import requests
from collections import Counter
import pandas as pd


url = "https://remotive.com/api/remote-jobs"
params = {'category': 'software-dev', 'limit': 30}

print("Fetching live jobs from Remotive API...")
response = requests.get(url, params=params)

if response.status_code == 200:
    jobs = response.json().get('jobs', [])
    
    target_skills = ['python', 'sql', 'aws', 'docker', 'react', 'javascript', 'api', 'git', 'linux', 'kubernetes']
    skill_counts = Counter()
    
   
    for job in jobs:
        job_text = f"{job.get('title', '')} {' '.join(job.get('tags', []))}".lower()
        for skill in target_skills:
            if skill in job_text:
                skill_counts[skill] += 1

    
    data = []
    total_jobs = len(jobs)
    
    for skill, count in skill_counts.items():
        percentage = round((count / total_jobs) * 100, 2)
        data.append({
            'Skill': skill.upper(),
            'Mentions': count,
            'Demand_Percentage': percentage
        })
    
    
    df = pd.DataFrame(data)
    df = df.sort_values(by='Mentions', ascending=False)
   
    csv_filename = "skill_demand.csv"
    df.to_csv(csv_filename, index=False)
    
    print("\n✅ Analysis Complete! Here is your structured data sample:\n")
    print(df.head(10)) # Print top 10 rows
    print(f"\n📁 Data successfully saved to '{csv_filename}'")

else:
    print(f"Failed to fetch job data. Status Code: {response.status_code}")