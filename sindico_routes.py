from fastapi import APIRouter
from schemas import UsuarioSchema, CondominiosSchema, AmbienteCondominioSchema, CriarMoradorSchema, ReservaSchema, EditarReservaSchema, VisitaSchema, ServicoSchema, ServicoEditarSchema, EditarMoradorSchema, AmbienteCondominioEditarSchema
from dependeces import pegarSessao, verificarTokenSindico
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario, SindicoCondominio, MoradorCondominio, ReservaAmbiente, AmbientesCondominio, Condominio, Pessoas, Visitas, Servicos
from main import bcrypt_context
from datetime import date, time

sindico_router = APIRouter(prefix="/sindico", tags=["Sindico"], dependencies=[Depends(verificarTokenSindico)])

listaDeValoresInvalidos = [None, "", "\n", "\t", 0, "string"]

####################### MORADORES ##############################
@sindico_router.post("/morador")
async def criarMorador(body:CriarMoradorSchema, sessaoDb:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarTokenSindico)):
    
    usuario.verificaCondominio(body.idCondominio)
    
    verificaEmailCadastro = sessaoDb.query(Usuario).filter(Usuario.email == body.email).first()
    
    if verificaEmailCadastro:
        raise HTTPException(status_code=400, detail="Email já cadastrado!")
    
    elif not int(body.idCondominio): #verificar se é numero e !=0
        raise HTTPException(status_code=400, detail="id Condomio Obrigatorio!")
    else:
        senhaCrypt = bcrypt_context.hash(str(body.senha))
        novoUsuario= Usuario(body.nome, body.cpf, body.telefone, body.email, senhaCrypt, "morador")
        sessaoDb.add(novoUsuario)
        sessaoDb.flush()
        moradorCOndominio = MoradorCondominio(body.idCondominio ,novoUsuario.id, body.apartamento, body.torre)
        sessaoDb.add(moradorCOndominio)
        sessaoDb.commit()
        sessaoDb.refresh(moradorCOndominio)
        
        
        return {"mensagen": "Morador criado",
                "nomeUsuario": novoUsuario.nome,
                "morador": moradorCOndominio
                }

@sindico_router.patch("/morador/{idMoradorCondominio}")
async def criarMorador(body:EditarMoradorSchema, idMoradorCondominio:int, session:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarTokenSindico)):
    
    moradorCondominio = session.query(MoradorCondominio).filter(MoradorCondominio.id == idMoradorCondominio).first()
    if not moradorCondominio:
        raise HTTPException(status_code=404, detail="Morador não cadastrado!")
    
    verificaSindicoMorador = usuario.verificaCondominio(moradorCondominio.idCondominio)
    if not verificaSindicoMorador:
        raise HTTPException(status_code=403, detail="Acesso negado: não é síndico deste condomínio")
    
    usuarioMorador = session.query(Usuario).filter(Usuario.id == moradorCondominio.idMorador).first()
    
    checkEmail = session.query(Usuario).filter(Usuario.email == body.email, Usuario.id != moradorCondominio.idMorador).first()
    
    if checkEmail:
        raise HTTPException(status_code=400, detail="Email já cadastrado!")
    
    dados = body.model_dump(exclude_unset=True, exclude_none=True) 

    for campo, valor in dados.items():

        # --- Tratamento especial da senha ---
        if campo == "senha":
            if valor in listaDeValoresInvalidos:
                continue  # senha vazia -> não atualizar

            try:
                senhaIgual = bcrypt_context.verify(valor, usuarioMorador.senha)
            except Exception:
                senhaIgual = False  # hash antigo/ruim -> força atualizar

            if not senhaIgual:
                usuarioMorador.senha = bcrypt_context.hash(str(valor))
            
            continue  # não deixar cair no setattr

        if valor not in listaDeValoresInvalidos:
            setattr(usuarioMorador, campo, valor)
        
        session.commit()
        return   {"mensagem": "Morador atualizado com sucesso!",
                  "nome": usuarioMorador.nome,
                  "email": usuarioMorador.email,
                  "apartamento": moradorCondominio.apartamento,
                  "torre": moradorCondominio.torre} 

