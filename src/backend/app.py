# src/backend/app.py

from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from . import crud, schemas

app = FastAPI(
    title="Flood Sentinel API (SQLite)",
    description="API para receber leituras, gerenciar alertas, locais e sensores.",
    version="1.0"
)

# ================================
# ENDPOINT: CRIAR LOCAL
# ================================
@app.post("/locais/", response_model=schemas.LocalResponse)
def endpoint_criar_local(local: schemas.LocalCreate):
    try:
        novo = crud.criar_local(local)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar local: {e}")
    return novo

# ================================
# ENDPOINT: ATUALIZAR LOCAL
# ================================
@app.put("/locais/{cd_area}", response_model=schemas.LocalResponse)
def endpoint_atualizar_local(cd_area: int, local: schemas.LocalUpdate):
    try:
        atualizado = crud.atualizar_local(cd_area, local)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar local: {e}")
    return atualizado

# ================================
# ENDPOINT: LISTAR LOCAIS
# ================================
@app.get("/locais/", response_model=List[schemas.LocalResponse])
def endpoint_listar_locais():
    try:
        locais = crud.listar_locais()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar locais: {e}")
    if not locais:
        raise HTTPException(status_code=404, detail="Nenhum local cadastrado.")
    return locais


# ================================
# ENDPOINT: LISTAR SENSORES POR LOCAL
# ================================
@app.get("/sensores/{cd_area}", response_model=List[schemas.SensorResponse])
def endpoint_listar_sensores(cd_area: int):
    try:
        sensores = crud.listar_sensores_por_local(cd_area)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar sensores: {e}")
    if not sensores:
        raise HTTPException(status_code=404, detail="Nenhum sensor encontrado para esta área.")
    return sensores

# ================================
# ENDPOINT: CRIAR LEITURA
# ================================
@app.post("/leituras/", response_model=schemas.LeituraSensorResponse)
def endpoint_criar_leitura(leitura: schemas.LeituraSensorCreate):
    try:
        nova = crud.criar_leitura(leitura)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inserir leitura: {e}")
    return nova

# ================================
# ENDPOINT: LISTAR LEITURAS POR SENSOR
# ================================
@app.get("/leituras/{cd_sensor}", response_model=List[schemas.LeituraSensorResponse])
def endpoint_listar_leituras(cd_sensor: int, limit: int = 100):
    try:
        leituras = crud.listar_leituras_por_sensor(cd_sensor, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar leituras: {e}")
    if not leituras:
        raise HTTPException(status_code=404, detail="Nenhuma leitura encontrada para este sensor.")
    return leituras

# ================================
# ENDPOINT: CRIAR ALERTA
# ================================
@app.post("/alertas/", response_model=schemas.AlertaResponse)
def endpoint_criar_alerta(alerta: schemas.AlertaCreate):
    try:
        novo = crud.criar_alerta(alerta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inserir alerta: {e}")
    return novo

# ================================
# ENDPOINT: LISTAR ALERTAS
# ================================
@app.get("/alertas/", response_model=List[schemas.AlertaResponse])
def endpoint_listar_alertas(
    limit: int = Query(100, ge=1, description="Quantidade máxima de alertas retornados"),
    cd_area: Optional[int] = Query(
        None,
        description="Filtrar apenas alertas desta área (opcional)"
    )
):
    """
    Retorna os alertas mais recentes. Se 'cd_area' for informado, devolve apenas os alertas
    daquela área, até o número limite especificado.
    """
    try:
        if cd_area is not None:
            alertas = crud.listar_alertas_por_area(cd_area=cd_area, limit=limit)
        else:
            alertas = crud.listar_alertas(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar alertas: {e}")

    if not alertas:
        raise HTTPException(status_code=404, detail="Nenhum alerta encontrado.")

    return alertas
