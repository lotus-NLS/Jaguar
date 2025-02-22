from engine import LotusEngine

if __name__ == "__main__":
    engine = LotusEngine()

    while True:
        user_input = input()
        if user_input == 'exit':
            break
        print(f'User: {user_input}')
        engine.converse(msg=user_input)