@sindico_router.get("/morador/{idcondominio}")
async def moradores(idcondominio:int, nome: str | None=None, apt: str | None=None, sessaoDb:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarTokenSindico)):
    
    usuario.verificaCondominio(idcondominio)
    
    if not nome or apt:
        moradores_rows = (
        sessaoDb.query(
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
    
    if nome:    
        moradores_rows = (
            sessaoDb.query(
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
        
    if apt:    
        moradores_rows = (
            sessaoDb.query(
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
@sindico_router.post("/ambiente")
async def criarambiente(body:AmbienteCondominioSchema, sessaoDb:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarTokenSindico)):
    
    usuario.verificaCondominio(body.idCondominio)
    
    ambiente = AmbientesCondominio(body.idCondominio ,body.nome, body.info)
    sessaoDb.add(ambiente)
    sessaoDb.commit()
    return{"mensage":"ambiente criado com sucesso",
            "nome": ambiente.nome,
            "consominio": ambiente.condominio}
        
@sindico_router.patch("/ambiente/{idAmbienteCondominio}")
async def editarambiente(idAmbienteCondominio: int, body: AmbienteCondominioEditarSchema, session: Session = Depends(pegarSessao), usuario: Usuario = Depends(verificarTokenSindico)):
    ambiente = session.query(AmbientesCondominio).filter(AmbientesCondominio.id== idAmbienteCondominio).first()
    if not ambiente:
        raise HTTPException(status_code=404, detail="Ambiente não encontrado")
    
    usuario.verificaCondominio(ambiente.idCondominio)
    
    dados = body.model_dump(exclude_none=True, exclude_unset=True)
    for campo, valor in dados.items():
        if valor not in listaDeValoresInvalidos:
            setattr(ambiente, campo, valor)
    
    session.commit()
    session.refresh(ambiente)
    return{"mensage":"ambiente editado com sucesso",
               "ambiente": ambiente} 

@sindico_router.get("/ambiente/{idcondominio}")
async def getAmbientes(idcondominio:int, session:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarTokenSindico)):
    
    usuario.verificaCondominio(idcondominio)
    
    condominio = session.query(Condominio).filter(Condominio.id == idcondominio).first()
    
    return{"ambientes": condominio.ambientes}

####################### RESERVAS DE AMBIENTE ##############################    
@sindico_router.post("/reserva/{idCondominio}")
async def criarreserva(criarReserva:ReservaSchema, idCondominio: int , sessaoDb:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarTokenSindico)):

    usuario.verificaCondominio(idCondominio)
    
    verificaAmbiente = sessaoDb.query(AmbientesCondominio).filter(AmbientesCondominio.id == criarReserva.idAmbiente, AmbientesCondominio.idCondominio == idCondominio).first()
    if not verificaAmbiente:
        raise HTTPException(status_code=400, detail="Ambiente não cadastrado neste condominio")
    
    verificarDataReserva = sessaoDb.query(ReservaAmbiente).filter(ReservaAmbiente.dataReserva == criarReserva.dataReserva, ReservaAmbiente.idAmbiente == criarReserva.idAmbiente).first()
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
    sessaoDb.add(reserva)
    sessaoDb.commit()
    sessaoDb.refresh(reserva)
    
    return {"mensagem": "Reserva criada com sucesso!",
            "Ambiente:": verificaAmbiente.nome,
            "Data da Reserva:": criarReserva.dataReserva,
            "Hora Início:": criarReserva.horaInicio,
            "Hora Fim:": criarReserva.horaFim}

@sindico_router.patch("/reserva/{idCondominio}/{idReserva}")
async def editarReserva(body:EditarReservaSchema, idCondominio:int, idReserva:int, sessaoDb:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarTokenSindico)):
    
    usuario.verificaCondominio(idCondominio)
        
    reserva = sessaoDb.query(ReservaAmbiente).filter(ReservaAmbiente.id == idReserva).first()
    
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    
    verificaData = sessaoDb.query(ReservaAmbiente).filter(ReservaAmbiente.dataReserva == body.dataReserva, ReservaAmbiente.idAmbiente == body.idAmbiente, reserva.idMorador != ReservaAmbiente.idMorador).first()
    
    if verificaData:
        raise HTTPException(status_code=400, detail="Ambiente indisponivel")
        
    dados = body.model_dump(exclude_unset=True, exclude_none=True)
    
    for campo, valor in dados.items():
        if valor not in listaDeValoresInvalidos:
            setattr(reserva, campo, valor)  

    sessaoDb.commit()
    sessaoDb.refresh(reserva)
    
    return { "mensagem": "Status alterado",
            "reserva": reserva}
    
@sindico_router.get("/reserva/{idCondominio}")
async def reservas(idCondominio:int, usuario:Usuario=Depends(verificarTokenSindico), sessaoDb:Session=Depends(pegarSessao)):
    
    usuario.verificaCondominio(idCondominio)
    
    reservas_rows = sessaoDb.query(
        AmbientesCondominio.nome.label("Ambiente"),
        Usuario.nome,
        MoradorCondominio.apartamento,
        ReservaAmbiente
    ).join(AmbientesCondominio, AmbientesCondominio.id == ReservaAmbiente.idAmbiente).join(MoradorCondominio, MoradorCondominio.idMorador == ReservaAmbiente.idMorador).join(Usuario, Usuario.id == ReservaAmbiente.idMorador).all()
    
    reservas_rows2 = sessaoDb.query(
        AmbientesCondominio.nome.label("Ambiente"),
        Usuario.nome,
        ReservaAmbiente
    ).join(AmbientesCondominio, AmbientesCondominio.id == ReservaAmbiente.idAmbiente).join(SindicoCondominio,SindicoCondominio.idUsuario == ReservaAmbiente.idMorador).join(Usuario, Usuario.id == ReservaAmbiente.idMorador).all()

    reservas = [row._asdict() for row in [*reservas_rows,*reservas_rows2]]
    return reservas
    
####################### VISITAS ##############################    

@sindico_router.post("/visita")
async def criarVisita(body: VisitaSchema, sessaoDb:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarTokenSindico)):
    
    usuario.verificaCondominio(body.idCodominio)
    
    verificaPessoa = sessaoDb.query(Pessoas).filter(Pessoas.cpf == body.cpf).first()
    
    if verificaPessoa:
        visita = Visitas(verificaPessoa.id, usuario.id, "sindico", body.idCodominio , body.info, body.dataVisita, body.horaVisita)
        sessaoDb.add(visita)
        sessaoDb.commit()
        sessaoDb.refresh(visita)
        
        return {"mensagem":"Visita criada",
            "visita": visita}
    
    pessoa = Pessoas(body.nome, body.cpf, body.telefone)
    sessaoDb.add(pessoa)
    sessaoDb.flush()
    visita = Visitas(pessoa.id, usuario.id, "sindico", body.idCodominio, body.info, body.dataVisita, body.horaVisita)
    sessaoDb.add(visita)
    sessaoDb.commit()
    sessaoDb.refresh(visita) 
    
    return {"mensagem":"Visita criada",
            "visita": visita}
    
@sindico_router.patch("/visita/{idVisita}")
async def criarVisita(idVisita:int, body: VisitaSchema, sessaoDb:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarTokenSindico)):
    
    usuario.verificaCondominio(body.idCodominio)
    
    visita = sessaoDb.query(Visitas).filter(Visitas.id == idVisita).first()
    
    if not visita:
        raise HTTPException(status_code=404, detail="Visita não encontrada")
    
    pessoa = sessaoDb.query(Pessoas).filter(Pessoas.cpf == body.cpf).first()
    
    pessoaDic = {
        "nome": body.nome,
        "telefone": body.telefone,
        "cpf":body.cpf
    }
    
    visitaDicionio = {
        "info": body.info,
        "dataVisita": body.dataVisita,
        "horaVisita": body.horaVisita  
    }
    
    for campo, valor in pessoaDic.items():
        if valor not in (None, "", "\n", "\t", 0, " "):
            setattr(pessoa, campo, valor)
    
    for campo, valor in visitaDicionio.items():
        if valor not in (None, "", "\n", "\t", 0, " "):
            setattr(visita, campo, valor)
    
    sessaoDb.commit()
    
    sessaoDb.refresh(visita)
    sessaoDb.refresh(pessoa)
    
    return {
        "pessoa": pessoa,
        "visita": visita    }
    
