class UserIO:
    @staticmethod
    def get_confirmation(msg : str) -> bool:
        while True:
            user_input = input(msg)
            if user_input.lower() in ['y', 'n']:
                break
            else:
                print("Invalid input. Please enter (y/n)")


        if user_input == 'y':
            return True
        else:
            return False

# Note that since there is only a single user_io object , which is not threaded, calls from anywhere
# in the project will block other calls.
# However, considering that there is only a single user, that should make sense.
user_io = UserIO()