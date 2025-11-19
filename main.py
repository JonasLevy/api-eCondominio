from fastapi import FastAPI
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
import os
from fastapi.middleware.cors import CORSMiddleware



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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#rodar no terminak uvicorn main:app --reload
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload

