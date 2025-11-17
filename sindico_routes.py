from fastapi import APIRouter
from schemas import UsuarioSchema, CondominiosSchema, AmbienteCondominioSchema
from dependeces import pegarSessao, verificarToken
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario, SindicoCondominio, MoradorCondominio, AmbientesCondominio
from main import bcrypt_context

sindico_router = APIRouter(prefix="/sindico", tags=["Sindico"], dependencies=[Depends(verificarToken)])

@sindico_router.post("/criarmorador")
async def criarUsuario(usuario_schema:UsuarioSchema, idCondominio:int,session:Session=Depends(pegarSessao), sindico:Usuario=Depends(verificarToken)):
    
    if(sindico.tipo !="sindico" ):
        raise HTTPException(status_code=400, detail="Não autorizado")
    
    usuarioMorador = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuarioMorador:
        raise HTTPException(status_code=400, detail="Email já cadastrado!")
    elif not int(idCondominio):
        raise HTTPException(status_code=400, detail="id Condomio Obrigatorio!")
    else:
        senhaCrypt = bcrypt_context.hash(str(usuario_schema.senha))
        novoUsuario= Usuario(usuario_schema.nome, usuario_schema.email, senhaCrypt, "morador")
        session.add(novoUsuario)
        session.flush()
        moradorCOndominio = MoradorCondominio(idCondominio ,novoUsuario.id)
        session.add(moradorCOndominio)
        session.commit()
        return {"mensagen": "Morador criado"}
    
@sindico_router.post("/criarambiente")
async def criarambiente(ambiente_schema:AmbienteCondominioSchema, session:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarToken)):
    sindico = session.query(SindicoCondominio).filter(usuario.id == SindicoCondominio.idUsuario, ambiente_schema.idCondominio == SindicoCondominio.idCondominio).first()
    if usuario.tipo != "sindico":
        raise HTTPException(status_code=400, detail="Não autorizado")
        
    if not sindico:
        raise HTTPException(status_code=400, detail="Não é sindico deste Condominio")
    else:
        ambiente = AmbientesCondominio(ambiente_schema.idCondominio ,ambiente_schema.nome)
        session.add(ambiente)
        session.commit()
        return{"mensage":"ambiente criado com sucesso",
               "nome": ambiente.nome,
               "consominio": ambiente.idCondominio}
        
@sindico_router.get("/ambientes/{idcondominio}")
async def getAmbientes(idcondominio:int, session:Session=Depends(pegarSessao)):
    ambientes = session.query(AmbientesCondominio).filter(AmbientesCondominio.idCondominio == idcondominio).all()
    return{"resp": ambientes}
    


    