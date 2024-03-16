from api.network import Network, NetworkArea, Socket
from hollarek.devtools import Unittest

class TestNetwork(Unittest):

    def test_init_default_sockets(self):
        network = Network()
        self.assertEqual(network.webapp_socket.ip, network.get_host(area=NetworkArea.LOCALHOST))
        self.assertEqual(network.webapp_socket.port, 5000)
        self.assertEqual(network.engine_socket.ip, network.get_host(area=NetworkArea.LOCALHOST))
        self.assertEqual(network.engine_socket.port, 5001)

    def test_init_custom_sockets(self):
        custom_webapp_socket = Socket(ip_addr="192.168.1.10", port=6000)
        custom_engine_socket = Socket(ip_addr="192.168.1.11", port=6001)
        network = Network(webapp_socket=custom_webapp_socket, engine_socket=custom_engine_socket)
        self.assertEqual(network.webapp_socket, custom_webapp_socket)
        self.assertEqual(network.engine_socket, custom_engine_socket)


    def test_host(self):
        self.assertEqual(Network.get_host(NetworkArea.LOCALHOST), '127.0.0.1')
        self.assertIsInstance(Network.get_private_ip(), str)
        with self.assertRaises(PermissionError):
            Network.get_host(NetworkArea.GLOBAL)

    def test_get_public_ip_addr(self):
        ip_addr = Network.get_public_ip()
        self.assertIsInstance(ip_addr, str)
        self.log(f'Public ip addr is {ip_addr}')

    def test_get_private_ip_addr(self):
        ip_addr = Network.get_private_ip()
        self.assertIsInstance(ip_addr, str)
        self.log(f'Private ip addr is {ip_addr}')

if __name__ == '__main__':
    TestNetwork.execute_all()
