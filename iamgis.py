import requests

url = "https://app.iamgis.com/connect/token"
data = {
    'client_id': 'posm',
    'client_secret': 'DeFS&KA#7@GwR&6m',
    'grant_type': 'client_credentials'
}
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.post(url, data=data, headers=headers)

if response.status_code == 200:
    print("Connection successful!")
    print("Response:", response.text)
else:
    print("Failed to connect. Status code:", response.status_code)
    print("Response:", response.text)
