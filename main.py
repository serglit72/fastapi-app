from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from typing import List
import os
from dotenv import load_dotenv
from process import process_file
# from auth import authenticate_user, create_access_token, get_current_user
import uuid
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import UUID4, BaseModel, ConfigDict
from pydantic_settings import BaseSettings

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException




load_dotenv()

class Settings(BaseSettings):
    secret: str = ""  # automatically taken from environment variable


class UserCreate(BaseModel):
    email: str
    password: str
    model_config = ConfigDict(from_attributes=True)


class User(UserCreate):
    id: UUID4


DEFAULT_SETTINGS = Settings(_env_file=".env")
DB = {
    "users": {}
}
TOKEN_URL = "/auth/token"


app = FastAPI()
app.add_middleware(HTTPSRedirectMiddleware)
manager = LoginManager(DEFAULT_SETTINGS.secret, TOKEN_URL)



app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SECRET = os.getenv("SECRET")
manager = LoginManager(SECRET, token_url="/auth/login")

# @manager.user_loader
# def load_user(username: str):
#     return authenticate_user(username)

@manager.user_loader()
def get_user(email: str):
    return DB["users"].get(email)


@app.get("/")
def index():
    with open("./templates/index.html", 'r') as f:
        return HTMLResponse(content=f.read())

# @app.post("/auth/login")
# def login(data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(data.username, data.password)
#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid credentials")
#     access_token = create_access_token(data.username)
#     return {"access_token": access_token, "token_type": "bearer"}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...), user=Depends(get_user)):
    file_location = f"files/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    processed_file_path = process_file(file_location)
    return {"file_url": f"/static/{processed_file_path}"}

# @app.get("/", response_class=HTMLResponse)
# async def read_root():
#     return templates.TemplateResponse("index.html", {"request": {}})

@app.post("/auth/register")
def register(user: UserCreate):
    if user.email in DB["users"]:
        raise HTTPException(status_code=400, detail="A user with this email already exists")
    else:
        db_user = User(**user.dict(), id=uuid.uuid4())
        # PLEASE hash your passwords in real world applications
        DB["users"][db_user.email] = db_user
        return {"detail": "Successful registered"}


@app.post(TOKEN_URL)
def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = get_user(email)  # we are using the same function to retrieve the user
    if not user:
        raise InvalidCredentialsException  # you can also use your own HTTPException
    elif password != user.password:
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data=dict(sub=email)
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.get("/private")
def private_route(user=Depends(manager)):
    return {"detail": f"Welcome {user.email}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app")