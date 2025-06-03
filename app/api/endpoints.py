from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List

from app.db.session import get_db
from app.schemas.schemas import Implant
from app.db import models

router = APIRouter()

@router.get("/implants", response_model=List[Implant])
def get_implants(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Retorna a lista de implantes cadastrados no sistema.
    """
    implants = db.query(models.Implant).offset(skip).limit(limit).all()
    return implants

@router.get("/implants/{implant_id}", response_model=Implant)
def get_implant(
    implant_id: int, 
    db: Session = Depends(get_db)
):
    """
    Retorna os detalhes de um implante específico.
    """
    implant = db.query(models.Implant).filter(models.Implant.id == implant_id).first()
    if not implant:
        raise HTTPException(status_code=404, detail="Implante não encontrado")
    return implant

@router.get("/healthcheck")
def healthcheck(db: Session = Depends(get_db)):
    """
    Verifica a saúde da aplicação, incluindo a conexão com o banco de dados.
    """
    try:
        # Tenta executar uma query simples para verificar a conexão com o BD
        db.execute("SELECT 1")
        db_status = "ok"
    except SQLAlchemyError:
        db_status = "error"
        # Você pode logar o erro aqui para depuração
        raise HTTPException(status_code=503, detail="Database connection error")
    
    return {"status": "ok", "database_status": db_status, "version": "2.0.0"}
