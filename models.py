from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey, DateTime, func, ForeignKey, Date, Time
from sqlalchemy.orm import declarative_base, relationship

db= create_engine("sqlite:///banco.db")

Base = declarative_base()

class Status(Base):
    __tablename__ = "status"
    
    id= Column("id", Integer, autoincrement=True, primary_key=True)
    nome= Column("nome", String, nullable=False)
    tabela = Column("tabela", String, nullable=False)
    
    def __init__(self, nome):
        self.nome = nome

class Usuario(Base):
    __tablename__  = "usuarios"
    
    id= Column("id", Integer, autoincrement=True, primary_key=True)
    nome= Column("nome", String, nullable=False)
    email=Column("email", String, nullable=False)
    senha= Column("senha", String, nullable=False)
    ativo= Column("ativo", Boolean, default=True)
    tipo=Column("tipo", String, nullable=False)
    telefone=Column("telefone", String, nullable=True)
    cpf=Column("cpf", String, nullable=True)
    condominiosMorador= relationship("MoradorCondominio", cascade="all, delete")
    sindicoCondominio= relationship("SindicoCondominio", cascade="all, delete")
    
    
    def __init__(self, nome, cpf, telefone, email, senha, tipo):
        self.nome = nome
        self.telefone = telefone
        self.cpf = cpf
        self.email = email
        self.senha = senha
        self.tipo = tipo

class Condominio(Base):
    __tablename__ = "condominios"
    
    id = Column("id", Integer, autoincrement=True, primary_key=True)
    nome = Column("nome", String, nullable=False)
    endereco= Column("endereco", String, nullable=False)
    moradores = relationship("MoradorCondominio" , cascade="all, delete")
    ambientes = relationship("AmbientesCondominio", cascade="all, delete")
    
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
    info = Column("info", String, nullable= True)
    idCondominio = Column("id_condominio", ForeignKey("condominios.id"))
    
    def __init__(self, idCondominio, nome, info):
        self.idCondominio = idCondominio
        self.nome = nome
        self.info = info
        
class MoradorCondominio(Base):
    __tablename__ = "morador_condominio"
    
    id = Column("id", Integer, autoincrement=True, primary_key=True)
    idCondominio = Column("id_condominio", ForeignKey("condominios.id"))
    idMorador = Column("id_morador", ForeignKey("usuarios.id"))
    apartamento = Column("apartamento", String, nullable=True)
    torre = Column("torre", String, nullable=True)
    
    def __init__(self, idCondominio, idMorador, apartamento, torre):
        self.idCondominio = idCondominio 
        self.idMorador = idMorador 
        self.apartamento = apartamento
        self.torre = torre  
        
class ReservaAmbiente(Base):
    __tablename__ = "reserva_ambiente"
    
    id = Column("id", Integer, autoincrement=True, primary_key=True)
    idAmbiente = Column("id_ambiente", ForeignKey("ambientes_condominio.id"))
    idMorador = Column("id_morador", ForeignKey("usuarios.id"))
    idCondominio = Column("id_condominio", ForeignKey("condominios.id"))
    dataReserva = Column("data_reserva", Date, nullable=False)
    horaInicio = Column("hora_inicio", Time, nullable=False)
    horaFim = Column("hora_fim", Time, nullable=False)
    info = Column("info", String, nullable=True)
    status = Column("status", String, default="pendente")
    
    def __init__(self, idAmbiente, idMorador, dataReserva, horaInicio, horaFim, idCondominio, info):
        self.idCondominio = idCondominio
        self.idAmbiente = idAmbiente
        self.idMorador = idMorador
        self.dataReserva = dataReserva
        self.horaInicio = horaInicio
        self.horaFim = horaFim
        self.info = info