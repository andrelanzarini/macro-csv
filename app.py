from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime, timedelta
import subprocess
import os
import psutil

app = Flask(__name__)

DB_NAME = "dados_arqcsv.db"
coletor_process = None

def criar_tabelas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS premercado (
            data TEXT,
            codigo TEXT,
            variacao TEXT,
            PRIMARY KEY (data, codigo)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mercado (
            data TEXT,
            hora TEXT,
            alta INTEGER,
            queda INTEGER,
            neutro INTEGER
        )
    """)
    conn.commit()
    conn.close()

criar_tabelas()

def get_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    hoje = datetime.now().strftime('%d-%m-%Y')
    cursor.execute("""
        SELECT data, hora, alta, queda, neutro 
        FROM mercado 
        WHERE data = ? 
        ORDER BY hora
    """, (hoje,))
    rows = cursor.fetchall()
    conn.close()

    labels, altas, quedas, neutros = [], [], [], []
    for row in rows:
        label = row[1]  # só a hora
        labels.append(label)
        altas.append(row[2])
        quedas.append(row[3])
        neutros.append(row[4])

    return {
        "labels": labels,
        "alta": altas,
        "queda": quedas,
        "neutro": neutros
    }

def is_process_running(process):
    return process and process.poll() is None

def iniciar_coletor():
    global coletor_process
    if not is_process_running(coletor_process):
        coletor_process = subprocess.Popen(["python3", "coletor.py"], stdout=open("coletor.log", "a"), stderr=subprocess.STDOUT)

def parar_coletor():
    global coletor_process
    if is_process_running(coletor_process):
        coletor_process.terminate()
        coletor_process.wait()
        coletor_process = None

@app.route("/dados")
def dados():
    return jsonify(get_data())

@app.route("/coletor", methods=["POST"])
def toggle_coletor():
    action = request.json.get("acao")
    if action == "iniciar":
        iniciar_coletor()
        return {"status": "iniciado"}
    elif action == "parar":
        parar_coletor()
        return {"status": "parado"}
    return {"status": "invalido"}, 400

@app.route("/status")
def status():
    return jsonify({"ativo": is_process_running(coletor_process)})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/premercado", methods=["GET", "POST"])
def painel_premercado():
    mensagem = ""
    codigos = ["PBR", "VALE.K", "EWZ", "XLF", "XLE", "XLP", "XME", "SOXX.O", "EEM"]
    hoje = datetime.now().strftime('%d-%m-%Y')

    if request.method == "POST":
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        for codigo in codigos:
            variacao = request.form.get(codigo)
            if variacao:  # só insere se o campo não estiver vazio
                cursor.execute("""
                    INSERT OR REPLACE INTO premercado (data, codigo, variacao)
                    VALUES (?, ?, ?)
                """, (hoje, codigo, variacao))

        conn.commit()
        conn.close()
        mensagem = "Dados atualizados com sucesso!"

    # Gera HTML com os campos de edição
    form_linhas = "\n".join([
        f"<tr><td>{codigo}</td><td><input type='text' name='{codigo}' style='width: 80px;' /></td></tr>"
        for codigo in codigos
    ])

    return f"""
    <html>
    <head>
        <title>Pré-Mercado</title>
    </head>
    <body style="font-family: Arial; padding: 20px;">
        <h2>Cadastro de Variações Pré-Mercado</h2>
        <form method="POST">
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
                <tr><th>Código</th><th>Variação (%)</th></tr>
                {form_linhas}
            </table>
            <br>
            <button type="submit" style="padding: 10px;">Salvar Tudo</button>
        </form>
        <p style="color: green;">{mensagem}</p>
        <a href="/" style="margin-top: 20px; display: inline-block;">Voltar para o Dashboard</a>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)
