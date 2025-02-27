from engine.l0_main.dev_monitor import DevMonitor
from holytools.network import Endpoint


class QuittableMonitor(DevMonitor):
    def __init__(self, ip: str, port: int):
        super().__init__(ip=ip, port=port)
        self.kill_endpoint: Endpoint = self.make_endpopint(path=f'/kill')

        @self.app.get(self.kill_endpoint.path)
        def shutdown_server():
            raise RuntimeError(f'Server shut down')
