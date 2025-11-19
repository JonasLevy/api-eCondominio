from pydantic import BaseModel
from typing import Optional

class UsuarioSchema(BaseModel):
    nome: str
    telefone: str
    email: str
    cpf: str
    
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
    idCondominio: int
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
        