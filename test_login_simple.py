import requests
import json

url = "http://192.168.130.10:9001/api/v1/auth/login"
data = {
    "email": "admin@pcm.local",
    "password": "Admin@123456"
}

print(f"Testing login at: {url}")
print(f"Credentials: {data['email']} / ***")

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
