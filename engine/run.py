from engine import LotusEngine

if __name__ == "__main__":
    engine = LotusEngine()

    while True:
        print('User: ', end='')
        user_input = input()
        if user_input == 'exit':
            break
        engine.converse(msg=user_input)
        print()


