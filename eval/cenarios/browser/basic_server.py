import os.path
import time

from flask import Flask, render_template_string


def run_basic_server(port : int):
    app = Flask(__name__)
    dirpath = os.path.dirname(__file__)

    @app.route('/')
    def index():
        with open(f'{dirpath}/helloworld.html', 'r') as f:
            HTML_TEMPLATE = f.read()
            return render_template_string(HTML_TEMPLATE)

    app.run(port=port)


if __name__ == "__main__":
    from multiprocessing import Process

    p = Process(target=run_basic_server)
    p.start()

    time.sleep(2)

    p.kill()