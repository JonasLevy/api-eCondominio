from fastapi import APIRouter
from schemas import UsuarioSchema, CondominiosSchema
from dependeces import pegarSessao, verificarToken
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario, Condominio, SindicoCondominio
from main import bcrypt_context


admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@admin_router.post("/criarsindico")
async def create(usuario_schema:UsuarioSchema, session:Session=Depends(pegarSessao)):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="Email já cadastrado!")
    else:
        senhaCrypt = bcrypt_context.hash(str(usuario_schema.senha))
        novoUsuario= Usuario(usuario_schema.nome, usuario_schema.cpf, usuario_schema.telefone, usuario_schema.email, senhaCrypt, "sindico")
        session.add(novoUsuario)
        session.commit()
        return {"mensagen": "Usuario criado"}

    
@admin_router.post("/criarcondominio")
async def criarCondominio(condominio_schema: CondominiosSchema, idSindico:int,session:Session=Depends(pegarSessao)):
    sindico = session.query(Usuario).filter(Usuario.id == idSindico).first()
    if not sindico:
        raise HTTPException(status_code=404, detail="Síndico não encontrado")
    if sindico.tipo != "sindico":
        raise HTTPException(status_code=400, detail="Usuário informado não é um síndico")

    condominio = Condominio(condominio_schema.nome, condominio_schema.endereco)
    session.add(condominio)
    session.flush() 
    sindicoCondominio = SindicoCondominio(condominio.id, idSindico)
    session.add(sindicoCondominio)
    session.commit()

    return {"condominio": {"id": condominio.id, "nome": condominio.nome}, "sindico_id": idSindico}
