from engine import LotusEngine

# ----------------------------------------------

ip = '127.0.0.1'
port = 5001

the_engine = LotusEngine(ip=ip, port=port, local=True)
the_engine.run()
input('Press any key to quit')
