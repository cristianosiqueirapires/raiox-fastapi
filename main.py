from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api import webhook, endpoints
from app.core.config import settings
from app.db.session import engine, Base

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("raiox-api")

# Criar tabelas no banco de dados
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas/verificadas com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}")
        raise

# Inicializar aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
)

# Configurar CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Incluir routers
app.include_router(webhook.router, tags=["webhook"])
app.include_router(endpoints.router, prefix=settings.API_V1_STR, tags=["endpoints"])

@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando aplicação Raiox AI")
    init_db()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Encerrando aplicação Raiox AI")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
