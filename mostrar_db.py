import sqlite3

# Conectando ao banco de dados
conexao = sqlite3.connect('dados_arqcsv.db')

# Criando um cursor para executar comandos SQL
cursor = conexao.cursor()

# Solicitando o nome da tabela ao usuário
nome_tabela = input("Digite o nome da tabela que deseja listar: ")

try:
    # Obtendo todos os registros da tabela
    cursor.execute(f"SELECT * FROM {nome_tabela}")
    registros = cursor.fetchall()

    # Listando os registros no console
    if registros:
        for registro in registros:
            print(registro)
    else:
        print(f"A tabela '{nome_tabela}' está vazia ou não existe.")

except sqlite3.Error as e:
    print(f"Erro ao acessar o banco de dados: {e}")

finally:
    # Fechando a conexão com o banco de dados
    conexao.close()
