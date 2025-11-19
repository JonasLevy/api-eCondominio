from fastapi import APIRouter, Depends, HTTPException
from models import Usuario, MoradorCondominio, Condominio, SindicoCondominio
from dependeces import pegarSessao, verificarToken
from main import bcrypt_context, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM, oauth2_scheme
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


def criarToken(id_usuario, duracaoToken = timedelta(days=int(ACCESS_TOKEN_EXPIRE_MINUTES))):
    dataExpiração = datetime.now(timezone.utc) + duracaoToken
    dic_info = {"sub":str(id_usuario), "exp": dataExpiração}
    jwtCodificacao = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return jwtCodificacao

def autenticarUsuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
   
    if not usuario:
       return False
    elif not bcrypt_context.verify(senha, usuario.senha):
           return False
    
    return usuario


@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session=Depends(pegarSessao) ):
    usuario = autenticarUsuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario ou senha Invalido")
    else:
        sindicoCondominios = session.query(Condominio).join(SindicoCondominio).filter(SindicoCondominio.idUsuario == usuario.id ).all()
        condominioMorador = session.query(Condominio).join(MoradorCondominio).filter(MoradorCondominio.idMorador == Condominio.id ).all()
        token = criarToken(usuario.id)
        refreshToken = criarToken(usuario.id, duracaoToken=timedelta(days=7))
        return{
            "access_token": token,
            "refresh_token": refreshToken,
            "token_type": "Bearer",
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "tipo": usuario.tipo,
                "condominioMorador": condominioMorador,
                "sindicoCondominio": sindicoCondominios
            } }

@auth_router.post("/loginForm")
async def loginForm(dadosFormulario: OAuth2PasswordRequestForm = Depends(), session: Session=Depends(pegarSessao) ):
    usuario = autenticarUsuario(dadosFormulario.username, dadosFormulario.password, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Não deu bom")
    else:
        token = criarToken(usuario.id)
        return{
            "access_token": token,
            "token_type": "Bearer"}

    
@auth_router.get("/refresh")
async def useRefreshToken(usuario:Usuario=Depends(verificarToken)):
    access_token = criarToken(usuario.id)
    return{
            "access_token": access_token,
            "token_type": "Bearer"}