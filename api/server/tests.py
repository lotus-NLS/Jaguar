import time
import requests
from api.server.server import LotusServerIO


test_server = LotusServerIO()
test_server.start()


def test_create_item():
    url = "http://127.0.0.1:8000/item/"
    data = {"name": "Test Item", "description": "This is a test item."}
    response = requests.post(url, json=data)
    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    time.sleep(1)
    test_create_item()
    while True:
        time.sleep(1)