@sindico_router.get("/visitas/{idCondominio}/{apto}")
async def visitas( idCondominio:int, apto:int ,torre: str|None=None,   sessaoDb:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarTokenSindico)):
    
    usuario.verificaCondominio(idCondominio)
    
    buscaVisitas = sessaoDb.query(Visitas).filter(Visitas.idCodominio == idCondominio, Visitas.apartamento.ilike(f"%{apto}%")).all()
    
    if not buscaVisitas:
        raise HTTPException(status_code=40, detail="Nenhum apartamento encontrado!")
        
    return buscaVisitas

####################### SERVICO ##############################   
@sindico_router.post("/servico")
async def criarServico(body: ServicoSchema, sessaoDb:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarTokenSindico)): 
    
    usuario.verificaCondominio(body.idCodominio)
    
    novoServico = Servicos(
                            usuario.id, body.idCodominio, body.idAmbiente,
                            body.apartamento, body.torre, body.dataInicio,
                            body.dataFim, body.horaInicio, body.horaFim,
                            body.info, body.empresa)
    
    sessaoDb.add(novoServico)
    sessaoDb.commit()
    sessaoDb.refresh(novoServico)
        
    return {"Mensagem": "Servico criado!",
            "Servico":novoServico}
    
@sindico_router.patch("/servico/{idServico}")
async def editarServico(
    idServico: int,
    body: ServicoEditarSchema,
    sessaoDb: Session = Depends(pegarSessao),
    usuario: Usuario = Depends(verificarTokenSindico)
):

    usuario.verificaCondominio(body.idCodominio)

    servico = sessaoDb.query(Servicos).filter(Servicos.id == idServico).first()

    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    dados = body.model_dump(exclude_unset=True, exclude_none=True)

    for campo, valor in dados.items():
        if valor not in listaDeValoresInvalidos:
            setattr(servico, campo, valor)

    sessaoDb.commit()
    sessaoDb.refresh(servico)

    return {
        "Mensagem": "Serviço atualizado com sucesso!",
        "Servico": servico
    }

