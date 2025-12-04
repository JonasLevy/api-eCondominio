from fastapi import APIRouter
from schemas import ReservaSchema, VisitaSchema, VisitaEditarSchema, ServicoSchema, ServicoEditarSchema, PrestadorServicoSchema
from dependeces import pegarSessao, verificarToken
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import Condominio, Usuario, MoradorCondominio, ReservaAmbiente, AmbientesCondominio, Visitas, Pessoas, Servicos, PrestadorServico

morador_router = APIRouter(prefix="/morador", tags=["Morador"], dependencies=[Depends(verificarToken)])


####################### RESERVAS DE AMBIENTE ##############################
@morador_router.post("/reservas/{idCondominio}")
async def fazerReserva(body: ReservaSchema, idCondominio: int, usuario: Usuario = Depends(verificarToken), sessionDb: Session = Depends(pegarSessao)):
    """Cria uma reserva de ambiente para o morador logado."""
    moradorCondominio = sessionDb.query(MoradorCondominio).filter(
        MoradorCondominio.idCondominio == idCondominio,
        MoradorCondominio.idMorador == usuario.id
    ).first()

    if not moradorCondominio:
        raise HTTPException(status_code=400, detail="Não é Morador deste Condominio")

    verificaAmbiente = sessionDb.query(AmbientesCondominio).filter(
        AmbientesCondominio.id == body.idAmbiente,
        AmbientesCondominio.idCondominio == idCondominio
    ).first()
    if not verificaAmbiente:
        raise HTTPException(status_code=400, detail="Ambiente não cadastrado neste condominio")

    verificarDataReserva = sessionDb.query(ReservaAmbiente).filter(
        ReservaAmbiente.dataReserva == body.dataReserva,
        ReservaAmbiente.idAmbiente == body.idAmbiente
    ).first()
    if verificarDataReserva:
        raise HTTPException(status_code=400, detail="Já existe uma reserva para este ambiente nesta data")

    reserva = ReservaAmbiente(
        body.idAmbiente,
        usuario.id,
        body.dataReserva,
        body.horaInicio,
        body.horaFim,
        idCondominio,
        body.info
    )
    sessionDb.add(reserva)
    sessionDb.commit()

    return {
        "mensagem": "Reserva criada com sucesso!",
        "ambiente": verificaAmbiente.nome,
        "data_reserva": reserva.dataReserva,
        "hora_inicio": reserva.horaInicio,
        "hora_fim": reserva.horaFim
    }

@morador_router.patch("/reservas/{idReserva}")
async def editarReserva(idReserva:int, body: ReservaSchema, usuario:Usuario=Depends(verificarToken), sessaoDb:Session=Depends(pegarSessao)):
    """Edita uma reserva existente do morador logado."""
    reserva = sessaoDb.query(ReservaAmbiente).filter(ReservaAmbiente.id == idReserva).first()
    
    usuario.verificaCondominioMorador(reserva.idCondominio)
    
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    if reserva.idMorador != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para editar esta reserva")
    
    
    dados = body.model_dump(exclude_unset=True, exclude_none=True)
    for chave, valor in dados.items():
        setattr(reserva, chave, valor)
    
    sessaoDb.commit()
    sessaoDb.refresh(reserva)
    
    return {"mensagem":"Reserva atualizada com sucesso",
            "reserva": reserva}

@morador_router.get("/reservas/{idCondominio}")
async def listarReservas(idCondominio:int, usuario:Usuario=Depends(verificarToken), sessaoDb:Session=Depends(pegarSessao)):
    """Lista todas as reservas do morador logado em um condomínio específico."""
    usuario.verificaCondominioMorador(idCondominio)
    
    reservas_rows = (
        sessaoDb.query(
            ReservaAmbiente.id,
            ReservaAmbiente.dataReserva,
            ReservaAmbiente.horaInicio,
            ReservaAmbiente.horaFim,
            ReservaAmbiente.status,
            ReservaAmbiente.info,
            AmbientesCondominio.nome.label("ambienteNome")
        )
        .join(AmbientesCondominio, ReservaAmbiente.idAmbiente == AmbientesCondominio.id)
        .filter(
            ReservaAmbiente.idMorador == usuario.id,
            ReservaAmbiente.idCondominio == idCondominio
        )
        .all()
    )
    
    reservas = [row._asdict() for row in reservas_rows]
    
    return {"reservas": reservas}

