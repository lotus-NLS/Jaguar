from engine.l0_main.lotus_engine import LotusEngine

if __name__ == "__main__":
    engine = LotusEngine()
    while True:
        user_input = input("User:")
        if user_input == 'exit':
            break
        engine.do_talk(query=user_input)
        print()

