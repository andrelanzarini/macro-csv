import sqlite3

# Conectar ao banco de dados de backup
backup_conn = sqlite3.connect('dados_arqcsv.old')
backup_cursor = backup_conn.cursor()

# Conectar ao banco de dados principal
main_conn = sqlite3.connect('dados_arqcsv.db')
main_cursor = main_conn.cursor()

try:
    # Obter todas as tabelas do banco de dados de backup
    backup_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = backup_cursor.fetchall()

    # Transferir os dados de cada tabela
    for table_name in tables:
        table_name = table_name[0]
        
        # Obter os dados da tabela de backup
        backup_cursor.execute(f"SELECT * FROM {table_name}")
        rows = backup_cursor.fetchall()
        
        # Obter o esquema da tabela
        backup_cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in backup_cursor.fetchall()]
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['?' for _ in columns])
        
        # Inserir os dados no banco de dados principal
        main_cursor.executemany(
            f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})",
            rows
        )
        print(f"Dados da tabela '{table_name}' transferidos com sucesso!")

    # Salvar as alterações no banco de dados principal
    main_conn.commit()

except sqlite3.Error as e:
    print(f"Ocorreu um erro: {e}")

finally:
    # Fechar as conexões
    backup_conn.close()
    main_conn.close()
