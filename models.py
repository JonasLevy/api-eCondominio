from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey, DateTime, func, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

db= create_engine("sqlite:///banco.db")

Base = declarative_base()

class Usuario(Base):
    __tablename__  = "usuarios"
    
    id= Column("id", Integer, autoincrement=True, primary_key=True)
    nome= Column("nome", String, nullable=False)
    email=Column("email", String, nullable=False)
    senha= Column("senha", String, nullable=False)
    ativo= Column("ativo", Boolean, default=True)
    tipo=Column("tipo", String, nullable=False)
    
    def __init__(self, nome, email, senha, tipo):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.tipo = tipo

class Condominio(Base):
    __tablename__ = "condominios"
    
    id = Column("id", Integer, autoincrement=True, primary_key=True)
    nome = Column("nome", String, nullable=False)
    endereco= Column("endereco", String, nullable=False)
    moradores = relationship("MoradorCondominio" , cascade="all, delete")
    
    def __init__(self,nome,endereco):
        self.nome = nome
        self.endereco = endereco

class SindicoCondominio(Base):
    __tablename__ = "sindico_condominio"
    
    id = Column("id", Integer, autoincrement=True, primary_key=True)
    idCondominio = Column("id_condominio", ForeignKey("condominios.id"))
    idUsuario = Column("id_usuario", ForeignKey("usuarios.id"))
    dataCriacao = Column( DateTime, 
        server_default=func.now(),  # usa a hora atual do banco
        nullable=False)
    condominios = relationship("Condominio" , cascade="all, delete")

    def __init__(self, idCondominio, idUsuario):
        self.idCondominio = idCondominio
        self.idUsuario= idUsuario
        
class AmbientesCondominio(Base):
    __tablename__ = "ambientes_condominio"
    
    id = Column("id", Integer, autoincrement=True, primary_key=True)
    nome = Column("nome", String, nullable=False)
    idCondominio = Column("id_condominio", ForeignKey("condominios.id"))
    
    def __init__(self, idCondominio, nome):
        self.idCondominio = idCondominio
        self.nome = nome
        
class MoradorCondominio(Base):
    __tablename__ = "morador_condominio"
    
    id = Column("id", Integer, autoincrement=True, primary_key=True)
    idCondominio = Column("id_condominio", ForeignKey("condominios.id"))
    idMorador = Column("id_morador", ForeignKey("usuarios.id"))
    
    def __init__(self, idCondominio, idMorador):
        self.idCondominio = idCondominio 
        self.idMorador = idMorador 