from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str

@app.get("/send_string/")
def send_string(item: Item):
    return {"message": f"Hello {item.name}"}
