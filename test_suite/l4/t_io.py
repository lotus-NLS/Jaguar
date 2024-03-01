from unittest.mock import patch
from hollarek.dev import Unittest
from api import DefaultNetwork, Entry, APIMessage, DialogueRole
from engine.l4_singletons import EngineIO


class TestEngineIO(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.engine_io = EngineIO(ip=DefaultNetwork.ip_engine, port=DefaultNetwork.port_engine)

    def setUp(self):
        self.engine_io._outgoing_entry_queue.queue.clear()
        self.engine_io._incoming_entry_waiter.clear()

    def test_send(self):
        test_entry = Entry(role=DialogueRole.user_role(), msg="Test message")
        self.engine_io.get_response_stream(test_entry)
        self.assertEqual(test_entry, self.engine_io._outgoing_entry_queue.get_nowait())

    def test_get_entry(self):
        test_entry = Entry(role=DialogueRole.user_role(), msg="Test message")
        self.engine_io._incoming_entry_waiter.write(test_entry)
        retrieved_entry = self.engine_io.get_response_stream()
        self.assertEqual(test_entry, retrieved_entry)

    @patch('flask.Flask.run')
    def test_launch(self, mock_run):
        self.engine_io.launch()
        mock_run.assert_called_once_with(host=DefaultNetwork.ip_engine, port=DefaultNetwork.port_engine)

if __name__ == "__main__":
    TestEngineIO.run_tests()
