## Manejo de base de datos
from sqlalchemy import create_engine, Column, String, Date, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker, Session


class Base(DeclarativeBase):
    pass

class ErrorEntry(Base):
    __tablename__ = 'functional_error_test'
    id = Column(Integer, primary_key=True)
    status = Column(String)
    title = Column(String)
    pasos_reproducir = Column(String)
    mensaje_error = Column(String)
    resultados_esperados = Column(String)
    resultados_obtenidos = Column(String)
    error_date = Column(Date)