import requests

# 1. Define the API endpoint (a public URL that returns fake job/user data for testing)
url = "https://jsonplaceholder.typicode.com/posts/1"

# 2. Make a request to the web page
response = requests.get(url)

# 3. Print the result status code (200 means success!)
print("Status Code:", response.status_code)
print("Data Received:", response.json())