####################### VISITAS ##############################
@morador_router.post("/visitas")
async def criarVisita(body: VisitaSchema, sessaoDb: Session = Depends(pegarSessao), usuario: Usuario = Depends(verificarToken)):
    """Cria um registro de visita (cria pessoa se não existir)."""
    moradorDoCondominio = sessaoDb.query(MoradorCondominio).filter(
        MoradorCondominio.idCondominio == body.idCodominio,
        MoradorCondominio.idMorador == usuario.id
    ).first()

    if not moradorDoCondominio:
        raise HTTPException(status_code=400, detail="Não é morador deste Condominio")

    verificaPessoa = sessaoDb.query(Pessoas).filter(Pessoas.cpf == body.cpf).first()

    if verificaPessoa:
        visita = Visitas(
            verificaPessoa.id,
            usuario.id,
            moradorDoCondominio.apartamento,
            moradorDoCondominio.idCondominio,
            body.info,
            body.dataVisita,
            body.horaVisita
        )
        sessaoDb.add(visita)
        sessaoDb.commit()

        return {
            "mensagem": "Visita criada",
            "nome": verificaPessoa.nome,
            "condominio": visita.idCodominio,
            "apto": visita.apartamento
        }

    pessoa = Pessoas(body.nome, body.cpf, body.telefone)
    sessaoDb.add(pessoa)
    sessaoDb.flush()
    
    visita = Visitas(
        pessoa.id,
        usuario.id,
        moradorDoCondominio.apartamento,
        moradorDoCondominio.idCondominio,
        body.info,
        body.dataVisita,
        body.horaVisita
    )
    sessaoDb.add(visita)
    sessaoDb.commit()
    sessaoDb.refresh(visita)

    return {
        "mensagem": "Visita criada com sucesso",
        "nome": pessoa.nome,
        "apto": visita.apartamento,
        "condominio": visita.idCodominio,
        "data": visita.dataDaVisita,
        "hora": visita.horaDaVisita
    }

@morador_router.patch("/visita/{idVisita}")
async def editarVisita(idVisita:int, body: VisitaEditarSchema, sessaoDb:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarToken)):
    
    visita = sessaoDb.query(Visitas).filter(Visitas.id == idVisita).first()
    
    if not visita:
        raise HTTPException(status_code=404, detail="Visita não encontrada")
    
    usuario.verificaCondominioMorador(visita.idCodominio)
    
    pessoa = sessaoDb.query(Pessoas).filter(Pessoas.id == visita.idPessoa).first()
    
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    
    dados = body.model_dump(exclude_unset=True, exclude_none=True)
    for chave, valor in dados.items():
        if chave in ["nome", "telefone", "cpf"]:
            setattr(pessoa, chave, valor)
        else:
            setattr(visita, chave, valor)
    
    sessaoDb.commit()
    sessaoDb.refresh(visita)
    
    return {"mensagem":"Visita atualizada com sucesso",
            "visita": visita}

@morador_router.get("/visitas/{idCodominio}")
async def listarVisitas(idCodominio:int, nome:str | None=None, usuario: Usuario = Depends(verificarToken), sessaoDb: Session = Depends(pegarSessao)):
    
    usuario.verificaCondominioMorador(idCodominio)
    
    visitas_rows = (
        sessaoDb.query(
            Visitas.apartamento, Visitas.idCodominio, Visitas.info, Visitas.dataDaVisita,
            Visitas.horaDaVisita, Visitas.id.label("idVisita"), Pessoas.nome, Pessoas.telefone, Pessoas.cpf
        )
        .join(Pessoas, Visitas.idPessoa == Pessoas.id)
        .filter(Visitas.idMorador == usuario.id)
        .all()
    )
    
    if nome:
        visitas_rows = [row for row in visitas_rows if nome.lower() in row.nome.lower()]
        return {"visitas": [row._asdict() for row in visitas_rows]}
    
    visitas = [row._asdict() for row in visitas_rows]

    return {"visitas": visitas}

