from .the_api import LotusAPI


comm = LotusAPI()
# init_confirm = comm.initialize_request(userID='the_user')
receive_confirm = comm.post_engine_message(msg_content='bla bla')
server_message = comm.get_user_msg()

# print(init_confirm)
print(receive_confirm)
print(server_message)