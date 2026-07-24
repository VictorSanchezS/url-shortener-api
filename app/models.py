from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    codigo_corto = Column(String(10), unique=True, index=True, nullable=False)
    url_original = Column(String(2048), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    clics_totales = Column(Integer, default=0)

    clics = relationship("Clic", back_populates="url", cascade="all, delete-orphan")


class Clic(Base):
    __tablename__ = "clics"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    ip_hash = Column(String(64), nullable=True)
    user_agent = Column(String(255), nullable=True)
    referrer = Column(String(2048), nullable=True)

    url = relationship("URL", back_populates="clics")