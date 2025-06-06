# src/backend/crud.py

from typing import List
import sqlite3
import pandas as pd
from sqlalchemy.orm import Session
from .database import get_connection
from .schemas import (
    LeituraSensorCreate,
    LeituraSensorResponse,
    AlertaCreate,
    AlertaResponse,
    LocalCreate,
    LocalUpdate,
    LocalResponse,
    SensorResponse
)

# ================================
# FUNÇÃO: CRIAR LEITURA
# ================================
def criar_leitura(leitura: LeituraSensorCreate) -> LeituraSensorResponse:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO LEITURA_SENSOR (cd_sensor, dt_leitura, vl_valor)
            VALUES (?, ?, ?)
            """,
            (
                leitura.cd_sensor,
                leitura.dt_leitura.isoformat(sep=" "),
                leitura.vl_valor
            )
        )
        conn.commit()
        novo_id = cursor.lastrowid
        return LeituraSensorResponse(
            cd_leitura=novo_id,
            cd_sensor=leitura.cd_sensor,
            dt_leitura=leitura.dt_leitura,
            vl_valor=leitura.vl_valor
        )
    finally:
        conn.close()

# ================================
# FUNÇÃO: LISTAR LEITURAS POR SENSOR
# ================================
def listar_leituras_por_sensor(cd_sensor: int, limit: int = 100) -> list[LeituraSensorResponse]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT cd_leitura, cd_sensor, dt_leitura, vl_valor
              FROM LEITURA_SENSOR
             WHERE cd_sensor = ?
             ORDER BY datetime(dt_leitura) ASC
             LIMIT ?
            """,
            (cd_sensor, limit)
        )
        linhas = cursor.fetchall()
        resultado = []
        for row in linhas:
            dt = row["dt_leitura"]
            resultado.append(
                LeituraSensorResponse(
                    cd_leitura=int(row["cd_leitura"]),
                    cd_sensor=int(row["cd_sensor"]),
                    dt_leitura=pd.to_datetime(dt) if dt is not None else None,
                    vl_valor=float(row["vl_valor"])
                )
            )
        return resultado
    finally:
        conn.close()

# ================================
# FUNÇÃO: CRIAR ALERTA
# ================================
def criar_alerta(alerta: AlertaCreate) -> AlertaResponse:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO ALERTA (dt_alerta, tp_nivel, tp_origem, ds_obs, cd_area, cd_usuario)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                alerta.dt_alerta.isoformat(sep=" "),
                alerta.tp_nivel,
                alerta.tp_origem,
                alerta.ds_obs,
                alerta.cd_area,
                alerta.cd_usuario
            )
        )
        conn.commit()
        novo_id = cursor.lastrowid

        # Busca o nome do local e define nm_usuario fixo
        cursor.execute(
            """
            SELECT l.nm_local,
                   ? AS nm_usuario
              FROM ALERTA a
              JOIN LOCAL l ON a.cd_area = l.cd_area
             WHERE a.cd_alerta = ?
            """,
            ("UsuárioFixo", novo_id)
        )
        linha = cursor.fetchone()
        nm_local, nm_usuario = linha["nm_local"], linha["nm_usuario"]

        return AlertaResponse(
            cd_alerta=novo_id,
            dt_alerta=alerta.dt_alerta,  # usa diretamente o valor enviado
            tp_nivel=alerta.tp_nivel,
            tp_origem=alerta.tp_origem,
            ds_obs=alerta.ds_obs,
            cd_area=alerta.cd_area,
            cd_usuario=alerta.cd_usuario,
            nm_local=nm_local,
            nm_usuario=nm_usuario
        )
    finally:
        conn.close()

# ================================
# FUNÇÃO: LISTAR ALERTAS
# ================================
def listar_alertas(limit: int) -> List[AlertaResponse]:
    """
    Retorna até 'limit' alertas mais recentes de todas as áreas.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT a.cd_alerta,
                   a.dt_alerta,
                   a.tp_nivel,
                   a.tp_origem,
                   a.ds_obs,
                   a.cd_area,
                   a.cd_usuario,
                   l.nm_local,
                   ? AS nm_usuario
              FROM ALERTA a
              JOIN LOCAL l ON a.cd_area = l.cd_area
             ORDER BY datetime(a.dt_alerta) DESC
             LIMIT ?
            """,
            ("UsuárioFixo", limit)
        )
        linhas = cursor.fetchall()
        resultado = []
        for row in linhas:
            dt = row["dt_alerta"]
            resultado.append(
                AlertaResponse(
                    cd_alerta=int(row["cd_alerta"]),
                    dt_alerta=pd.to_datetime(dt) if dt is not None else None,
                    tp_nivel=row["tp_nivel"],
                    tp_origem=row["tp_origem"],
                    ds_obs=row["ds_obs"],
                    cd_area=int(row["cd_area"]),
                    cd_usuario=int(row["cd_usuario"]),
                    nm_local=row["nm_local"],
                    nm_usuario=row["nm_usuario"]
                )
            )
        return resultado
    finally:
        conn.close()


