from datetime import datetime

from pydantic import BaseModel, HttpUrl, ConfigDict


class URLCreate(BaseModel):
    url_original: HttpUrl


class URLResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo_corto: str
    url_original: str
    fecha_creacion: datetime
    clics_totales: int


class URLStats(BaseModel):
    codigo_corto: str
    url_original: str
    clics_totales: int
    ultimos_clics: list[datetime]