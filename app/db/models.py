from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.db.session import Base

class Implant(Base):
    __tablename__ = "implants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    manufacturer = Column(String(255), nullable=False)
    image_path = Column(String(255))
    image_url = Column(String(255))
    vector = Column(Vector(512))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Implant(id={self.id}, name='{self.name}', manufacturer='{self.manufacturer}')>"


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(String(255), nullable=False, index=True)
    client_id = Column(String(255), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_url = Column(String(255), nullable=False)
    vector = Column(Vector(512))
    metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<Image(id={self.id}, submission_id='{self.submission_id}', client_id='{self.client_id}')>"


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(String(255), nullable=False, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    implant_id = Column(Integer, ForeignKey("implants.id"), nullable=False)
    similarity = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Result(id={self.id}, image_id={self.image_id}, implant_id={self.implant_id}, similarity={self.similarity})>"
