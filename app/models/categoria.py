# Tabela de categoria
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)
    ativo = Column(Boolean, default=True)

    #Relacionamento com a tabela de produtos
    #Lazy "selectin" - Carrega os produtos apenas quando nescessário.
    produtos = relationship("Produto", back_populates="categoria", lazy="selectin")