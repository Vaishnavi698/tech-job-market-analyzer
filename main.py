import requests

# Remotive provides a free API for live tech jobs with no key required!
url = "https://remotive.com/api/remote-jobs"

# Filter parameters: search specifically for software/tech roles
params = {
    'category': 'software-dev',
    'limit': 5
}

print("Fetching live job data from Remotive API...\n")
response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    jobs = data.get('jobs', [])
    
    print(f"✅ Success! Fetched {len(jobs)} live jobs:\n")
    
    for i, job in enumerate(jobs, 1):
        title = job.get('title')
        company = job.get('company_name')
        category = job.get('category')
        tags = ", ".join(job.get('tags', [])) # Extract skills/tags listed
        
        print(f"{i}. Job Title: {title}")
        print(f"   Company  : {company}")
        print(f"   Category : {category}")
        print(f"   Skills/Tags: {tags}")
        print("-" * 50)
else:
    print(f"❌ Failed to fetch data. Status Code: {response.status_code}")