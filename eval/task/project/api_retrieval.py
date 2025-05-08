import urllib.request
import json

API_RETRIEVAL_PORT = None

if __name__ == "__main__":
    with urllib.request.urlopen(f'http://localhost:{API_RETRIEVAL_PORT}/') as response:
        data = response.read()  # read raw bytes
        json_data = json.loads(data.decode())  # decode bytes and parse JSON
        print(json_data)
