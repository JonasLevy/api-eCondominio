from fastapi import APIRouter
from schemas import UsuarioSchema
from dependeces import pegarSessao
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import Condominio

morador_router = APIRouter(prefix="/morador", tags=["Morador"])