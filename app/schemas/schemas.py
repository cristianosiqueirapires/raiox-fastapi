from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

class ImplantBase(BaseModel):
    name: str
    manufacturer: str
    image_url: Optional[HttpUrl] = None

class ImplantCreate(ImplantBase):
    pass

class Implant(ImplantBase):
    id: int
    image_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    similarity: Optional[float] = None

    class Config:
        orm_mode = True

class ImageBase(BaseModel):
    submission_id: str
    client_id: str
    file_name: str

class ImageCreate(ImageBase):
    file_path: str
    file_url: HttpUrl
    metadata: Optional[dict] = None

class Image(ImageBase):
    id: int
    file_path: str
    file_url: HttpUrl
    metadata: Optional[dict] = None
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ResultBase(BaseModel):
    submission_id: str
    image_id: int
    implant_id: int
    similarity: float
    rank: int

class ResultCreate(ResultBase):
    pass

class Result(ResultBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class WebhookRequest(BaseModel):
    client_id: str = Field(..., description="ID do cliente que enviou a solicitação")
    image_url: HttpUrl = Field(..., description="URL da imagem para processamento")

class WebhookResponse(BaseModel):
    success: bool
    message: str
    results: Optional[List[Implant]] = None
