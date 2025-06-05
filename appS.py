import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import expon, poisson, norm, t
import sqlite3

sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams.update({'figure.figsize': (8, 4.5), 'axes.titlesize': 14, 'axes.labelsize': 12})

st.set_page_config(layout="wide")
st.title("Centro Comercial Alvarenga - Análise Estatística")

# --- Conectar ao banco de dados e carregar os dados do último mês ---
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

servicos = df['servico'].unique().tolist()
servico_sel = st.radio("Selecione o serviço:", servicos, horizontal=True)

filtro = df[df['servico'] == servico_sel].copy()

# --- Cálculo dos tempos ---
filtro['tempo_atendimento'] = (filtro['horario_finalizacao'] - filtro['horario_chamada']).dt.total_seconds() / 60
filtro['tempo_espera'] = (filtro['horario_chamada'] - filtro['horario_chegada']).dt.total_seconds() / 60
filtro['tempo_total'] = (filtro['horario_finalizacao'] - filtro['horario_chegada']).dt.total_seconds() / 60
filtro['chegada_diff'] = filtro['horario_chegada'].diff().dt.total_seconds() / 60
filtro['hora'] = filtro['horario_chegada'].dt.hour

filtro['data'] = filtro['horario_chegada'].dt.date
filtro = filtro.sort_values(['data', 'horario_chegada'])
filtro['chegada_diff'] = filtro.groupby('data')['horario_chegada'].diff().dt.total_seconds() / 60

# --- Medidas Descritivas ---
def estatisticas(col):
    return {
        "Média": round(col.mean(), 2),
        "Mediana": round(col.median(), 2),
        "Moda": round(col.mode().iloc[0], 2) if not col.mode().empty else np.nan,
        "Desvio Padrão": round(col.std(), 2)
    }

with st.expander("Medidas Descritivas"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Tempo entre chegadas")
        st.json(estatisticas(filtro['chegada_diff'].dropna()))
    with col2:
        st.subheader("Tempo de atendimento")
        st.json(estatisticas(filtro['tempo_atendimento']))
    with col3:
        st.subheader("Tempo de espera")
        st.json(estatisticas(filtro['tempo_espera']))

# --- Visualizações ---
with st.expander("Visualizações (gráficos dinâmicos)"):
    tipo = st.selectbox("Escolha o tipo de gráfico:", [
        "Histogramas + Densidade",
        "Boxplots",
        "Linha - Tempo de espera por ordem"
    ])

    if tipo == "Histogramas + Densidade":
        for var in ["tempo_atendimento", "tempo_espera", "tempo_total"]:
            st.markdown(f"**Distribuição do {var.replace('_', ' ')} - mostra como os dados estão espalhados e sua densidade**")
            fig, ax = plt.subplots()
            sns.histplot(filtro[var].dropna(), kde=True, ax=ax, bins=30, color="skyblue")
            ax.set_title(f"{var.replace('_', ' ').capitalize()} - {servico_sel.capitalize()}")
            ax.set_xlabel("Minutos")
            ax.grid(False)
            st.pyplot(fig)           

    elif tipo == "Boxplots":
        st.markdown("**Comparação da dispersão entre os tempos de atendimento e de espera.**")
        fig1, ax1 = plt.subplots()
        sns.boxplot(data=filtro[["tempo_atendimento", "tempo_espera"]], palette="pastel", linewidth=2, ax=ax1)
        ax1.set_title("Boxplot - Atendimento vs Espera", fontsize=14)
        ax1.set_xticklabels(["Atendimento", "Espera"])
        ax1.grid(False)
        st.pyplot(fig1)
       


        if "tipo" in filtro.columns:
            st.markdown("**Comparativo do tempo de espera entre clientes prioritários e não prioritários.**")
            fig2, ax2 = plt.subplots()
            sns.boxplot(x="tipo", y="tempo_espera", data=filtro, ax=ax2)
            ax2.set_title("Tempo de espera - Prioridade")
            st.pyplot(fig2)

    elif tipo == "Linha - Tempo de espera por ordem":
        st.markdown("**Evolução do tempo de espera ao longo do dia em ordem de chegada.**")
        fig, ax = plt.subplots()
        filtro_sorted = filtro.sort_values("horario_chegada").reset_index(drop=True)

        fig, ax = plt.subplots()
        sns.lineplot(x=range(len(filtro_sorted)), y=filtro_sorted["tempo_espera"], marker='o', ax=ax, color="royalblue")
        ax.set_title("Evolução do Tempo de Espera", fontsize=14)
        ax.set_xlabel("Ordem de chegada")
        ax.set_ylabel("Tempo de espera (min)")
        ax.grid(False)  # <- remove grades
        st.pyplot(fig)




# --- Verificações estatísticas ---
with st.expander("Distribuições teóricas: Exponencial e Poisson"):
    st.subheader("Tempo entre chegadas ~ Exponencial")
    st.markdown(" Esta análise verifica se os tempos entre as chegadas seguem uma **distribuição exponencial**, como previsto em filas do tipo M/M/c.")

    fig, ax = plt.subplots()
    dados = filtro['chegada_diff'].dropna()
    sns.histplot(dados, kde=False, stat='density', bins=30, ax=ax, label="Empírico", color="lightblue")
    x = np.linspace(0, dados.max(), 100)
    lambda_ = 1 / dados.mean()
    ax.plot(x, expon.pdf(x, scale=1/lambda_), label="Exponencial ajustada", color='red')
    ax.set_title("Ajuste da Distribuição Exponencial")
    ax.legend()
    ax.grid(False)
    st.pyplot(fig)

    st.subheader("Nº de chegadas por hora ~ Poisson")
    st.markdown(" Esta análise verifica se o número de clientes que chegam por hora segue uma **distribuição Poisson**, que modela eventos discretos ao longo do tempo.")

    contagem = filtro['hora'].value_counts().sort_index()
    media = contagem.mean()
    fig2, ax2 = plt.subplots()
    contagem.plot(kind='bar', ax=ax2, label="Observado", color="lightgray")
    poisson_probs = [poisson.pmf(k, mu=media) * len(contagem) for k in contagem.index]
    ax2.plot(contagem.index, poisson_probs, color='red', marker='o', linestyle='--', label="Poisson ajustado")
    ax2.set_title("Chegadas por hora - Ajuste Poisson")
    ax2.legend()
    ax2.grid(False)
    st.pyplot(fig2)

# --- Intervalos de Confiança ---
def intervalo_confianca_amostra(amostra):
    media = amostra.mean()
    desvio = amostra.std()
    n = len(amostra)
    t_crit = t.ppf(0.975, df=n-1)
    margem = t_crit * desvio / np.sqrt(n)
    return (round(media - margem, 2), round(media + margem, 2))

with st.expander("Intervalos de Confiança + Interpretação"):
    st.subheader("IC para o tempo médio de atendimento")
    ic1 = intervalo_confianca_amostra(filtro['tempo_atendimento'].dropna())
    st.write(f"Intervalo de Confiança (95%): {ic1[0]} a {ic1[1]} minutos")
    st.subheader("IC para o tempo médio de espera")
    ic2 = intervalo_confianca_amostra(filtro['tempo_espera'].dropna())
    st.write(f"Intervalo de Confiança (95%): {ic2[0]} a {ic2[1]} minutos")

    st.markdown("""
    **Interpretação**:
    - Se o tempo de espera está muito variável ou com limites altos, pode indicar necessidade de mais guichês.
    - O tempo de atendimento com IC muito largo pode impactar a previsibilidade.
    - Avalie o modelo M/M/c baseado nesses indicadores.
    """)
