# models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

class EmpresaCliente(Base):
    __tablename__ = "empresacliente"

    idEmpresaCliente = Column(Integer, primary_key = True, autoincrement = True)
    nome = Column(String)
    cnpj = Column(Integer)
    contato = Column(Integer)

    chats = relationship("chat", back_populates = "owner")

class Chat(Base):
    __tablename__ = "chat"

    idChat = Column(Integer, primary_key = True, autoincrement = True)
    idEmpresaCliente = Column(Integer, ForeignKey("empresacliente.idEmpresaCliente"))

class Historico(Base):
    __tablename__ = "historico"

    idHistorico = Column(Integer, primary_key = True, autoincrement = True)
    numero = Column(String, nullable = False)
    mensagem = Column(String, nullable = False)
    tag = Column(String)
    data = Column(String, nullable = False)
    hora = Column(String, nullable = False)
    nome = Column(String, nullable = False)
    
    