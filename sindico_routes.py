from fastapi import APIRouter
from schemas import UsuarioSchema, CondominiosSchema, AmbienteCondominioSchema, CriarMoradorSchema
from dependeces import pegarSessao, verificarToken
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario, SindicoCondominio, MoradorCondominio, AmbientesCondominio, Condominio
from main import bcrypt_context

sindico_router = APIRouter(prefix="/sindico", tags=["Sindico"], dependencies=[Depends(verificarToken)])

@sindico_router.post("/criarmorador")
async def criarMorador(morador_schema:CriarMoradorSchema, session:Session=Depends(pegarSessao), sindico:Usuario=Depends(verificarToken)):
    
    if(sindico.tipo !="sindico" ):
        raise HTTPException(status_code=400, detail="Não autorizado")
    
    usuarioMorador = session.query(Usuario).filter(Usuario.email == morador_schema.email).first()
    if usuarioMorador:
        raise HTTPException(status_code=400, detail="Email já cadastrado!")
    elif not int(morador_schema.idCondominio):
        raise HTTPException(status_code=400, detail="id Condomio Obrigatorio!")
    else:
        senhaCrypt = bcrypt_context.hash(str(morador_schema.senha))
        novoUsuario= Usuario(morador_schema.nome, morador_schema.cpf, morador_schema.telefone, morador_schema.email, senhaCrypt, "morador")
        session.add(novoUsuario)
        session.flush()
        moradorCOndominio = MoradorCondominio(morador_schema.idCondominio ,novoUsuario.id, morador_schema.apartamento, morador_schema.torre)
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
async def getAmbientes(idcondominio:int, session:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarToken)):
    sindico = session.query(SindicoCondominio).filter(SindicoCondominio.idUsuario == usuario.id, SindicoCondominio.idCondominio == idcondominio).first()
    condominio = session.query(Condominio).filter(Condominio.id == idcondominio).first()
    if not condominio:
        raise HTTPException(status_code=400, detail="Condominio, não cadastrado")
    if not sindico:
        raise HTTPException(status_code=400, detail="Não é sindico deste Condominio")
    
    return{"ambientes": condominio.ambientes}

@sindico_router.get("/moradores/{idcondominio}")
async def moradores(idcondominio:int,  session:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarToken)):
    
    sindico = session.query(SindicoCondominio).filter(SindicoCondominio.idUsuario == usuario.id, SindicoCondominio.idCondominio == idcondominio).first()
    
    condominio = session.query(Condominio).filter(Condominio.id == idcondominio).first()
    
    
    if not condominio:
        raise HTTPException(status_code=404, detail="Condominio, não cadastrado")
    if not sindico:
        raise HTTPException(status_code=403, detail="Acesso negado: não é síndico deste condomínio")

    
    moradores_rows = (
    session.query(
        Usuario.nome,
        Usuario.telefone,
        Usuario.email,
        MoradorCondominio.apartamento,
        MoradorCondominio.torre,
    )
    .join(MoradorCondominio, MoradorCondominio.idMorador == Usuario.id)
    .filter(MoradorCondominio.idCondominio == idcondominio)
    .all()
    )

    moradores_dict = [row._asdict() for row in moradores_rows]
    return moradores_dict


    