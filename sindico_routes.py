from fastapi import APIRouter
from schemas import UsuarioSchema, CondominiosSchema, AmbienteCondominioSchema, CriarMoradorSchema, CriarReservaSchema
from dependeces import pegarSessao, verificarToken
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario, SindicoCondominio, MoradorCondominio, ReservaAmbiente, AmbientesCondominio, Condominio
from main import bcrypt_context

sindico_router = APIRouter(prefix="/sindico", tags=["Sindico"], dependencies=[Depends(verificarToken)])

listaDeValoresInvalidos = [None, "", "\n", "\t"]

####################### MORADORES ##############################
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

@sindico_router.post("/editarmorador/{idMorador}")
async def criarMorador(morador_schema:CriarMoradorSchema, idMorador:int, session:Session=Depends(pegarSessao), sindico:Usuario=Depends(verificarToken)):
    
    usuarioMorador = session.query(Usuario).filter(Usuario.id == idMorador).first()
    moradorCondominio = session.query(MoradorCondominio).filter(MoradorCondominio.idMorador == idMorador).first()
    sindicoCondominio = session.query(SindicoCondominio).filter(SindicoCondominio.idUsuario == sindico.id, SindicoCondominio.idCondominio == moradorCondominio.idCondominio).first()
        
    if(sindico.tipo !="sindico" or not sindicoCondominio ):
        raise HTTPException(status_code=401, detail="Não autorizado!")
    
    if not int(idMorador):
        raise HTTPException(status_code=400, detail="id usuario Obrigatorio!")
    
    checkEmail = session.query(Usuario).filter(Usuario.email == morador_schema.email, Usuario.id != idMorador).first()
    
    if checkEmail:
        raise HTTPException(status_code=400, detail="Email já cadastrado!")
          
    if not usuarioMorador:
        raise HTTPException(status_code=404, detail="Morador não cadastrado!")
    else:
        
        if morador_schema.nome != usuarioMorador.nome and morador_schema.nome.strip()!="":
            usuarioMorador.nome = morador_schema.nome
        if morador_schema.telefone != usuarioMorador.telefone and morador_schema.telefone.strip()!="":
            usuarioMorador.telefone = morador_schema.telefone
        if morador_schema.cpf != usuarioMorador.cpf and morador_schema.cpf.strip()!="":
            usuarioMorador.cpf = morador_schema.cpf
        if morador_schema.email != usuarioMorador.email and morador_schema.email.strip()!="":
            usuarioMorador.email = morador_schema.email
        if morador_schema.email != usuarioMorador.email and morador_schema.email.strip()!="":
            usuarioMorador.email = morador_schema.email
        if morador_schema.senha and morador_schema.senha.strip() != "":
            try:
                senhaIgual = bcrypt_context.verify(morador_schema.senha, usuarioMorador.senha)
            except Exception:
                senhaIgual = False  # hash inválido no banco, força atualizar
            if not senhaIgual:
                senhaCrypto = bcrypt_context.hash(str(morador_schema.senha))
                usuarioMorador.senha = senhaCrypto
        if morador_schema.apartamento != moradorCondominio.apartamento and morador_schema.apartamento.strip()!="":
            moradorCondominio.apartamento = morador_schema.apartamento 
        if morador_schema.torre != moradorCondominio.torre and morador_schema.torre.strip()!="":
            moradorCondominio.torre = morador_schema.torre 
        session.commit()
        return   {"mensagem": "Morador atualizado com sucesso!",
                  "nome": usuarioMorador.nome,
                  "email": usuarioMorador.email,
                  "apartamento": moradorCondominio.apartamento,
                  "torre": moradorCondominio.torre} 

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
    .limit(10)
    )

    moradores_dict = [row._asdict() for row in moradores_rows]
    return moradores_dict

@sindico_router.get("/moradores/{idcondominio}/pesquisa")
async def moradoresPesquisa(idcondominio:int,  session:Session=Depends(pegarSessao),
                            nome: str | None=None, apt: str | None=None,
                            usuario:Usuario=Depends(verificarToken)):
    
    sindico = session.query(SindicoCondominio).filter(SindicoCondominio.idUsuario == usuario.id, SindicoCondominio.idCondominio == idcondominio).first()
    
    condominio = session.query(Condominio).filter(Condominio.id == idcondominio).first()
    
    if not condominio:
        raise HTTPException(status_code=404, detail="Condominio, não cadastrado")
    if not sindico:
        raise HTTPException(status_code=403, detail="Acesso negado: não é síndico deste condomínio")
    
    if nome:    
        moradores_rows = (
            session.query(
                Usuario.nome,
                Usuario.telefone,
                Usuario.email,
                MoradorCondominio.apartamento,
                MoradorCondominio.torre,
            )
            .join(MoradorCondominio, MoradorCondominio.idMorador == Usuario.id)
            .filter(MoradorCondominio.idCondominio == idcondominio,
                    Usuario.nome.ilike(f"%{nome}%"))
            .all()
            )
    if apt :    
        moradores_rows = (
            session.query(
                Usuario.nome,
                Usuario.telefone,
                Usuario.email,
                MoradorCondominio.apartamento,
                MoradorCondominio.torre,
            )
            .join(MoradorCondominio, MoradorCondominio.idMorador == Usuario.id)
            .filter(MoradorCondominio.idCondominio == idcondominio,
                    MoradorCondominio.apartamento.ilike(f"%{apt}%"))
            .all()
            )

    moradores_dict = [row._asdict() for row in moradores_rows]
    return moradores_dict


