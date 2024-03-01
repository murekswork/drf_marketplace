import requests

endpoint = "http://localhost:8000/api/auth/"
auth_response = requests.post(endpoint, json={'username': 'user', 'password': '0xABAD1DEA'})
print(auth_response)

if auth_response.status_code == 200:
    token = auth_response.json()['token']
    headers = {
        "Authorization": f"Bearer {token}"
    }

data = {
    'title': 'Hello',
    'price': 999
}
endpoint = "http://localhost:8000/api/products/4/update"
get_response = requests.put(endpoint, json=data, headers=headers)

print(get_response.json())