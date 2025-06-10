# 📊 Simulador de Atendimento

Este repositório apresenta um sistema integrado para simulação de atendimento com geração de senhas, chamadas por atendentes, visualização em painel e análise posterior com foco estatístico e operacional. O projeto é voltado para uso educacional, exposições e estudos em disciplinas como **Pesquisa Operacional**, **Estatística** e **Desenvolvimento Web**.

---

## 📦 Pré-requisitos

- Python 3.10 ou superior
- Git (opcional, para clonar o repositório)

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
├── _proposta          # Proposta do projeto
├── templates          # Templates de documentação
├── samples            # Exemplos de documentação preenchida
├── network            # Guia para estruturação da rede
├── app.py             # Servidor Flask - geração de senhas e API
├── appPO.py           # Página de análise de Pesquisa Operacional (Streamlit)
├── appS.py            # Página de análise Estatística (Streamlit)
├── starserver.py      # Script para iniciar Flask e ambas as páginas Streamlit
├── frontend/          # Interfaces e estilos (HTML, CSS, imagens)
│   ├── atendente.html, painel.html, totem.html
│   ├── atendente.css, painel.css, totem.css
│   └── img/           # Imagens e ícones
├── dados.db           # Banco de dados SQLite com histórico dos atendimentos
└── README.md          # Guia de leitura do projeto
```

---

## 📄 Diretrizes do Projeto

Consulte o arquivo `_proposta/PBL_EC8_2025_02.pdf` para detalhes completos das diretrizes e objetivos.

---

## 🚀 Como Executar o Projeto

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/simulador-atendimento.git
cd simulador-atendimento
```

### 2. (Opcional) Crie um ambiente virtual

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Instale as dependências

```bash
pip install flask streamlit pandas numpy matplotlib seaborn scipy
```

### 4. Execute todos os servidores com um único comando

```bash
python starserver.py
```

Esse script inicializa automaticamente:
- O servidor Flask (`app.py`) para geração e controle de senhas
- A página Streamlit de Estatística (`appS.py`)
- A página Streamlit de Pesquisa Operacional (`appPO.py`)

> **Nota:** O banco de dados `dados.db` será criado automaticamente se não existir.

---

## 🌐 Acessando as Interfaces

- **Totem:** abra `frontend/totem.html` em um navegador → Geração de senha por serviço
- **Painel:** abra `frontend/painel.html` em um navegador → Exibição pública da próxima senha chamada
- **Atendente:** abra `frontend/atendente.html` em um navegador → Tela de gerenciamento e chamada das senhas
- **Análise PO e Estatística:** acesse o Streamlit em `http://localhost:8501` (Estatística) e `http://localhost:8502` (PO)

> **Importante:** Garanta que o backend (`app.py`) esteja rodando para que as páginas funcionem corretamente.

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

