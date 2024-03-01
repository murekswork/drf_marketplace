import requests
from getpass import getpass

endpoint = 'http://localhost:8000/api/auth/'
username = input('Enter your username: ')
password = getpass()

auth_response = requests.post(endpoint, json={'username': username, 'password': password})
print(auth_response.json())

if auth_response.status_code == 200:
    token = auth_response.json()['token']
    headers = {
        "Authorization": f"Bearer {token}"
    }


    products_endpoint = "http://localhost:8000/api/products/"

    get_response = requests.get(products_endpoint, headers=headers)
    print(get_response.json())
