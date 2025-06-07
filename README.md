# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
  <a href="https://www.fiap.com.br/">
    <img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" width="40%" height="40%" border="0">
  </a>
</p>

<br>

## Equipe Rocket

A proposta, estrutura e descrição do projeto estão contidas no PDF:  
[Flood Sentinel – Sistema de Alerta de Enchentes Online e Offline](./document/Flood%20Sentinel%20-%20Sistema%20de%20Alerta%20de%20Enchentes%20Online%20e%20Offline.pdf)

---

## 🔧 Como executar o código

### Pré-requisitos

- **Python 3.x**  
- (Opcional) ambiente virtual criado e ativado  
- Dependências instaladas:

```bash
pip install -r requirements.txt
```
- iniciar backend:
```bash
cd src && uvicorn backend.app:app --reload

```
- iniciar dashboard:
```bash
python src/dashboard/app.py
```

### Projeto ESP32

[Demonstração](esp32-project/README.md)