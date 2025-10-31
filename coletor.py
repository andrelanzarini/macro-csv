import csv
import sqlite3
import os
import time
from datetime import datetime

# Constantes
DIRETORIO = "/mnt/c/Users/alanzari/Downloads/"
ARQUIVO = "dados_investing.csv"
CAMINHO_ARQUIVO = os.path.join(DIRETORIO, ARQUIVO)
DB_NOME = "dados_arqcsv.db"
CODIGOS_SEGURANCA = {"DX", "USD/MXN", "USD/NOK", "USD/NZD", "USD/AUD", "USD/KRW", "USD/CNY", "EUR/USD"}
CODIGO_VIX = "VX"
CODIGOS_PREMERCADO = {"PBR", "VALE.K", "EWZ", "XLF", "XLE", "XLP", "XME", "SOXX.O", "EEM"}

CODIGOS_RISCO = {
    "GC", "HG", "CL", "PBR", "VALE.K", "EWZ", "XLF", "XLE", "XLP", "XME", ".BSESN", ".OSEAX", "ZS",
    "SOXX.O", "1YMM25", "EEM", ".GDOW"
}

def interpretar_variacao(valor):
    return float(valor.strip('%').replace(',', '.'))

def classificar_variacao(codigo, variacao):
    if codigo in CODIGOS_SEGURANCA:
        if variacao > 0.30:
            return 'alta'
        elif variacao < -0.30:
            return 'queda'
        else:
            return 'neutro'
    elif codigo == CODIGO_VIX:
        if variacao > 5:
            return 'alta'
        elif variacao < -5:
            return 'queda'
        else:
            return 'neutro'
    elif codigo in CODIGOS_RISCO:
        if variacao > 0.30:
            return 'queda'
        elif variacao < -0.30:
            return 'alta'
        else:
            return 'neutro'
    else:
        if variacao > 0.30:
            return 'alta'
        elif variacao < 0.30:
            return 'queda'
        else:
            return 'neutro'

def contar_variacoes(dados):
    contagem = {'alta': 0, 'queda': 0, 'neutro': 0}
    for linha in dados:
        codigo = linha[1]
        variacao = interpretar_variacao(linha[3])
        classificacao = classificar_variacao(codigo, variacao)
        contagem[classificacao] += 1
    return contagem

def ler_csv(path):
    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # pular cabeçalho
        return list(reader)

def conectar_banco(path):
    return sqlite3.connect(path)


def obter_premercado(conexao, codigo):
    hoje = datetime.now().strftime('%d-%m-%Y')
    cursor = conexao.cursor()
    cursor.execute("SELECT variacao FROM premercado WHERE data = ? AND codigo = ?", (hoje, codigo))
    row = cursor.fetchone()
    return row[0] if row else None


def inserir_dados(conexao, alta, queda, neutro, hora):
    data_hoje = datetime.now().strftime('%d-%m-%Y')
    with conexao:
        conexao.execute('''
            INSERT INTO mercado (data, hora, alta, queda, neutro) 
            VALUES (?, ?, ?, ?, ?)
        ''', (data_hoje, hora, alta, queda, neutro))
    return hora

def extrair_hora_csv(dados):
    for linha in dados[:3]:
        if len(linha) >= 5 and linha[4].strip():
            try:
                hora_bruta = linha[4].strip()
                hora_formatada = datetime.strptime(hora_bruta, "%H:%M:%S").strftime("%H:%M")
                return hora_formatada
            except ValueError:
                pass  # ignora se não conseguir converter
    return time.strftime('%H:%M')  # fallback se nenhum valor for encontrado

def main():
    while True:
        try:
            dados = ler_csv(CAMINHO_ARQUIVO)
            agora = datetime.now()
            usar_premercado = agora.hour < 10 or (agora.hour == 10 and agora.minute < 30)

            if usar_premercado:
                conn = conectar_banco(DB_NOME)
                for i, linha in enumerate(dados):
                    codigo = linha[1]
                    if codigo in CODIGOS_PREMERCADO:
                        valor_manual = obter_premercado(conn, codigo)
                        if valor_manual is not None:
                            linha[3] = valor_manual
                conn.close()

            contagem = contar_variacoes(dados)
            conn = conectar_banco(DB_NOME)
            hora_csv = extrair_hora_csv(dados)
            hora = inserir_dados(conn, contagem['alta'], contagem['queda'], contagem['neutro'], hora_csv)
        # hora = inserir_dados(conn, contagem['alta'], contagem['queda'], contagem['neutro'])
            print(f"[{hora}] Inserido com sucesso: {contagem}")
            time.sleep(300)  # aguarda 5 minutos
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(60)

if __name__ == '__main__':
    main()
