import os
import sqlite3

# Caminho absoluto para o arquivo .db (SQLite) dentro de src/backend
DB_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),  # <projeto_root>/src/backend
        "flood_sentinel.db"
    )
)

def get_connection():
    """
    Retorna uma conexão do sqlite3 configurada para retornar linhas como sqlite3.Row,
    com parsing automático de datas (ISO strings).
    """
    conn = sqlite3.connect(
        DB_PATH,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Cria as tabelas no SQLite, caso ainda não existam.
    A DDL abaixo reflete a mesma estrutura de colunas que você tinha no Oracle.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS LOCAL (
        cd_area            INTEGER PRIMARY KEY AUTOINCREMENT,
        nm_local           TEXT    NOT NULL,
        tp_vulnerabilidade TEXT    NOT NULL,
        lat                REAL,
        lon                REAL
    );

    CREATE TABLE IF NOT EXISTS SENSOR (
        cd_sensor INTEGER PRIMARY KEY AUTOINCREMENT,
        tp_sensor TEXT    NOT NULL,
        nm_modelo TEXT,
        cd_area   INTEGER NOT NULL REFERENCES LOCAL(cd_area) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS LEITURA_SENSOR (
        cd_leitura INTEGER PRIMARY KEY AUTOINCREMENT,
        cd_sensor  INTEGER NOT NULL REFERENCES SENSOR(cd_sensor) ON DELETE CASCADE,
        dt_leitura TEXT    NOT NULL,    -- armazenamos ISO string aqui
        vl_valor   REAL    NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ALERTA (
        cd_alerta  INTEGER PRIMARY KEY AUTOINCREMENT,
        dt_alerta  TEXT    NOT NULL,   -- ISO string
        tp_nivel   TEXT    NOT NULL,
        tp_origem  TEXT    NOT NULL,
        ds_obs     TEXT,
        cd_area    INTEGER NOT NULL REFERENCES LOCAL(cd_area) ON DELETE CASCADE,
        cd_usuario INTEGER NOT NULL
    );
    """)
    conn.commit()
    conn.close()

# Garante que, ao importar este módulo, as tabelas existam
init_db()
