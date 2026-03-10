import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("--- Testing Unauthorized Access ---")
res = requests.post(f"{BASE_URL}/api/analyze", json={
    "code": "print('hello')",
    "analysis_type": "Bug Detection",
    "language": "Python"
})
print("Blocked Access Status:", res.status_code)

print("\n--- Testing Registration ---")
import random
user = f"testuser_{random.randint(1000,9999)}"
password = "supersecretpassword123!"

res = requests.post(f"{BASE_URL}/api/register", json={
    "username": user,
    "password": password
})
print("Register Status:", res.status_code, res.json())

print("\n--- Testing Login ---")
res = requests.post(f"{BASE_URL}/api/login", data={
    "username": user,
    "password": password
})
print("Login Status:", res.status_code)
token_data = res.json()
token = token_data.get("access_token")

print("\n--- Testing Authorized Access ---")
if token:
    res = requests.post(f"{BASE_URL}/api/analyze", json={
        "code": "def no_colon()\n  pass",
        "analysis_type": "Bug Detection",
        "language": "Python"
    }, headers={"Authorization": f"Bearer {token}"})
    print("Authorized Access Status:", res.status_code)
    # Don't print the whole JSON payload to save space since Gemini takes a few seconds
    print("Has Result Key:", "result" in res.json())
else:
    print("Failed to get token!")
