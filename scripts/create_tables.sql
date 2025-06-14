-- scripts/create_tables.sql

-- Generated by Oracle SQL Developer Data Modeler 24.3.1.351.0831
--   at:        2025-06-01 17:09:08 BRT
--   site:      Oracle Database 11g
--   type:      Oracle Database 11g

CREATE TABLE Alerta (
    cd_alerta  INTEGER  NOT NULL,
    dt_alerta  TIMESTAMP WITH LOCAL TIME ZONE  NOT NULL,
    tp_nivel   VARCHAR2 (15)  NOT NULL,
    tp_origem  VARCHAR2 (15)  NOT NULL,
    ds_obs     CLOB,
    cd_area    INTEGER  NOT NULL,
    cd_usuario INTEGER  NOT NULL
);
ALTER TABLE Alerta ADD CONSTRAINT PK_Alerta PRIMARY KEY (cd_alerta);

CREATE TABLE Leitura_Sensor (
    cd_leitura INTEGER  NOT NULL,
    dt_leitura DATE  NOT NULL,
    vl_valor   FLOAT  NOT NULL,
    cd_sensor  INTEGER  NOT NULL
);
ALTER TABLE Leitura_Sensor ADD CONSTRAINT PK_Leitura_Sensor PRIMARY KEY (cd_sensor, cd_leitura);

CREATE TABLE Local (
    cd_area            INTEGER  NOT NULL,
    nm_local           VARCHAR2 (100)  NOT NULL,
    tp_vulnerabilidade VARCHAR2 (20)  NOT NULL
);
ALTER TABLE Local ADD CONSTRAINT PK_Local PRIMARY KEY (cd_area);

CREATE TABLE Sensor (
    cd_sensor INTEGER  NOT NULL,
    tp_sensor VARCHAR2 (30)  NOT NULL,
    nm_modelo VARCHAR2 (100),
    cd_area   INTEGER  NOT NULL
);
ALTER TABLE Sensor ADD CONSTRAINT PK_Sensor PRIMARY KEY (cd_sensor);

CREATE TABLE Usuario (
    cd_usuario INTEGER  NOT NULL,
    nm_usuario VARCHAR2 (100)  NOT NULL,
    ds_email   VARCHAR2 (100)  NOT NULL,
    tp_usuario VARCHAR2 (15)  NOT NULL
);
ALTER TABLE Usuario ADD CONSTRAINT PK_Usuario PRIMARY KEY (cd_usuario);

ALTER TABLE Alerta
  ADD CONSTRAINT FK_Alerta_Local FOREIGN KEY (cd_area) REFERENCES Local(cd_area);
ALTER TABLE Alerta
  ADD CONSTRAINT FK_Alerta_Usuario FOREIGN KEY (cd_usuario) REFERENCES Usuario(cd_usuario);
ALTER TABLE Leitura_Sensor
  ADD CONSTRAINT FK_Leitura_Sensor_Sensor FOREIGN KEY (cd_sensor) REFERENCES Sensor(cd_sensor);
ALTER TABLE Sensor
  ADD CONSTRAINT FK_Sensor_Local FOREIGN KEY (cd_area) REFERENCES Local(cd_area);
