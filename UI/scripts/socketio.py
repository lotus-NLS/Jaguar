from pywebdev.browser import window, document

socket = window.io.connect('http://localhost:5000')

def on_connect():
    print('connected')


def on_disconnect():
    print('disconnected')


def on_send_button_click(event):
    window.console.log('hey')
    text_bar = document["text_bar"]
    message = text_bar.value
    socket.emit('message', message)
    text_bar.value = ''


socket.on('connect', on_connect)
socket.on('disconnect', on_disconnect)
document['Send'].bind('click', on_send_button_click)