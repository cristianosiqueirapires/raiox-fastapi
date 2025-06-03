import os
import io
import json
import logging
import numpy as np
import torch
from PIL import Image
import clip
from typing import List, Optional, Tuple
import boto3
from botocore.exceptions import NoCredentialsError

from app.core.config import settings

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("clip_service")

class ClipService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Inicializando serviço CLIP no dispositivo: {self.device}")
        
        # Carregar modelo CLIP
        self.model, self.preprocess = clip.load(settings.CLIP_MODEL, device=self.device)
        logger.info(f"Modelo CLIP carregado: {settings.CLIP_MODEL}")
        
        # Configurar cliente S3 para DigitalOcean Spaces
        self.s3_client = boto3.client(
            's3',
            region_name=settings.DO_SPACES_REGION,
            endpoint_url=settings.DO_SPACES_ENDPOINT,
            aws_access_key_id=settings.DO_SPACES_KEY,
            aws_secret_access_key=settings.DO_SPACES_SECRET
        )
        logger.info(f"Cliente S3 configurado para bucket: {settings.DO_SPACES_BUCKET}")
    
    def process_image(self, image_data: bytes) -> np.ndarray:
        """
        Processa uma imagem e gera um vetor CLIP.
        
        Args:
            image_data: Dados binários da imagem
            
        Returns:
            np.ndarray: Vetor CLIP normalizado (512 dimensões)
        """
        try:
            # Abrir imagem
            image = Image.open(io.BytesIO(image_data))
            
            # Pré-processar imagem para o modelo CLIP
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Gerar vetor
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)
            
            # Converter para numpy array
            vector = image_features.cpu().numpy().flatten()
            
            logger.info(f"Vetor CLIP gerado com sucesso: {len(vector)} dimensões")
            return vector
        
        except Exception as e:
            logger.error(f"Erro ao processar imagem com CLIP: {str(e)}")
            raise
    
    def find_similar_implants(self, query_vector: np.ndarray, db, limit: int = 3) -> List:
        """
        Encontra implantes similares baseado na distância do cosseno usando pgvector.
        
        Args:
            query_vector: Vetor de consulta
            db: Sessão do banco de dados
            limit: Número máximo de resultados
            
        Returns:
            List: Lista de implantes similares
        """
        try:
            from app.db.models import Implant
            from sqlalchemy import text
            
            # Usando a função cosine_distance do pgvector para melhor performance
            # com vetores normalizados como os do CLIP
            query = text("""
                SELECT id, name, manufacturer, image_url, 
                       1 - (vector <=> :vector::vector) as similarity
                FROM implants
                ORDER BY vector <=> :vector::vector
                LIMIT :limit
            """)
            
            vector_str = str(query_vector.tolist()).replace('[', '{').replace(']', '}')
            result = db.execute(query, {"vector": vector_str, "limit": limit})
            
            similar_implants = []
            for row in result:
                similar_implants.append({
                    "id": row[0],
                    "name": row[1],
                    "manufacturer": row[2],
                    "image_url": row[3],
                    "similarity": float(row[4]) * 100  # Converter para porcentagem
                })
            
            logger.info(f"Encontrados {len(similar_implants)} implantes similares")
            return similar_implants
        
        except Exception as e:
            logger.error(f"Erro ao buscar implantes similares: {str(e)}")
            raise
    
    def upload_to_spaces(self, file_content, object_name: str) -> str:
        """
        Faz upload de um arquivo para o DigitalOcean Spaces.
        
        Args:
            file_content: Conteúdo do arquivo
            object_name: Nome do objeto no Spaces
            
        Returns:
            str: URL pública do objeto
        """
        try:
            self.s3_client.upload_fileobj(
                file_content,
                settings.DO_SPACES_BUCKET,
                object_name,
                ExtraArgs={'ACL': 'public-read'}
            )
            
            url = f"https://{settings.DO_SPACES_BUCKET}.{settings.DO_SPACES_REGION}.digitaloceanspaces.com/{object_name}"
            logger.info(f"Arquivo enviado com sucesso para: {url}")
            return url
        
        except NoCredentialsError:
            logger.error("Credenciais não encontradas para DigitalOcean Spaces")
            raise
        except Exception as e:
            logger.error(f"Erro ao fazer upload para DigitalOcean Spaces: {str(e)}")
            raise

# Instância global do serviço CLIP
clip_service = ClipService()
