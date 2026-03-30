
import requests

url = "https://127.0.0.1:8089/expand"
data = {"prompt":"talk"}
response = requests.post(url, verify=False, json=data)
print(response.json())