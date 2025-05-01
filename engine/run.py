from engine.l0_main.lotus_engine import LotusEngine

if __name__ == "__main__":
    engine = LotusEngine()
    engine.do_talk(query='Please open the terminal')
    engine.do_talk(query='Execute the echo command with a hello world message')

    while True:
        user_input = input("User:")
        if user_input == 'exit':
            break
        engine.do_talk(query=user_input)
        print()

