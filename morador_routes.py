from fastapi import APIRouter
from schemas import UsuarioSchema,ReservaSchema
from dependeces import pegarSessao, verificarToken
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import Condominio, Usuario, MoradorCondominio, ReservaAmbiente, AmbientesCondominio

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