@sindico_router.get("/servico")
async def listarServicos(
    idCondominio: int,
    apartamento: str | None = None,
    torre: str | None = None,
    empresa: str | None = None,
    idAmbiente: int | None = None,
    idUsuario: int | None = None,
    status: str | None = None,
    dataInicio: date | None = None,
    dataFim: date | None = None,
    sessaoDb: Session = Depends(pegarSessao),
    usuario: Usuario = Depends(verificarTokenSindico)
):
    # Verifica se o usuário é síndico do condomínio
    if not usuario.verificaCondominio(idCondominio):
        raise HTTPException(status_code=400, detail="Não é síndico deste condomínio")

    query = sessaoDb.query(Servicos).filter(Servicos.idCodominio == idCondominio)

    # Aplicando filtros opcionais
    if apartamento:
        query = query.filter(Servicos.apartamento.ilike(f"%{apartamento}%"))
    
    if torre:
        query = query.filter(Servicos.torre.ilike(f"%{torre}%"))
    
    if empresa:
        query = query.filter(Servicos.empresa.ilike(f"%{empresa}%"))
    
    if idAmbiente:
        query = query.filter(Servicos.idAmbiente == idAmbiente)
    
    if status:
        query = query.filter(Servicos.status == status)
    
    if dataInicio:
        query = query.filter(Servicos.dataInicio >= dataInicio)
    
    if dataFim:
        query = query.filter(Servicos.dataFim <= dataFim)

    # Ordenação por mais recente
    query = query.order_by(Servicos.id.desc())

    resultados = query.all()

    return {
        "qtd": len(resultados),
        "servicos": resultados
    }
    
####################### ENCOMENDAS ##############################   


    
    
    
    

