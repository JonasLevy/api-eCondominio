from sqlalchemy.orm import sessionmaker, Session
from models import db
from models import Usuario
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from main import SECRET_KEY, ALGORITHM, oauth2_scheme


def pegarSessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()
        

def verificarToken(token:str = Depends(oauth2_scheme), session:Session = Depends(pegarSessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM )
        idUsuario = int(dic_info.get("sub"))
    except JWTError as error:
        print(error)
        raise HTTPException(status_code=401, detail="Token inválido")
    usuario = session.query(Usuario).filter(Usuario.id == idUsuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario  

def verificarTokenSindico(token:str = Depends(oauth2_scheme), session:Session = Depends(pegarSessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM )
        idUsuario = int(dic_info.get("sub"))
    except JWTError as error:
        print(error)
        raise HTTPException(status_code=401, detail="Token inválido")
    usuario = session.query(Usuario).filter(Usuario.id == idUsuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if usuario.tipo != "sindico":
        raise HTTPException(status_code=401, detail="Permissão negada!!")

    
    return usuario  