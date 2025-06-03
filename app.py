from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from datetime import datetime
import sqlite3
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

app = Flask(__name__)
CORS(app)

# Configurações
DB_PATH = 'dados.db'
SERVICOS_VALIDOS = {"hospital", "banco", "restaurante"}
GUICHES_VALIDOS = set(range(1, 6))
MESAS_VALIDAS = set(range(1, 26))
HORARIO_BANCO = (10, 23)
LIMITE_BANCO = 500
TURNOS_RESTAURANTE = {
    "cafe": (7, 10),
    "almoco": (11, 15),
    "jantar": (17, 22)
}


def validar_banco():
    hora = datetime.now().hour
    if not (HORARIO_BANCO[0] <= hora < HORARIO_BANCO[1]):
        return "Fora do horário de funcionamento do banco (10h às 16h)."
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM senhas WHERE servico='banco'")
        if cursor.fetchone()[0] >= LIMITE_BANCO:
            return "Limite diário de senhas do banco atingido (500)."
    return None


def validar_restaurante():
    hora = datetime.now().hour
    turno_valido = any(start <= hora < end for start, end in TURNOS_RESTAURANTE.values())
    if not turno_valido:
        return "Fora do horário de funcionamento do restaurante."
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM senhas WHERE servico='restaurante' AND status='na_fila'")
        if cursor.fetchone()[0] >= len(MESAS_VALIDAS):
            return "Capacidade máxima do restaurante atingida neste turno."
    return None


@app.route('/nova_senha', methods=['POST'])
def nova_senha():
    dados = request.json
    servico = dados.get('servico')
    prioritario = dados.get('prioritario', False)

    if servico not in SERVICOS_VALIDOS:
        return jsonify({"erro": "Serviço inválido"}), 400

    tipo = 'P' if prioritario else 'C'
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    horario_chegada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if servico == 'banco':
        erro = validar_banco()
        if erro:
            return jsonify({"erro": erro}), 403
    elif servico == 'restaurante':
        erro = validar_restaurante()
        if erro:
            return jsonify({"erro": erro}), 403

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Conta quantas senhas já foram geradas hoje para esse serviço/tipo
        cursor.execute('''
            SELECT COUNT(*) FROM senhas
            WHERE servico=? AND tipo=? AND data=?
        ''', (servico, tipo, data_hoje))
        total = cursor.fetchone()[0] + 1
        numero = str(total).zfill(3)

        prefixo = {'banco': 'BAN', 'hospital': 'HOS', 'restaurante': 'RES'}[servico]
        senha = f"{prefixo}-{tipo}{numero}"

        cursor.execute('''
            INSERT INTO senhas (servico, senha, tipo, status, horario_chegada, data)
            VALUES (?, ?, ?, 'na_fila', ?, ?)
        ''', (servico, senha, tipo, horario_chegada, data_hoje))
        conn.commit()

    return jsonify({
        "mensagem": "Senha registrada com sucesso!",
        "senha": senha,
        "horario": horario_chegada
    })


@app.route('/chamar_senha', methods=['POST'])
def chamar_senha():
    dados = request.json
    servico = dados.get('servico')
    guiche = dados.get('guiche')
    guiche = int(dados.get('guiche'))  


    if servico not in SERVICOS_VALIDOS:
        return jsonify({"erro": "Serviço inválido"}), 400

    try:
        guiche = int(guiche)
        if servico in {"banco", "hospital"} and guiche not in GUICHES_VALIDOS:
            raise ValueError()
        if servico == "restaurante" and guiche not in MESAS_VALIDAS:
            raise ValueError()
    except:
        return jsonify({"erro": "Guichê/Mesa inválido(a)"}), 400

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM senhas
            WHERE servico=? AND guiche=? AND status='chamada'
        ''', (servico, guiche))
        if cursor.fetchone()[0] > 0:
            return jsonify({"erro": f"{'Guichê' if servico != 'restaurante' else 'Mesa'} {guiche} está ocupado(a)."}), 400

        cursor.execute('''
            SELECT id, senha, tipo FROM senhas
            WHERE servico=? AND status='na_fila'
            ORDER BY horario_chegada ASC LIMIT 1
        ''', (servico,))
        resultado = cursor.fetchone()

        if not resultado:
            return jsonify({"erro": "Nenhuma senha na fila."}), 404

        id_senha, codigo, tipo = resultado
        horario_chamada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            UPDATE senhas
            SET status='chamada', guiche=?, horario_chamada=?
            WHERE id=?
        ''', (guiche, horario_chamada, id_senha))
        conn.commit()

    return jsonify({
        "senha": codigo,
        "guiche": guiche,
        "horario": horario_chamada
    })