####################### SERVICO ##############################
@morador_router.post("/servico")
async def solicitarServico(body: ServicoSchema, sessaoDb: Session = Depends(pegarSessao), usuario: Usuario = Depends(verificarToken)):
    """Solicita um serviço para o morador logado. 
        Ambiete e info podem ser nulos."""    
    usuario.verificaCondominioMorador(body.idCodominio)
    moradorDoCondominio = sessaoDb.query(MoradorCondominio).filter(
        MoradorCondominio.idCondominio == body.idCodominio,
        MoradorCondominio.idMorador == usuario.id
    ).first()

    servico = Servicos(
        usuario.id,
        body.idCodominio,
        body.idAmbiente,
        moradorDoCondominio.apartamento,
        moradorDoCondominio.torre,
        body.dataInicio,
        body.dataFim,
        body.horaInicio,
        body.horaFim,
        body.info,
        body.empresa
    )
    sessaoDb.add(servico)
    sessaoDb.commit()
    sessaoDb.refresh(servico)

    return {
        "mensagem": "Serviço solicitado com sucesso",
        "servico": servico
    }
    
@morador_router.patch("/servico/{idServico}")
async def editarServico(idServico:int, body: ServicoEditarSchema, sessaoDb:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarToken)):
    """Edita um serviço existente do morador logado.
        Você pode enviar só os campos que deseja alterar."""
    servico = sessaoDb.query(Servicos).filter(Servicos.id == idServico).first()
    usuario.verificaCondominioMorador(servico.idCodominio)
    
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
        
    dados = body.model_dump(exclude_unset=True, exclude_none=True)
    for chave, valor in dados.items():
        setattr(servico, chave, valor)
    
    sessaoDb.commit()
    sessaoDb.refresh(servico)
    
    return {"mensagem":"Serviço atualizado com sucesso",
            "servico": servico}
    
@morador_router.get("/servicos/{idCodominio}")
async def listarServicos(idCodominio:int, usuario:Usuario=Depends(verificarToken), sessaoDb:Session=Depends(pegarSessao)):
    """Lista todos os serviços do morador logado em um condomínio específico."""
    usuario.verificaCondominioMorador(idCodominio)
    
    servicos_rows = (
        sessaoDb.query(Servicos).filter(
            Servicos.idUsuario == usuario.id,
            Servicos.idCodominio == idCodominio
        )
        .all()
    )
    
  
    
    return {"servicos": servicos_rows}

####################### PRESTADOR DE SERVICO ##############################
@morador_router.post("/prestadorservico")
async def cadastrarPrestadorServico(body: PrestadorServicoSchema, sessaoDb: Session = Depends(pegarSessao), usuario: Usuario = Depends(verificarToken)):
    """Cadastra um prestador de serviço para o morador logado."""
    usuario.verificaCondominioMorador(body.idCodominio)
    
    verificaPessoa = sessaoDb.query(Pessoas).filter(Pessoas.cpf == body.cpf).first()

    if verificaPessoa:
        prestadorServico = PrestadorServico(
            verificaPessoa.id,
            body.idServico
        )
        sessaoDb.add(prestadorServico)
        sessaoDb.commit()

        return {
            "mensagem": "Prestador de serviço cadastrado",
            "nome": verificaPessoa.nome,
            "idServico": prestadorServico.idServico
        }

    pessoa = Pessoas(body.nome, body.cpf, body.telefone)
    sessaoDb.add(pessoa)
    sessaoDb.flush()
    
    prestadorServico = PrestadorServico(
        pessoa.id,
        body.idServico
    )
    sessaoDb.add(prestadorServico)
    sessaoDb.commit()
    sessaoDb.refresh(prestadorServico)

    return {
        "mensagem": "Prestador de serviço cadastrado com sucesso",
        "nome": pessoa.nome,
        "idServico": prestadorServico.idServico
    }