####################### AMBIENTES ##############################    
@sindico_router.post("/criarambiente")
async def criarambiente(ambiente_schema:AmbienteCondominioSchema, session:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarToken)):
    sindico = session.query(SindicoCondominio).filter(usuario.id == SindicoCondominio.idUsuario, ambiente_schema.idCondominio == SindicoCondominio.idCondominio).first()
    if usuario.tipo != "sindico":
        raise HTTPException(status_code=400, detail="Não autorizado")
        
    if not sindico:
        raise HTTPException(status_code=400, detail="Não é sindico deste Condominio")
    else:
        ambiente = AmbientesCondominio(ambiente_schema.idCondominio ,ambiente_schema.nome, ambiente_schema.info)
        session.add(ambiente)
        session.commit()
        return{"mensage":"ambiente criado com sucesso",
               "nome": ambiente.nome,
               "consominio": ambiente.idCondominio}
        
@sindico_router.post("/editarambiente/{idcondominio}/{idAmbiente}")
async def editarambiente(idcondominio: int, idAmbiente: int, ambiente_schema: AmbienteCondominioSchema, session: Session = Depends(pegarSessao), usuario: Usuario = Depends(verificarToken)):
    sindico = session.query(SindicoCondominio).filter(SindicoCondominio.idUsuario == usuario.id, SindicoCondominio.idCondominio == idcondominio).first()
    ambiente = session.query(AmbientesCondominio).filter(AmbientesCondominio.id == idAmbiente, AmbientesCondominio.idCondominio == idcondominio).first()
    if not ambiente:
        raise HTTPException(status_code=400, detail="Ambiente não cadastrado")
    if not sindico:
        raise HTTPException(status_code=400, detail="Não é sindico deste Condominio")
    if ambiente_schema.nome != ambiente.nome and ambiente_schema.nome.strip() != "":
        ambiente.nome = ambiente_schema.nome
    if ambiente_schema.info != ambiente.info and (ambiente_schema.info is not None):
        ambiente.info = ambiente_schema.info
    session.commit()
    return{"mensage":"ambiente editado com sucesso",
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

####################### RESERVAS DE AMBIENTE ##############################    
@sindico_router.post("/criarreserva/{idCondominio}")
async def criarreserva(criarReserva:CriarReservaSchema, idCondominio: int ,session:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarToken)):
    
    if idCondominio in listaDeValoresInvalidos:
        raise HTTPException(status_code=400, detail="id Condomio Obrigatorio!")
    sindico = session.query(SindicoCondominio).filter(SindicoCondominio.idUsuario == usuario.id, SindicoCondominio.idCondominio == idCondominio).first()
    if not sindico:
        raise HTTPException(status_code=400, detail="Não é sindico deste Condominio")
    
    verificaAmbiente = session.query(AmbientesCondominio).filter(AmbientesCondominio.id == criarReserva.idAmbiente, AmbientesCondominio.idCondominio == idCondominio).first()
    if not verificaAmbiente:
        raise HTTPException(status_code=400, detail="Ambiente não cadastrado neste condominio")
    
    verificarDataReserva = session.query(ReservaAmbiente).filter(ReservaAmbiente.dataReserva == criarReserva.dataReserva, ReservaAmbiente.idAmbiente == criarReserva.idAmbiente).first()
    if verificarDataReserva:
        raise HTTPException(status_code=400, detail="Já existe uma reserva para este ambiente nesta data")  
    
    reserva = ReservaAmbiente(
        criarReserva.idAmbiente,
        usuario.id,
        criarReserva.dataReserva,
        criarReserva.horaInicio,
        criarReserva.horaFim,
        idCondominio,
        criarReserva.info)
    session.add(reserva)
    session.commit()
    
    return {"mensagem": "Reserva criada com sucesso!",
            "Ambiente:": verificaAmbiente.nome,
            "Data da Reserva:": criarReserva.dataReserva,
            "Hora Início:": criarReserva.horaInicio,
            "Hora Fim:": criarReserva.horaFim}