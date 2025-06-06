# src/backend/schemas.py

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# ========== LeituraSensor ==========
class LeituraSensorCreate(BaseModel):
    cd_sensor: int
    dt_leitura: datetime
    vl_valor: float

class LeituraSensorResponse(BaseModel):
    cd_leitura: int
    cd_sensor: int
    dt_leitura: datetime
    vl_valor: float

    class Config:
        orm_mode = True

# ========== Alerta ==========
class AlertaCreate(BaseModel):
    dt_alerta: datetime
    tp_nivel: str
    tp_origem: str
    ds_obs: Optional[str] = None
    cd_area: int
    cd_usuario: int

class AlertaResponse(BaseModel):
    cd_alerta: int
    dt_alerta: datetime
    tp_nivel: str
    tp_origem: str
    ds_obs: Optional[str] = None
    cd_area: int
    cd_usuario: int
    nm_local: str
    nm_usuario: str

    class Config:
        orm_mode = True

# ========== Local ==========
class LocalCreate(BaseModel):
    nm_local: str
    tp_vulnerabilidade: str
    lat: Optional[float] = None
    lon: Optional[float] = None

class LocalUpdate(BaseModel):
    nm_local: Optional[str] = None
    tp_vulnerabilidade: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

class LocalResponse(BaseModel):
    cd_area: int
    nm_local: str
    tp_vulnerabilidade: str
    lat: Optional[float] = None
    lon: Optional[float] = None

    class Config:
        orm_mode = True

# ========== Sensor ==========
class SensorResponse(BaseModel):
    cd_sensor: int
    tp_sensor: str
    nm_modelo: Optional[str] = None
    cd_area: int

    class Config:
        orm_mode = True
