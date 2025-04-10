import time


def run_app(port : int):
    from flask import Flask, render_template_string

    app = Flask(__name__)

    @app.route('/')
    def index():
        with open('helloworld.html', 'r') as f:
            HTML_TEMPLATE = f.read()
            return render_template_string(HTML_TEMPLATE)

    app.run(debug=True, port=port)


if __name__ == "__main__":
    from multiprocessing import Process

    p = Process(target=run_app)
    p.start()

    time.sleep(2)

    p.kill()