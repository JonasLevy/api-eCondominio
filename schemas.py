from pydantic import BaseModel
from typing import Optional

class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: Optional[bool]
    
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
    class Config:
        from_attributes = True