@app.route('/em_atendimento', methods=['POST'])
def em_atendimento():
    dados = request.json
    servico = dados.get('servico')
    guiche = dados.get('guiche')

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT senha, guiche, horario_chamada
            FROM senhas
            WHERE servico=? AND guiche=? AND status='chamada'
        ''', (servico, guiche))
        dados = cursor.fetchall()

    return jsonify([
        {"senha": s, "guiche": g, "horario": h}
        for s, g, h in dados
    ])

@app.route('/senhas_em_atendimento', methods=['GET'])
def senhas_em_atendimento():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT servico, senha, guiche, horario_chamada
            FROM senhas
            WHERE status = 'chamada'
            ORDER BY servico, horario_chamada
        ''')
        resultado = cursor.fetchall()

    return jsonify([
        {"servico": s, "senha": senha, "guiche": g, "horario": h}
        for s, senha, g, h in resultado
    ])


@app.route('/finalizar_atendimento', methods=['POST'])
def finalizar_atendimento():
    dados = request.json
    servico = dados.get('servico')
    senha = dados.get('senha')

    if servico not in SERVICOS_VALIDOS:
        return jsonify({"erro": "Serviço inválido"}), 400

    horario_final = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE senhas
            SET status='finalizada', horario_finalizacao=?
            WHERE servico=? AND senha=? AND status='chamada'
        ''', (horario_final, servico, senha))
        conn.commit()

    return jsonify({"mensagem": f"Atendimento finalizado para senha {senha}."})


@app.route('/painel/<servico>', methods=['GET'])
def painel_por_servico(servico):
    if servico not in SERVICOS_VALIDOS:
        return jsonify({"erro": "Serviço inválido"}), 400

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT senha, guiche FROM senhas
            WHERE servico=? AND status='chamada'
            ORDER BY horario_chamada DESC
        ''', (servico,))
        chamadas = [{"senha": s, "guiche": g} for s, g in cursor.fetchall()]

        cursor.execute('''
            SELECT senha FROM senhas
            WHERE servico=? AND status='na_fila'
            ORDER BY horario_chegada ASC
        ''', (servico,))
        espera = [{"senha": s[0]} for s in cursor.fetchall()]

        cursor.execute('''
            SELECT senha, guiche FROM senhas
            WHERE servico=? AND status='finalizada'
            ORDER BY horario_finalizacao DESC
            LIMIT 5
        ''', (servico,))
        finalizadas = [{"senha": s, "guiche": g} for s, g in cursor.fetchall()]

    return jsonify({
        "chamadas": chamadas,
        "espera": espera,
        "finalizadas": finalizadas
    })

@app.route('/senhas_em_espera', methods=['GET'])
def senhas_em_espera():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT servico, senha, horario_chegada
            FROM senhas
            WHERE status = 'na_fila'
            ORDER BY servico, horario_chegada
        ''')
        dados = cursor.fetchall()

    return jsonify([
        {"servico": servico, "senha": senha, "horario": horario}
        for servico, senha, horario in dados
    ])


@app.route('/exportar_csv')
def exportar_csv():
    import sqlite3
    import pandas as pd

    conn = sqlite3.connect('dados.db')
    df = pd.read_sql_query('SELECT * FROM senhas', conn)
    conn.close()

  
    df.to_csv('dados_filas.csv', index=False)
    return jsonify({"mensagem": "CSV exportado com sucesso"})



@app.route('/')
def home():
    return "ok"


if __name__ == '__main__':
    app.run(debug=True)
