
# 📊 Simulador de Atendimento 

Este repositório apresenta um sistema integrado para simulação de atendimento com geração de senhas, chamadas por atendentes, visualização em painel, e análise posterior com foco estatístico e operacional. O projeto é voltado para uso educacional, exposições e estudos em disciplinas como **Pesquisa Operacional**, **Estatística**, e **Desenvolvimento Web**.

---

## 🔧 Tecnologias Utilizadas

- Python 3.10+
- Flask (backend)
- Streamlit (visualizações e análise de dados)
- SQLite3 (banco de dados)
- HTML5, CSS3 (interfaces front-end)
- Pandas, NumPy, Matplotlib, Seaborn, SciPy

---

## 📁 Estrutura do Projeto

```
├── Projeto            # Pasta com documentação técnica de apoio 
├── app.py             # Servidor Flask - geração de senhas e API
├── appPO.py           # Página de análise de Pesquisa Operacional (Streamlit)
├── appS.py            # Página de análise Estatística (Streamlit)
├── starserver.py      # Script para iniciar Flask e ambas as páginas Streamlit
├── atendente.html     # Interface do atendente para chamar senhas
├── painel.html        # Painel de visualização de chamadas de senhas
├── totem.html         # Totem de atendimento para geração de senhas
├── atendente.css      # Estilo visual para atendente.html
├── painel.css         # Estilo visual para painel.html
├── totem.css          # Estilo visual para totem.html
├── logo.png           # Logotipo exibido nas páginas HTML
├── ms.ico             # Ícone do navegador (favicon)
├── dados.db           # Banco de dados SQLite com histórico dos atendimentos
└── README.md          # Documentação do projeto
└── Rede.jpg           # Guia para estruturação da rede do projeto
```

---

##  Diretrizes do Projeto

A pasta Projeto contém documentos técnicos de apoio para:
- Planejamento do Projeto
- Acompanhamento do Projeto

O arquivo Rede.jpg pode ajudá-lo no entendimento da arquitetura física da solução.

---

## 🚀 Como Executar o Projeto

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/simulador-atendimento.git
cd simulador-atendimento
```

### 2. Instale as dependências

```bash
pip install flask streamlit pandas numpy matplotlib seaborn scipy
```

### 3. Execute todos os servidores com um único comando

```bash
python starserver.py
```

Esse script inicializa automaticamente:
- O servidor Flask (`app.py`) para geração e controle de senhas
- A página Streamlit de Estatística (`appS.py`)
- A página Streamlit de Pesquisa Operacional (`appPO.py`)

---

## 🌐 Acessando as Interfaces

- **Totem**: abra `totem.html` em um navegador → Geração de senha por serviço
- **Painel**: abra `painel.html` em um navegador → Exibição pública da próxima senha chamada
- **Atendente**: abra `atendente.html` em um navegador → Tela de gerenciamento e chamada das senhas
- **Análise PO e Estatística**: acesse o Streamlit em `http://localhost:8501` e `http://localhost:8502`

> OBS: Garanta que o backend (`app.py`) esteja rodando para que as páginas funcionem corretamente.

---

## 📊 Funcionalidades

### 🔘 Totem

- Geração de senhas para três serviços: Banco, Hospital e Restaurante
- Seleção de prioridade no atendimento
- Interface amigável para tela touch

### 👩‍💼 Atendente

- Chamada de senhas por guichê
- Finalização de atendimentos
- Atualização em tempo real do painel

### 📺 Painel

- Exibição clara das senhas chamadas por serviço
- Atualização automática e design responsivo

### 📈 Análise PO

- Tempo médio de espera e atendimento
- Simulação de fila M/M/c
- Gráficos de ocupação e tempo de fila

### 📊 Análise Estatística

- Boxplot e histogramas dos tempos
- Testes de normalidade e aderência
- Intervalos de confiança e testes de hipóteses

---

## 🧠 Aplicações Educacionais

Este projeto é ideal para:

- Exposições técnicas ou feiras escolares
- Ensino interdisciplinar em Estatística, PO e Web
- Análise de sistemas de atendimento em tempo real

---

## 🙋 Contribuições

Contribuições são bem-vindas! Crie um _fork_, abra um _issue_ ou envie um _pull request_.

---

