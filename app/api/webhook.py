from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Header, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import requests
import logging

from app.db.session import get_db
from app.schemas.schemas import WebhookRequest, WebhookResponse, Implant
from app.services.clip_service import clip_service
from app.db import models

router = APIRouter()
logger = logging.getLogger("webhook_router")

@router.post("/webhook", response_model=WebhookResponse)
async def webhook(
    request: WebhookRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para receber webhooks do Jotform com imagens de raio-X para processamento.
    """
    logger.info(f"Recebido webhook para cliente {request.client_id}")
    
    try:
        # Baixar imagem da URL
        response = requests.get(request.image_url)
        if response.status_code != 200:
            logger.error(f"Erro ao baixar imagem da URL: {response.status_code}")
            return WebhookResponse(
                success=False,
                message="Não foi possível baixar a imagem da URL fornecida"
            )
        
        image_data = response.content
        
        # Fazer upload para DigitalOcean Spaces
        object_name = f"uploads/{request.client_id}/{request.image_url.split('/')[-1]}"
        spaces_url = clip_service.upload_to_spaces(io.BytesIO(image_data), object_name)
        
        # Processar imagem com CLIP
        vector = clip_service.process_image(image_data)
        
        # Salvar imagem no banco de dados
        db_image = models.Image(
            submission_id=f"webhook_{request.client_id}_{object_name.split('/')[-1]}",
            client_id=request.client_id,
            file_name=object_name.split('/')[-1],
            file_path=object_name,
            file_url=spaces_url,
            vector=vector
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        # Encontrar implantes similares
        similar_implants = clip_service.find_similar_implants(vector, db)
        
        # Salvar resultados no banco de dados
        for rank, implant in enumerate(similar_implants, 1):
            result = models.Result(
                submission_id=db_image.submission_id,
                image_id=db_image.id,
                implant_id=implant["id"],
                similarity=implant["similarity"],
                rank=rank
            )
            db.add(result)
        
        db.commit()
        
        logger.info(f"Processamento concluído para cliente {request.client_id}")
        return WebhookResponse(
            success=True,
            message="Imagem processada com sucesso",
            results=similar_implants
        )
    
    except Exception as e:
        logger.error(f"Erro no processamento do webhook: {str(e)}")
        db.rollback()
        return WebhookResponse(
            success=False,
            message=f"Erro no processamento: {str(e)}"
        )

@router.post("/upload", response_model=WebhookResponse)
async def upload_image(
    file: UploadFile = File(...),
    client_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Endpoint para upload direto de imagens de raio-X para processamento.
    """
    if not client_id:
        raise HTTPException(status_code=400, detail="Header client_id é obrigatório")
    
    logger.info(f"Recebido upload de imagem para cliente {client_id}")
    
    try:
        # Ler conteúdo do arquivo
        image_data = await file.read()
        
        # Fazer upload para DigitalOcean Spaces
        object_name = f"uploads/{client_id}/{file.filename}"
        spaces_url = clip_service.upload_to_spaces(io.BytesIO(image_data), object_name)
        
        # Processar imagem com CLIP
        vector = clip_service.process_image(image_data)
        
        # Salvar imagem no banco de dados
        db_image = models.Image(
            submission_id=f"upload_{client_id}_{file.filename}",
            client_id=client_id,
            file_name=file.filename,
            file_path=object_name,
            file_url=spaces_url,
            vector=vector
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        # Encontrar implantes similares
        similar_implants = clip_service.find_similar_implants(vector, db)
        
        # Salvar resultados no banco de dados
        for rank, implant in enumerate(similar_implants, 1):
            result = models.Result(
                submission_id=db_image.submission_id,
                image_id=db_image.id,
                implant_id=implant["id"],
                similarity=implant["similarity"],
                rank=rank
            )
            db.add(result)
        
        db.commit()
        
        logger.info(f"Processamento concluído para cliente {client_id}")
        return WebhookResponse(
            success=True,
            message="Imagem processada com sucesso",
            results=similar_implants
        )
    
    except Exception as e:
        logger.error(f"Erro no processamento do upload: {str(e)}")
        db.rollback()
        return WebhookResponse(
            success=False,
            message=f"Erro no processamento: {str(e)}"
        )
