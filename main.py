from fastapi import FastAPI
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/loginForm")

app = FastAPI()

from admin_routers import admin_router
from sindico_routes import sindico_router
from morador_routes import morador_router
from login_router import auth_router

app.include_router(admin_router)
app.include_router(sindico_router)
app.include_router(morador_router)
app.include_router(auth_router)



#rodar no terminak uvicorn main:app --reload