def listar_alertas_por_area(cd_area: int, limit: int) -> List[AlertaResponse]:
    """
    Retorna até 'limit' alertas mais recentes apenas da área 'cd_area'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT a.cd_alerta,
                   a.dt_alerta,
                   a.tp_nivel,
                   a.tp_origem,
                   a.ds_obs,
                   a.cd_area,
                   a.cd_usuario,
                   l.nm_local,
                   ? AS nm_usuario
              FROM ALERTA a
              JOIN LOCAL l ON a.cd_area = l.cd_area
             WHERE a.cd_area = ?
             ORDER BY datetime(a.dt_alerta) DESC
             LIMIT ?
            """,
            ("UsuárioFixo", cd_area, limit)
        )
        linhas = cursor.fetchall()
        resultado = []
        for row in linhas:
            dt = row["dt_alerta"]
            resultado.append(
                AlertaResponse(
                    cd_alerta=int(row["cd_alerta"]),
                    dt_alerta=pd.to_datetime(dt) if dt is not None else None,
                    tp_nivel=row["tp_nivel"],
                    tp_origem=row["tp_origem"],
                    ds_obs=row["ds_obs"],
                    cd_area=int(row["cd_area"]),
                    cd_usuario=int(row["cd_usuario"]),
                    nm_local=row["nm_local"],
                    nm_usuario=row["nm_usuario"]
                )
            )
        return resultado
    finally:
        conn.close()

# ================================
# FUNÇÃO: CRIAR ÁREA
# ================================
def criar_local(local: LocalCreate) -> LocalResponse:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO LOCAL (nm_local, tp_vulnerabilidade, lat, lon)
            VALUES (?, ?, ?, ?)
            """,
            (
                local.nm_local,
                local.tp_vulnerabilidade,
                local.lat,
                local.lon
            )
        )
        conn.commit()
        novo_id = cursor.lastrowid
        return LocalResponse(
            cd_area=novo_id,
            nm_local=local.nm_local,
            tp_vulnerabilidade=local.tp_vulnerabilidade,
            lat=local.lat,
            lon=local.lon
        )
    finally:
        conn.close()

# ================================
# FUNÇÃO: ATUALIZAR ÁREA
# ================================
def atualizar_local(cd_area: int, local: LocalUpdate) -> LocalResponse:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Montar dinamicamente SET apenas com campos não nulos
        campos = []
        valores = []
        if local.nm_local is not None:
            campos.append("nm_local = ?")
            valores.append(local.nm_local)
        if local.tp_vulnerabilidade is not None:
            campos.append("tp_vulnerabilidade = ?")
            valores.append(local.tp_vulnerabilidade)
        if local.lat is not None:
            campos.append("lat = ?")
            valores.append(local.lat)
        if local.lon is not None:
            campos.append("lon = ?")
            valores.append(local.lon)

        if not campos:
            # Se nenhum campo vier para atualizar, busca e retorna o que já existe
            cursor.execute(
                "SELECT cd_area, nm_local, tp_vulnerabilidade, lat, lon FROM LOCAL WHERE cd_area = ?",
                (cd_area,)
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Área com cd_area={cd_area} não encontrada.")
            return LocalResponse(
                cd_area=row["cd_area"],
                nm_local=row["nm_local"],
                tp_vulnerabilidade=row["tp_vulnerabilidade"],
                lat=row["lat"],
                lon=row["lon"]
            )

        # Adiciona cd_area ao final dos valores, para o WHERE
        valores.append(cd_area)
        sql = f"UPDATE LOCAL SET {', '.join(campos)} WHERE cd_area = ?"
        cursor.execute(sql, tuple(valores))
        if cursor.rowcount == 0:
            raise ValueError(f"Área com cd_area={cd_area} não encontrada.")
        conn.commit()

        # Busca a área atualizada
        cursor.execute(
            "SELECT cd_area, nm_local, tp_vulnerabilidade, lat, lon FROM LOCAL WHERE cd_area = ?",
            (cd_area,)
        )
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"Área com cd_area={cd_area} não encontrada após update.")
        return LocalResponse(
            cd_area=row["cd_area"],
            nm_local=row["nm_local"],
            tp_vulnerabilidade=row["tp_vulnerabilidade"],
            lat=row["lat"],
            lon=row["lon"]
        )
    finally:
        conn.close()

# ================================
# FUNÇÃO: LISTAR LOCAIS
# ================================
def listar_locais() -> list[LocalResponse]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT cd_area, nm_local, tp_vulnerabilidade, lat, lon FROM LOCAL")
        linhas = cursor.fetchall()
        resultado = []
        for row in linhas:
            resultado.append(
                LocalResponse(
                    cd_area=int(row["cd_area"]),
                    nm_local=row["nm_local"],
                    tp_vulnerabilidade=row["tp_vulnerabilidade"],
                    lat=row["lat"],
                    lon=row["lon"]
                )
            )
        return resultado
    finally:
        conn.close()

# ================================
# FUNÇÃO: LISTAR SENSORES POR LOCAL
# ================================
def listar_sensores_por_local(cd_area: int) -> list[SensorResponse]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT cd_sensor, tp_sensor, nm_modelo, cd_area FROM SENSOR WHERE cd_area = ?",
            (cd_area,)
        )
        linhas = cursor.fetchall()
        resultado = []
        for row in linhas:
            resultado.append(
                SensorResponse(
                    cd_sensor=int(row["cd_sensor"]),
                    tp_sensor=row["tp_sensor"],
                    nm_modelo=row["nm_modelo"],
                    cd_area=int(row["cd_area"])
                )
            )
        return resultado
    finally:
        conn.close()
