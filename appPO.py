
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import expon
import sqlite3
import math

st.set_page_config(page_title="Métricas de Pesquisa Operacional", layout="wide")
st.header(" Métricas Observadas - Centro Comercial Alvarenga")

@st.cache_data
def carregar_dados():
    conn = sqlite3.connect("dados.db")
    query = """
        SELECT * FROM senhas
        WHERE data >= date('now', '-1 month')
        AND horario_chegada IS NOT NULL
        AND horario_chamada IS NOT NULL
        AND horario_finalizacao IS NOT NULL
    """
    df = pd.read_sql(query, conn, parse_dates=["horario_chegada", "horario_chamada", "horario_finalizacao"])
    conn.close()
    return df

df = carregar_dados()
servico_sel = st.radio("Selecione o serviço:", df['servico'].unique(), horizontal=True)

filtro = df[df['servico'] == servico_sel].copy()

# Calcular tempos em minutos
filtro['tempo_chegada'] = filtro['horario_chegada'].diff().dt.total_seconds() / 60
filtro['tempo_espera'] = (filtro['horario_chamada'] - filtro['horario_chegada']).dt.total_seconds() / 60
filtro['tempo_atendimento'] = (filtro['horario_finalizacao'] - filtro['horario_chamada']).dt.total_seconds() / 60
filtro.dropna(inplace=True)

# Estimativas
tempo_total = (filtro['horario_finalizacao'].max() - filtro['horario_chegada'].min()).total_seconds() / 60
lambda_ = round(len(filtro) / tempo_total, 4)  # taxa de chegada
mu = round(1 / filtro['tempo_atendimento'].mean(), 4)  # taxa de atendimento
c = st.slider("Número estimado de servidores ativos:", min_value=1, max_value=10, value=3)

# Cálculo M/M/c
def calcular_metricas(lambda_, mu, c):
    ro = lambda_ / (c * mu)

    soma = sum([(lambda_/mu)**n / math.factorial(n) for n in range(c)])
    p0 = 1 / (soma + ((lambda_/mu)**c / (math.factorial(c) * (1 - ro))))

    lq = ((lambda_/mu)**c * ro) / (math.factorial(c) * ((1 - ro)**2)) * p0
    wq = lq / lambda_
    w = wq + 1/mu
    l = lambda_ * w
    p_espera = lq / lambda_

    return {
        "λ (chegada)": round(lambda_, 4),
        "μ (atendimento)": round(mu, 4),
        "ρ (utilização)": round(ro, 4),
        "P₀ (sistema vazio)": round(p0, 4),
        "P_espera (aguardar)": round(p_espera, 4),
        "Lq (fila)": round(lq, 4),
        "Wq (espera)": round(wq, 4),
        "W (sistema)": round(w, 4),
        "L (no sistema)": round(l, 4)
    }

metricas = calcular_metricas(lambda_, mu, c)

st.subheader(" Resultados para o serviço selecionado")
st.write(pd.DataFrame(metricas.items(), columns=["Métrica", "Valor"]).set_index("Métrica"))

st.markdown("""
### 🔍 Explicações:
- **P₀**: probabilidade do sistema estar vazio.
- **P_espera**: probabilidade de um cliente ter que aguardar.
- **Lq**: número médio de clientes na fila.
- **Wq**: tempo médio de espera na fila.
- **W**: tempo médio no sistema (espera + atendimento).
- **L**: número médio total de clientes no sistema.
""")


st.title("Pesquisa Operacional - Simulação M/M/c")

st.markdown("### Selecione o serviço e os parâmetros do sistema")

# Escolha do serviço
servico = st.radio("Tipo de Serviço:", ["banco", "hospital", "restaurante"], horizontal=True)

# Parâmetros de entrada
col1, col2, col3 = st.columns(3)
with col1:
    lamb = st.selectbox("Taxa de chegada (λ)", [20, 24, 30])
with col2:
    mu = st.selectbox("Taxa de atendimento (μ)", [10, 12, 14])
with col3:
    c = st.selectbox("Número de servidores (c)", [2, 3, 4])

