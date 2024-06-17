import psycopg2
import constantes

def connect():
    try:
        conn = psycopg2.connect(
            dbname=constantes.DB_NAME,
            user=constantes.DB_USER,
            password=constantes.DB_PASSWORD,
            host=constantes.DB_HOST,
            port=constantes.DB_PORT
        )
        return conn
    except Exception as e:
        print(f"[connect] Não foi possível se conectar ao banco: {e}.")
        exit()
    return


def create_scrobbles_table():
    conn = connect()
    cursor = conn.cursor()

    # Criar uma tabela se ela ainda não existir
    cursor.execute("""CREATE TABLE IF NOT EXISTS scrobbles (username TEXT, scrobble_date TIMESTAMP, artist TEXT, track TEXT, album TEXT, insertion_date TIMESTAMP DEFAULT now());""")
    conn.commit()
    
    # Feche a conexão com o banco de dados
    cursor.close()
    conn.close()
    return


def get_db_query(query, params):
    conn = connect()
    cursor = conn.cursor()
    
    # Execute a consulta SQL para contar os scrobbles do usuário
    try:
        cursor.execute(query, params)
    except Exception as e:
        print(f"[get_db_query] Exceção: {e}")
        return
    result = cursor.fetchall()
    
    # Feche a conexão com o banco de dados
    cursor.close()
    conn.close()

    return result


def execute_db_statement(query, params):
    conn = connect()
    cursor = conn.cursor()
    
    # Execute a consulta SQL para contar os scrobbles do usuário
    try:
        cursor.execute(query, params)
        conn.commit()
    except psycopg2.errors.UniqueViolation as e:
        conn.rollback()
        print(f"[execute_db_statement] Existe alguma condição de unique que está ativada indicando que os atributos da restrição já foram inseridos previamente.")
        print(f"[execute_db_statement] Exceção: {e}")
        return
    except Exception as e:
        conn.rollback()
        print(f"[execute_db_statement] Exceção: {e}")
        return

    # Feche a conexão com o banco de dados
    cursor.close()
    conn.close()
    
    return


def save_to_database(recent_tracks):
    # Conectar ao banco de dados PostgreSQL
    conn = connect()
    cursor = conn.cursor()
    
    # Inserir as faixas recentes na tabela
    insertions = 0
    for track in recent_tracks:
        try:
            cursor.execute("""
            INSERT INTO scrobbles (username, artist, track, album, scrobble_date)
            VALUES (%s, %s, %s, %s, %s)
            """, (track['user'], track['artist'], track['track'], track['album'], track['date']))
            # print(f"[save_to_databse] LOG REPORT: {track['user']} - {track['track']} - {track['date']}")
            insertions += 1
        except Exception as e:
            print(f"[save_to_database] Exceção: {e}")
            conn.rollback()
            continue
    
    # Commit e fechar a conexão
    conn.commit()
    conn.close()
    return insertions


def insert_into_control_panel(chave):
    statement = """
    INSERT INTO control_panel (start_date, chave, table_name, status)
    VALUES (now(), %s, 'scrobbles', 0);
    """
    params = (chave,)
    execute_db_statement(statement, params)
    return


def get_control_panel_info():
    query = """
    SELECT max(id) FROM control_panel;
    """
    params = ()
    result = get_db_query(query, params)
    if len(result) == 0:
        return None
    cp_id = int(get_db_query(query, params)[0][0])
    return cp_id

def update_control_panel(cp_id, status):
    statement = """
    UPDATE control_panel SET end_date = now(), status = %s WHERE id = %s
    """
    params = (status, cp_id)
    execute_db_statement(statement, params)
    print(f"[update_control_panel] Painel de controle atualizado corretamente.")
    return

def update_visions(list_of_initial_usernames):
    print("[update_visions] Atualizando as visões...")

    statement = """
    REFRESH MATERIALIZED VIEW stats_artists;
    """
    params = ()
    # execute_db_statement(statement, params)
    # print(f"[update_stats] Visão stats_artists atualizada.")

    statement = """
    REFRESH MATERIALIZED VIEW scrobbles24;
    """
    params = ()
    execute_db_statement(statement, params)
    print(f"[update_stats] Visão scrobbles24 atualizada.")

    for username in list_of_initial_usernames:
        initial_abbv = "mb"
        if username == "vicisnotonfire":
            initial_abbv = "vic"
        statement = f"""
        REFRESH MATERIALIZED VIEW scrobbles_{initial_abbv};
        """
        params = ()
        execute_db_statement(statement, params)
        print(f"[update_stats] Visão scrobbles_{initial_abbv} atualizada.")
    return