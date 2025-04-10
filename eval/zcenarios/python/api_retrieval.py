import requests

response = requests.get('http://localhost:8002/')
print(response.json())  # This will print: {'message': 'Farfalle'}
