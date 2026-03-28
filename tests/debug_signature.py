import hmac
import hashlib
import time
import os
from dotenv import load_dotenv

load_dotenv('config/.env')

API_KEY = os.getenv('ROOSTOO_API_KEY')
SECRET_KEY = os.getenv('ROOSTOO_API_SECRET')

print("=" * 60)
print("Roostoo API Signature Debug")
print("=" * 60)
print(f"API Key: {API_KEY[:10]}...{API_KEY[-10:]}")
print(f"Secret Key: {SECRET_KEY[:10]}...{SECRET_KEY[-10:]}")
print()

# Test 1: Generate timestamp
timestamp = str(int(time.time() * 1000))
print(f"Timestamp: {timestamp}")
print()

# Test 2: Create payload for balance endpoint (empty params + timestamp)
payload = {'timestamp': timestamp}
print(f"Payload: {payload}")
print()

# Test 3: Sort keys and create param string
sorted_keys = sorted(payload.keys())
print(f"Sorted keys: {sorted_keys}")
print()

total_params = "&".join(f"{k}={payload[k]}" for k in sorted_keys)
print(f"Total params string: {total_params}")
print()

# Test 4: Generate signature
signature = hmac.new(
    SECRET_KEY.encode('utf-8'),
    total_params.encode('utf-8'),
    hashlib.sha256
).hexdigest()
print(f"Signature: {signature}")
print()

# Test 5: Show what headers should look like
print("Headers that will be sent:")
print(f"  RST-API-KEY: {API_KEY}")
print(f"  MSG-SIGNATURE: {signature}")
print()

# Test 6: Make actual request with debug output
import requests

url = "https://mock-api.roostoo.com/v3/balance"
headers = {
    'RST-API-KEY': API_KEY,
    'MSG-SIGNATURE': signature
}

print(f"Request URL: {url}?timestamp={timestamp}")
print()

try:
    res = requests.get(url, headers=headers, params={'timestamp': timestamp})
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Error: {e}")

print("=" * 60)
