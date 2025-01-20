from engine.l0_engine.dev_server import DevServer

if __name__ == "__main__":
    dev_server = DevServer.localhost()
    dev_server.serve()