# Funções auxiliares
def calcular_mm_c(lamb, mu, c):
    rho = lamb / (c * mu)
    if rho >= 1:
        return None  # Sistema instável

    def fatorial(n):
        return np.math.factorial(n)

    # P0
    soma = sum((lamb/mu)**n / fatorial(n) for n in range(c))
    ultimo = ((lamb/mu)**c) / (fatorial(c) * (1 - rho))
    P0 = 1 / (soma + ultimo)

    # Prob. espera
    P_espera = ultimo * P0

    # Lq
    Lq = P_espera * (rho / (1 - rho))

    # Wq
    Wq = Lq / lamb

    # W e L
    W = Wq + 1/mu
    L = lamb * W

    return {
        "P0 (Sistema vazio)": round(P0, 4),
        "P_espera (Esperar na fila)": round(P_espera, 4),
        "Lq (Clientes na fila)": round(Lq, 2),
        "Wq (Tempo médio de espera)": round(Wq, 2),
        "W (Tempo total no sistema)": round(W, 2),
        "L (Clientes no sistema)": round(L, 2),
        "ρ (Utilização do sistema)": round(rho, 3)
    }

resultados = calcular_mm_c(lamb, mu, c)

st.subheader("📊 Métricas M/M/c")
if resultados:
    st.json(resultados)
else:
    st.error("Sistema instável (ρ ≥ 1). Escolha λ e μ apropriados.")

# Simulação de chegadas e atendimento
st.subheader(" Simulação de um período (exemplo de 100 clientes)")

n_clientes = 100
np.random.seed(42)
tempos_chegada = np.cumsum(expon.rvs(scale=1/lamb, size=n_clientes))
tempos_servico = expon.rvs(scale=1/mu, size=n_clientes)

fila = []
ocupacao = [0] * n_clientes
tempo_inicio_atendimento = []
tempo_espera = []

for i in range(n_clientes):
    if i < c:
        inicio = tempos_chegada[i]
    else:
        inicio = max(tempos_chegada[i], tempo_inicio_atendimento[i - c] + tempos_servico[i - c])
    tempo_inicio_atendimento.append(inicio)
    espera = inicio - tempos_chegada[i]
    tempo_espera.append(espera)
    fila.append(i)
    ocupacao[i] = min(c, sum(inicio < t <= inicio + s for t, s in zip(tempo_inicio_atendimento, tempos_servico)))

df_sim = pd.DataFrame({
    "Cliente": range(1, n_clientes + 1),
    "Chegada": tempos_chegada,
    "Início Atendimento": tempo_inicio_atendimento,
    "Tempo de Espera": tempo_espera,
    "Ocupação": ocupacao
})

# Gráficos
st.subheader(" Gráficos da Simulação")
tab1, tab2, tab3 = st.tabs(["Tempo de Espera", "Tamanho da Fila", "Ocupação dos Servidores"])

with tab1:
    fig, ax = plt.subplots()
    ax.plot(df_sim["Cliente"], df_sim["Tempo de Espera"], marker='o', color='blue')
    ax.set_title("Tempo de Espera por Cliente")
    ax.set_xlabel("Cliente")
    ax.set_ylabel("Tempo (min)")
    st.pyplot(fig)

with tab2:
    fila_tempo = df_sim["Tempo de Espera"].cumsum()
    fig, ax = plt.subplots()
    ax.plot(df_sim["Cliente"], fila_tempo, color='green')
    ax.set_title("Tamanho Acumulado da Fila")
    ax.set_xlabel("Cliente")
    ax.set_ylabel("Fila acumulada")
    st.pyplot(fig)

with tab3:
    fig, ax = plt.subplots()
    ax.plot(df_sim["Cliente"], df_sim["Ocupação"], color='red')
    ax.set_title("Ocupação dos Servidores")
    ax.set_xlabel("Cliente")
    ax.set_ylabel("Servidores Ocupados")
    st.pyplot(fig)

st.markdown("**Interpretação**:")
st.markdown("""
- Verifique se `Wq` está acima de 5 min.
- Avalie o impacto de aumentar `μ` (atendimento mais rápido) ou `c` (mais servidores).
- Um `P_espera` alto (> 0.7) pode indicar necessidade de ajuste.
""")
