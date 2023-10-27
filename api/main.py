from fastapi import FastAPI
from uvicorn import Config, Server

# fastAPI runs on a specified socket
# Then can define get and post interfaces through @app.get(...) and @app.post(...)
#

app = FastAPI()

@app.get("/send_string/")
def send_string(name: str):
    return {"message": f"Hello {name}"}

if __name__ == "__main__":
    config = Config(app=app, host="127.0.0.1", port=8000, reload=True)
    server = Server(config)
    server.run()
