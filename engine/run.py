from engine.l0_engine.dev_server import DevServer
from engine.l2_models.llm import LLM


if __name__ == "__main__":
    monitor_endpoint = LLM.dev_endpoint()
    dev_server = DevServer(ip=monitor_endpoint.ip, port=monitor_endpoint.port)
    dev_server.serve()