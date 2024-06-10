import os
import sqlite3

def recreate_database(database_file):
    # Verificar se o arquivo de banco de dados existe
    if os.path.exists(database_file):
        # Excluir o arquivo de banco de dados existente
        os.remove(database_file)
    
    # Criar um novo arquivo de banco de dados
    conn = sqlite3.connect(database_file)
    conn.close()

# Substitua 'recent_tracks.db' pelo nome do seu arquivo de banco de dados
recreate_database('lastfm.db')