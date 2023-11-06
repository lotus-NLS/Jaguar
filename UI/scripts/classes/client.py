from browser import ajax


class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.base_url = f"http://{ip}:{port}"

    def get(self, endpoint, callback):
        self._request(endpoint, 'GET', callback)

    def post(self, endpoint, data, callback):
        self._request(endpoint, 'POST', callback, data=data)

    def put(self, endpoint, data, callback):
        self._request(endpoint, 'PUT', callback, data=data)

    def delete(self, endpoint, callback):
        self._request(endpoint, 'DELETE', callback)

    def _request(self, endpoint, method, callback, data=None):
        url = f"{self.base_url}/{endpoint}"
        req = ajax.Ajax()
        req.open(method, url, True)
        req.bind('complete', callback)

        if data:
            req.set_header('content-type', 'application/json')
            req.send(data)
        else:
            req.send()