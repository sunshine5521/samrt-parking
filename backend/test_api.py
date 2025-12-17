import requests
import json

# 测试API的脚本
headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJyb2xlIjoidXNlciIsImV4cCI6MTczNDQxOTg3MX0.kC5_1y7eI9aC2f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b'
}

try:
    response = requests.get('http://127.0.0.1:5000/api/parking/records', headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
