from fastapi import APIRouter
from schemas import UsuarioSchema,ReservaSchema, VisitaSchema
from dependeces import pegarSessao, verificarToken
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import Condominio, Usuario, MoradorCondominio, ReservaAmbiente, AmbientesCondominio, Visitas, Pessoas

morador_router = APIRouter(prefix="/morador", tags=["Morador"], dependencies=[Depends(verificarToken)])

@morador_router.post("/fazerreservas/{idCondominio}")
async def fazerReserva(body:ReservaSchema, idCondominio:int, usuario:Usuario=Depends(verificarToken), sessionDb:Session=Depends(pegarSessao)):
    
    moradorCondominio = sessionDb.query(MoradorCondominio).filter(MoradorCondominio.idCondominio == idCondominio, MoradorCondominio.idMorador == usuario.id).first()
    
    if not moradorCondominio:
        raise HTTPException(status_code=400, detail="Não é Morador deste Condominio")
    
    verificaAmbiente = sessionDb.query(AmbientesCondominio).filter(AmbientesCondominio.id == body.idAmbiente, AmbientesCondominio.idCondominio == idCondominio).first()
    if not verificaAmbiente:
        raise HTTPException(status_code=400, detail="Ambiente não cadastrado neste condominio")
    
    verificarDataReserva = sessionDb.query(ReservaAmbiente).filter(ReservaAmbiente.dataReserva == body.dataReserva, ReservaAmbiente.idAmbiente == body.idAmbiente).first()
    if verificarDataReserva:
        raise HTTPException(status_code=400, detail="Já existe uma reserva para este ambiente nesta data")  
    
    reserva = ReservaAmbiente(
        body.idAmbiente,
        usuario.id,
        body.dataReserva,
        body.horaInicio,
        body.horaFim,
        idCondominio,
        body.info)
    sessionDb.add(reserva)
    sessionDb.commit()
    
    return {"mensagem": "Reserva criada com sucesso!",
            "Ambiente:": verificaAmbiente.nome,
            "Data da Reserva:": reserva.dataReserva,
            "Hora Início:": reserva.horaInicio,
            "Hora Fim:": reserva.horaFim}
    
@morador_router.post("/criarvisita")
async def criarVisita(body: VisitaSchema, sessaoDb:Session=Depends(pegarSessao), usuario:Usuario=Depends(verificarToken)):
    
    moradorDoCondominio = sessaoDb.query(MoradorCondominio).filter(MoradorCondominio.idCondominio==body.idCodominio, MoradorCondominio.idMorador == usuario.id).first()
    
    if not moradorDoCondominio:
        raise HTTPException(status_code=400, detail="Não é morador deste Condominio")
    
    verificaPessoa = sessaoDb.query(Pessoas).filter(Pessoas.cpf == body.cpf).first()
    
    if verificaPessoa:
        visita = Visitas(verificaPessoa.id, usuario.id, moradorDoCondominio.apartamento, moradorDoCondominio.idCondominio, body.info, body.dataVisita, body.horaVisita)
        sessaoDb.add(visita)
        sessaoDb.commit()
        
        return {"mensagem":"Visita criada",
            "nome": verificaPessoa.nome,
            "condominio": visita.idCodominio,
            "apto":visita.apartamento}
    
    pessoa = Pessoas(body.nome, body.cpf, body.telefone)
    sessaoDb.add(pessoa)
    sessaoDb.flush()
    visita = Visitas(pessoa.id, usuario.id, moradorDoCondominio.apartamento, moradorDoCondominio.idCondominio, body.info, body.dataVisita, body.horaVisita)
    sessaoDb.add(visita)
    sessaoDb.commit()
    sessaoDb.refresh(visita)
    
    return{
        "Nome": pessoa.nome,
        "apto": visita.apartamento,
        "Condominio": visita.idCodominio,
        "data": visita.dataDaVisita,
        "hora": visita.horaDaVisita
    }