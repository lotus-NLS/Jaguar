class UserIO:

    @staticmethod
    def get_user_msg(prompt_msg : str = '') -> str:
        return input(prompt_msg)


    @staticmethod
    def get_confirmation(msg : str) -> bool:
        while True:
            user_input = input(f'{msg}')
            if user_input.lower() in ['y', 'n']:
                break
            else:
                print("Invalid input. Please enter (y/n)")


        if user_input == 'y':
            return True
        else:
            return False

# TODO: This object could be accessed from multiple threads so it should be made thread secure
# TODO: For example currently if get_user_msg is called from a side thread while it it is called and hasnt return in the main thread
# TODO: The main thread will still hold the IO stream and the second call will have to wait until that is done to get it
user_io = UserIO()