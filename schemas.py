from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class UsuarioSchema(BaseModel):
    nome: str
    telefone: str
    email: str
    cpf: str
    senha:str
    
    class Config:
        from_attributes = True

        
class CondominiosSchema(BaseModel):
    nome: str
    endereco: str
    class Config:
        from_attributes = True
    
class SindicoCondominio(BaseModel):
    idCondominio: int
    idUsuaio: int
    class Config:
        from_attributes = True
        
class LoginSchema(BaseModel):
    email: str
    senha: str
    class Config:
        from_attributes = True
        
class AmbienteCondominioSchema(BaseModel):
    nome: str
    info: Optional[str] = None
    idCondominio: int
    class Config:
        from_attributes = True

class AmbienteCondominioEditarSchema(BaseModel):
    nome: Optional[str] = None
    info: Optional[str] = None
    class Config:
        from_attributes = True
        
class MoradorCondominioSchema(BaseModel):
    idCondominio: int
    idMorador: int
    apartamento: str
    torre:str
    class Config:
        from_attributes = True
        
class CriarMoradorSchema(BaseModel):
    nome: str
    email: str
    senha: str
    cpf:str
    telefone:str
    idCondominio: int
    apartamento: str
    torre:str
    class Config:
        from_attributes = True
    
class EditarMoradorSchema(BaseModel):
    idCondominio: int
    nome: str | None = None
    email: str | None = None
    senha: str | None = None
    cpf:str | None = None
    telefone:str | None = None
    apartamento: str | None = None
    torre:str | None = None
    class Config:
        from_attributes = True
        
class ReservaSchema(BaseModel):
    idAmbiente: int
    dataReserva: date
    horaInicio: time
    horaFim: time
    status: str
    info: Optional[str] = None
    
    class Config:
        from_attributes = True
        
class EditarReservaSchema(BaseModel):
    idAmbiente: int | None = None
    dataReserva: date | None = None
    horaInicio: time | None = None
    horaFim: time | None = None
    status: str | None = None
    info: str | None = None
    
    class Config:
        from_attributes = True

        
class AlterarStatus(BaseModel):
    status: str
    info: str
    
    class Config:
        from_attributes = True
        
class VisitaSchema(BaseModel):
    nome: str
    telefone: str
    cpf: str
    idMorador: int
    idCodominio: int
    info: str
    dataVisita: date
    horaVisita: time 
    
    class Config:
        from_attributes = True    

class ServicoSchema(BaseModel):
    idUsuario : int
    idCodominio : int
    idAmbiente : int
    apartamento : str
    torre :str
    empresa : str
    dataInicio : date
    dataFim : date
    horaInicio : time
    horaFim :time
    info : str
    status : str
    class Config:
        from_attributes = True

class PrestadorServicoSchema(BaseModel):
    nome:Optional[str] = None
    cpf:Optional[str] = None
    telefone: Optional[str] = None
    idPessoa: Optional[str] = None
    idServico: int
    class Config:
        from_attributes = True
        
class ServicoEditarSchema(BaseModel):
    idAmbiente: int | None = None
    apartamento: str | None = None
    torre: str | None = None
    empresa: str | None = None
    dataInicio: date | None = None
    dataFim: date | None = None
    horaInicio: time | None = None
    horaFim: time | None = None
    info: str | None = None
    status: str | None = None

    class Config:
        from_attributes = True

class EncomendaSchema(BaseModel):
    idCodominio: int
    info: str
    tipo: str
    entregue: str
    class Config:
        from_attributes = True
       