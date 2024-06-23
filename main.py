from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from process import process_file
from auth import authenticate_user, create_access_token, get_current_user

load_dotenv()

app = FastAPI()
app.add_middleware(HTTPSRedirectMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SECRET = os.getenv("SECRET")
manager = LoginManager(SECRET, token_url="/auth/login")

@manager.user_loader
def load_user(username: str):
    return authenticate_user(username)

@app.post("/auth/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data.username)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    file_location = f"files/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    processed_file_path = process_file(file_location)
    return {"file_url": f"/static/{processed_file_path}"}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return templates.TemplateResponse("index.html", {"request": {}})
