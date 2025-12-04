from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey, DateTime, func, ForeignKey, Date, Time
from sqlalchemy.orm import declarative_base, relationship
from fastapi import HTTPException

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
    moradorCondominio = relationship("MoradorCondominio", back_populates="usuario")
    sindicoCondominio= relationship("SindicoCondominio", back_populates="sindicos")
    
    def verificaCondominio(self, idCondominio:int):
        
        sindico = any(
            item.idCondominio == idCondominio
            for item in self.sindicoCondominio
        )
        if not sindico:
            raise HTTPException(status_code=400, detail="Não é sindico deste Condominio.")
        else:
            return True
    
    
    def verificaCondominioMorador(self, idCondominio:int):
        
        morador = any(
            item.idCondominio == idCondominio
            for item in self.moradorCondominio
        )
        if not morador:
            raise HTTPException(status_code=400, detail="Não é morador deste Condominio.")
        else:
            return True
    
    
    
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
    moradores = relationship("MoradorCondominio" ,  back_populates="condominios")
    ambientes = relationship("AmbientesCondominio", back_populates="condominio")
    
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
    sindicos = relationship("Usuario" , back_populates="sindicoCondominio")

    def __init__(self, idCondominio, idUsuario):
        self.idCondominio = idCondominio
        self.idUsuario= idUsuario
        
class AmbientesCondominio(Base):
    __tablename__ = "ambientes_condominio"
    
    id = Column("id", Integer, autoincrement=True, primary_key=True)
    nome = Column("nome", String, nullable=False)
    info = Column("info", String, nullable= True)
    idCondominio = Column("id_condominio", ForeignKey("condominios.id"))
    condominio = relationship("Condominio", back_populates="ambientes")
    
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
    usuario = relationship("Usuario", back_populates="moradorCondominio")
    condominios = relationship("Condominio", back_populates="moradores")
    
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
        
class Pessoas(Base):
    __tablename__  = "pessoas"
    
    id= Column("id", Integer, autoincrement=True, primary_key=True)
    nome= Column("nome", String, nullable=False)
    ativo= Column("ativo", Boolean, default=False)
    telefone=Column("telefone", String, nullable=False)
    cpf=Column("cpf", String, nullable=False)    
    
    def __init__(self, nome, cpf, telefone):
        self.nome = nome
        self.telefone = telefone
        self.cpf = cpf

class Visitas(Base):
    __tablename__  = "visitas"
    
    id= Column("id", Integer, autoincrement=True, primary_key=True)
    idPessoa= Column("id_pessoa", ForeignKey("pessoas.id"))
    idMorador= Column("id_usuario",  ForeignKey("usuarios.id"))
    apartamento = Column("apto", String, nullable=False)
    idCodominio = Column("id_condominio", ForeignKey("condominios.id"))
    info = Column("info", String, nullable=False)
    dataDaVisita = Column("data_visita", Date, nullable=True)
    horaDaVisita = Column("hora_visita", Time, nullable=True)
    confirmado = Column("confirmado", String, default="false" )
    cancelado = Column("cancelado", String, default="false" )
    
    def __init__(self, idPessoa, idMorador, apartamento, idCodominio, info, dataDaVisita, horaDaVisita):
        self.idPessoa = idPessoa
        self.idMorador = idMorador
        self.apartamento = apartamento
        self.idCodominio = idCodominio
        self.info = info
        self.dataDaVisita = dataDaVisita
        self.horaDaVisita = horaDaVisita
        
class Servicos(Base):
    __tablename__="servicos"
    
    id= Column("id", Integer, autoincrement=True, primary_key=True)
    idUsuario= Column("id_usuario",  ForeignKey("usuarios.id"))
    idCodominio = Column("id_condominio", ForeignKey("condominios.id"))
    idAmbiente = Column("id_ambiente", ForeignKey("ambientes_condominio.id"), nullable=True)
    apartamento = Column("apto", String, nullable=True)
    torre = Column("torre", String, nullable=True)
    dataInicio = Column("data_inicio", Date, nullable=False)
    dataFim = Column("data_fim", Date, nullable=False)
    horaInicio = Column("hora_inicio", Time, nullable=False)
    horaFim = Column("hora_fim", Time, nullable=False)
    info = Column("info", String, nullable=True)
    status = Column("status", String, default="pendente")
    empresa = Column("empresa", String, nullable=True)
    aprovado = Column("aprovado", String, default="ok")
    prestadorServico = relationship("PrestadorServico", back_populates="servicos")
    
    def __init__(self, idUsuario, idCodominio, idAmbiente, apartamento, torre, dataInicio, dataFim, horaInicio, horaFim, info, empresa):
        self.idUsuario = idUsuario
        self.idCodominio = idCodominio
        self.idAmbiente = idAmbiente
        self.apartamento = apartamento
        self.torre = torre
        self.dataInicio = dataInicio
        self.dataFim = dataFim
        self.horaInicio = horaInicio
        self.horaFim = horaFim
        self.info = info
        self.empresa = empresa
    
class PrestadorServico(Base):
    __tablename__  = "prestador_servico"
    
    id= Column("id", Integer, autoincrement=True, primary_key=True)
    idPessoa= Column("id_pessoa", ForeignKey("pessoas.id"))
    idServico= Column("id_servico", ForeignKey("servicos.id"))
    servicos= relationship("Servicos", back_populates="prestadorServico")
    
    def __init__(self, idPessoa, idServico):
        self.idPessoa = idPessoa    
        self.idServico = idServico    
    
    
    
