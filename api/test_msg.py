from .the_api import LotusAPI


comm = LotusAPI()
# init_confirm = comm.initialize_request(userID='the_user')
receive_confirm = comm.msg_post(msg_content='bla bla')
server_message = comm.msg_get()

# print(init_confirm)
print(receive_confirm)
print(server_message)