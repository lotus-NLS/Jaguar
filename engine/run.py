from engine.l0_main.lotus_engine import LotusEngine


def testFunction():
    pass

if __name__ == "__main__":
    engine = LotusEngine()


    # engine.do_talk(query='Please open the terminal')
    # engine.do_talk(query='Find out what files are in the dir that just opened')

    # 1| Please open the termiinal
    # 2 | Find out what files are in your current directory
    # 3 | Search for beavers on google
    # 4 | Visit beave website
    # 5 | Open /home/daniel/lotus/engine
    # 6 | What top level folders does it contain


    testFunction()

    while True:
        user_input = input("User:")
        if user_input == 'exit':
            break
        engine.do_talk(query=user_input)

