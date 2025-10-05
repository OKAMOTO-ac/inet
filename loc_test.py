import requests

response = requests.get("https://ipinfo.io/json")
data = response.json()
print(f"IP: {data['ip']}")
print(f"City: {data['city']}")
print(f"Region: {data['region']}")
print(f"Country: {data['country']}")
print(f"Location: {data['loc']}")  # '緯度,経度'形式