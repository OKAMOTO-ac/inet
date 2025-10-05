import requests

response = requests.get("https://ipinfo.io/json")
data = response.json()
loc = data['loc'].split(',')
lat, lon = float(loc[0]), float(loc[1])
print(f"IP: {data['ip']}")
print(f"City: {data['city']}")
print(f"Region: {data['region']}")
print(f"Country: {data['country']}")
print(f"Location: {lat}, {lon}")  # '緯度,経度'形式