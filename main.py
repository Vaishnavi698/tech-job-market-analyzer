import requests
from collections import Counter


url = "https://remotive.com/api/remote-jobs"
params = {'category': 'software-dev', 'limit': 20}

print("Fetching 20 live jobs to analyze tech skills...\n")
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
                
    
    print("=" * 40)
    print("      LIVE TECH SKILL DEMAND ANALYSIS    ")
    print("=" * 40)
    for skill, count in skill_counts.most_common():
        percentage = (count / len(jobs)) * 100
        print(f"🔹 {skill.upper():<12} : Mentioned in {count}/{len(jobs)} jobs ({percentage:.1f}%)")
    print("=" * 40)

else:
    print(f"Failed to fetch job data. Status Code: {response.status_code}")