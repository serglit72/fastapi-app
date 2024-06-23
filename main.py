from fastapi import FastAPI
from fastapi_login import LoginManager

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}