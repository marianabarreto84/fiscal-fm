import time
import constantes
from DAO import create_scrobbles_table
from DAO import execute_db_statement
from DAO import get_db_query
from get_recent_tracks import save_user_recent_tracks
from get_friends import get_friends


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
    statement = """
    REFRESH MATERIALIZED VIEW stats_artists;
    """
    params = ()
    execute_db_statement(statement, params)
    print(f"[update_stats] Visão stats_artists atualizada.")

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

list_of_users = []
status = 1

for initial_username in constantes.LIST_OF_INITIAL_USERNAMES:
    list_of_friends = get_friends(initial_username)
    list_of_users.append(list_of_friends)

list_of_users_set = set().union(*list_of_users)
list_of_users = list(list_of_users_set)

print(f"[main] Usuarios para serem atualizados: {list_of_users}\n")

insert_into_control_panel(f"update_scrobbles")
cp_id = get_control_panel_info()

for user in list_of_users:
    status = save_user_recent_tracks(user)
    if status == -1:
        print(f"[main] Voltando para a main para finalizar a tentativa de inserção.")
        break
    time.sleep(constantes.WAIT_TIME)
    print(f"[main] Todas as informações de {user} já foram coletadas.\n")

status = 2

update_visions(constantes.LIST_OF_INITIAL_USERNAMES)
update_control_panel(cp_id, status)
