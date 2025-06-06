# src/dashboard/app.py

import dash
from dash import html, dcc, Output, Input
import plotly.express as px
import pandas as pd
import requests

# URL base do backend FastAPI
BACKEND_URL = "http://localhost:8000"

# (Opcional) Outras folhas de estilo externas podem ficar aqui
external_stylesheets = [
    # Por exemplo, normalize ou outro CSS
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server  # para deploy se necessário

# ================================
# Funções auxiliares para chamar o backend
# ================================

def fetch_areas():
    try:
        resp = requests.get(f"{BACKEND_URL}/locais/")
        resp.raise_for_status()
        df = pd.DataFrame(resp.json())
        return df
    except Exception as e:
        print("Erro ao buscar áreas:", e)
        return pd.DataFrame(columns=["cd_area", "nm_local", "tp_vulnerabilidade", "lat", "lon"])


def fetch_sensores(area_id: int):
    try:
        resp = requests.get(f"{BACKEND_URL}/sensores/{area_id}")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Erro ao buscar sensores para área {area_id}:", e)
        return []


def fetch_leituras_por_sensor(cd_sensor: int, limit: int = 50):
    try:
        resp = requests.get(f"{BACKEND_URL}/leituras/{cd_sensor}", params={"limit": limit})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Erro ao buscar leituras para sensor {cd_sensor}:", e)
        return []


def fetch_sensor_data(area_id: int):
    sensores = fetch_sensores(area_id)
    registros = []
    for sensor in sensores:
        cd_sensor = sensor.get("cd_sensor")
        nm_modelo = sensor.get("nm_modelo", f"Sensor {cd_sensor}")
        leituras = fetch_leituras_por_sensor(cd_sensor, limit=50)
        for L in leituras:
            try:
                registros.append({
                    "cd_leitura": L["cd_leitura"],
                    "cd_sensor": L["cd_sensor"],
                    "dt_leitura": pd.to_datetime(L["dt_leitura"]),
                    "vl_valor": L["vl_valor"],
                    "nm_modelo": nm_modelo
                })
            except Exception:
                continue

    if not registros:
        return pd.DataFrame(columns=["cd_leitura", "cd_sensor", "dt_leitura", "vl_valor", "nm_modelo"])
    return pd.DataFrame(registros)


def fetch_alertas(limit: int = 100):
    """
    Chama GET /alertas/?limit={limit} para obter últimos alertas.
    Retorna DataFrame com colunas: ['cd_alerta', 'dt_alerta', 'tp_nivel', 'ds_obs', 'cd_area', 'nm_local'].
    """
    try:
        resp = requests.get(f"{BACKEND_URL}/alertas/", params={"limit": limit})
        resp.raise_for_status()
        df = pd.DataFrame(resp.json())
        
        if "dt_alerta" in df.columns:
            # infer_datetime_format=True lida com formatos mistos (com ou sem microssegundos)
            df["dt_alerta"] = pd.to_datetime(
                df["dt_alerta"],
                infer_datetime_format=True,
                errors="coerce"
            )
        return df

    except Exception as e:
        print("Erro ao buscar alertas:", e)
        return pd.DataFrame(
            columns=["cd_alerta", "dt_alerta", "tp_nivel", "ds_obs", "cd_area", "nm_local"]
        )


# ================================
# Layout Inicial
# ================================

df_areas = fetch_areas()
area_options = [
    {"label": row["nm_local"], "value": row["cd_area"]}
    for _, row in df_areas.iterrows()
]

app.layout = html.Div(className="dash-container", children=[
    html.H1("Flood Sentinel Dashboard"),

    # Filtro de Área + botão Atualizar
    html.Div(
        style={"display": "flex", "justifyContent": "space-between", "marginBottom": "20px"},
        children=[
            html.Div(
                style={"flex": "1", "marginRight": "20px"},
                children=[
                    html.Label("Selecione a Área:", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="dropdown-area",
                        options=area_options,
                        value=area_options[0]["value"] if area_options else None,
                        clearable=False,
                    ),
                ]
            ),
            html.Button("Atualizar Dados", id="btn-atualizar", n_clicks=0, className="my-button"),
        ],
    ),

    # Painel principal: Leituras vs Alertas + Mapa
    html.Div(className="main-row", children=[
        # Coluna esquerda: gráfico + tabela de leituras
        html.Div(className="card", children=[
            html.H3("Leituras de Sensores"),
            dcc.Graph(id="graph-leituras-tempo"),
            html.H4("Últimas Leituras (tabela)", style={"marginTop": "20px"}),
            dcc.Loading(
                id="loading-table",
                type="default",
                children=html.Div(id="tabela-leituras"),
            ),
        ]),

        # Coluna direita: lista de alertas + mapa
        html.Div(className="card", children=[
            html.H3("Alertas Recentes"),
            html.Ul(id="lista-alertas", style={"paddingLeft": "20px"}),
            html.Button("Forçar Alerta (Manual)", id="btn-forcar-alerta", n_clicks=0,
                        style={"marginTop": "10px", "marginBottom": "20px"}, className="my-button"),

            html.H3("Mapa de Áreas"),
            dcc.Graph(id="mapa-areas"),
        ]),
    ]),

    # Seção de observações manuais
    html.Div(
        style={"marginTop": "30px", "borderTop": "1px solid #eee", "paddingTop": "20px"},
        children=[
            html.H3("Registrar Observação Manual"),
            dcc.Textarea(
                id="textarea-observacao",
                placeholder="Escreva aqui sua observação...",
                style={"width": "100%", "height": "100px"},
            ),
            html.Button("Enviar Observação", id="btn-enviar-observacao", n_clicks=0,
                        style={"marginTop": "10px"}, className="my-button"),
            html.Div(id="status-envio", style={"marginTop": "10px", "color": "green"}),
        ]
    ),
])


# ================================
# Callbacks
# ================================

@app.callback(
    Output("graph-leituras-tempo", "figure"),
    Input("dropdown-area", "value"),
    Input("btn-atualizar", "n_clicks"),
)
def atualizar_grafico_leituras(cd_area, _):
    if cd_area is None:
        return px.line(title="Selecione uma área para ver as leituras")

    df = fetch_sensor_data(cd_area)
    if df.empty:
        return px.line(
            pd.DataFrame({"dt_leitura": [], "vl_valor": [], "nm_modelo": []}),
            x="dt_leitura",
            y="vl_valor",
            color="nm_modelo",
            title="Sem dados disponíveis para esta área"
        )

    df["dt_leitura"] = df["dt_leitura"].dt.round("S")
    df = df.drop_duplicates(subset=["dt_leitura", "nm_modelo"])

    fig = px.line(
        df,
        x="dt_leitura",
        y="vl_valor",
        color="nm_modelo",
        title=f"Leituras Recentes - Área {cd_area}",
        labels={"vl_valor": "Valor", "dt_leitura": "Data/Hora", "nm_modelo": "Sensor/Modelo"}
    )
    fig.update_xaxes(tickformat="%H:%M:%S", ticklabelmode="period")
    fig.update_layout(
        transition_duration=300,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    return fig


@app.callback(
    Output("tabela-leituras", "children"),
    Input("dropdown-area", "value"),
    Input("btn-atualizar", "n_clicks"),
)
def atualizar_tabela_leituras(cd_area, _):
    if cd_area is None:
        return html.Div("Selecione uma área para ver as leituras.")

    df = fetch_sensor_data(cd_area)
    if df.empty:
        return html.Div("Sem dados para exibir.")

    df_ult = df.sort_values("dt_leitura", ascending=False).head(5)
    return html.Table(
        [html.Tr([html.Th(col) for col in ["Data/Hora", "Sensor", "Valor"]])] +
        [
            html.Tr([
                html.Td(row["dt_leitura"].strftime("%Y-%m-%d %H:%M:%S")),
                html.Td(row["nm_modelo"]),
                html.Td(f"{row['vl_valor']:.2f}")
            ])
            for _, row in df_ult.iterrows()
        ],
        className="dash-table-container"
    )


@app.callback(
    Output("lista-alertas", "children"),
    [
        Input("dropdown-area", "value"),
        Input("btn-atualizar", "n_clicks"),
        Input("btn-forcar-alerta", "n_clicks"),
        Input("btn-enviar-observacao", "n_clicks")
    ]
)
def atualizar_lista_alertas(cd_area, n_atualizar, n_forcar, n_enviar_obs):
    """
    Roda sempre que:
     - mudar a área no dropdown (cd_area muda),
     - ou clicar em Atualizar Dados (n_atualizar incrementa),
     - ou clicar em Forçar Alerta (n_forcar incrementa),
     - ou clicar em Enviar Observação (n_enviar_obs incrementa).
    """
    # 1) Se nenhuma área selecionada, mostra instrução
    if cd_area is None:
        return [html.Li("Selecione uma área para ver alertas.")]

    # 2) Busca alertas do backend
    try:
        df = fetch_alertas(limit=10)
    except Exception as e:
        print("Erro ao buscar alertas no callback:", e)
        return [html.Li("Não foi possível obter alertas.")]

    # DEBUG opcional: veja no terminal quais alertas chegaram
    print("\n[DEBUG] Alertas brutos vindos do backend (antes de filtrar):")
    try:
        # Exibe colunas relevantes para conferir no terminal
        print(df[["cd_alerta", "dt_alerta", "tp_nivel", "cd_area", "nm_local"]]
              .sort_values("dt_alerta", ascending=False).to_string(index=False))
    except Exception:
        print(df)

    # 3) Filtra apenas alertas da área selecionada
    df_area = df[df["cd_area"] == cd_area]

    # 4) Se não houver nenhum alerta para essa área, devolve uma mensagem
    if df_area.empty:
        return [html.Li("Nenhum alerta disponível para esta área.")]

    # 5) Ordena por data decrescente e pega os 10 mais recentes
    df_sorted = df_area.sort_values("dt_alerta", ascending=False).head(10)

    # 6) Monta a lista de <li> com o texto formatado
    itens = []
    for _, row in df_sorted.iterrows():
        # Se houver data válida, formata; caso contrário, deixa em branco
        if pd.notna(row["dt_alerta"]):
            ts = row["dt_alerta"].strftime("%Y-%m-%d %H:%M")
        else:
            ts = "DataDesconhecida"

        local = row.get("nm_local", f"Área {row.get('cd_area', '?')}")
        nivel = row.get("tp_nivel", "NívelDesconhecido")
        observacao = row.get("ds_obs", "")
        texto = f"[{ts}] {local} – {nivel} – {observacao}"
        itens.append(
            html.Li(texto, **{"data-nivel": nivel})
        )
    return itens


@app.callback(
    Output("mapa-areas", "figure"),
    Input("dropdown-area", "value"),
    Input("btn-atualizar", "n_clicks"),
)
def atualizar_mapa(cd_area, _):
    df = fetch_areas().copy()
    if df.empty:
        return px.scatter_map(
            pd.DataFrame({"lat": [], "lon": []}),
            lat="lat", lon="lon",
            title="Nenhuma área cadastrada"
        )

    if "lat" not in df.columns or "lon" not in df.columns:
        return px.scatter_map(
            pd.DataFrame({"lat": [], "lon": []}),
            lat="lat", lon="lon",
            title="Mapeamento indisponível (sem 'lat'/'lon')"
        )

    fig = px.scatter_map(
        df,
        lat="lat",
        lon="lon",
        hover_name="nm_local",
        color="tp_vulnerabilidade" if "tp_vulnerabilidade" in df.columns else None,
        size_max=15,
        zoom=6,
        height=400,
        title="Localização das Áreas"
    )
    fig.update_layout(mapbox_style="open-street-map", margin={"l": 0, "r": 0, "t": 30, "b": 0})
    return fig


@app.callback(
    Output("status-envio", "children"),
    Input("btn-enviar-observacao", "n_clicks"),
    Input("textarea-observacao", "value"),
    Input("dropdown-area", "value"),
)
def enviar_observacao(n_clicks, texto, cd_area):
    if n_clicks == 0:
        return ""

    if not texto or not texto.strip():
        return "Escreva algo antes de enviar."
    if cd_area is None:
        return "Selecione uma área antes de enviar."

    payload = {
        "dt_alerta": pd.Timestamp.now().isoformat(),
        "tp_nivel": "MANUAL",
        "tp_origem": "Dashboard",
        "ds_obs": texto,
        "cd_area": cd_area,
        "cd_usuario": 1
    }
    try:
        resp = requests.post(f"{BACKEND_URL}/alertas/", json=payload)
        resp.raise_for_status()
        return "Observação enviada como alerta com sucesso."
    except Exception as e:
        print("Erro ao enviar observação como alerta:", e)
        return "Falha ao enviar observação."


@app.callback(
    Output("btn-forcar-alerta", "children"),
    Input("btn-forcar-alerta", "n_clicks"),
    Input("dropdown-area", "value"),
)
def forcar_alerta(n_clicks, cd_area):
    if n_clicks == 0:
        return "Forçar Alerta (Manual)"
    if cd_area is None:
        return "Selecione uma área antes."

    payload = {
        "dt_alerta": pd.Timestamp.now().isoformat(),
        "tp_nivel": "CRITICO",
        "tp_origem": "Dashboard",
        "ds_obs": "Alerta manual pelo usuário",
        "cd_area": cd_area,
        "cd_usuario": 1
    }
    try:
        resp = requests.post(f"{BACKEND_URL}/alertas/", json=payload)
        resp.raise_for_status()
        return "Alerta forçado com sucesso!"
    except Exception as e:
        print("Erro ao forçar alerta:", e)
        return "Erro ao forçar alerta."


# ================================
# Run (substitui run_server)
# ================================
if __name__ == "__main__":
    app.run(debug=True)
