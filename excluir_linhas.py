import sqlite3
import argparse

# Argumentos de linha de comando
parser = argparse.ArgumentParser(description="Excluir linha da tabela 'mercado' por data e hora.")
parser.add_argument("db", help="Caminho para o arquivo .db")
parser.add_argument("data", help="Data no formato dd-mm-aaaa")
parser.add_argument("hora", help="Hora no formato HH:MM")

args = parser.parse_args()

# Conecta no banco
conn = sqlite3.connect(args.db)
cursor = conn.cursor()

# Executa o delete
query = "DELETE FROM mercado WHERE data = ? AND hora = ?"
cursor.execute(query, (args.data, args.hora))
conn.commit()

print(f"Linhas excluídas: {cursor.rowcount}")

conn.close()

