import requests


class LotusAPI_Communicator:
    def send_request(self, endpoint, params=None, data=None):
        base_url = "http://127.0.0.1:8000"  # Replace with your FastAPI app's URL

        response = requests.get(f"{base_url}/{endpoint}/", params=params) if data is None else requests.post(
            f"{base_url}/{endpoint}/", json=data)
        return response.json()


