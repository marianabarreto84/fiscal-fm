import time
import constantes
from DAO import create_scrobbles_table
from DAO import execute_db_statement
from DAO import get_db_query
from DAO import insert_into_control_panel, get_control_panel_info, update_control_panel, update_visions
from get_recent_tracks import save_user_recent_tracks
from get_friends import get_friends

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

for index, user in enumerate(list_of_users, start=1):
    print(f"{index} - INFORMAÇÕES DO USUÁRIO {user.upper()}")
    status = save_user_recent_tracks(user)
    time.sleep(constantes.WAIT_TIME)
    print(f"[main] Todas as informações de {user} já foram coletadas. Ainda faltam {len(list_of_users) - index} usuários.\n")

status = 2

update_visions(constantes.LIST_OF_INITIAL_USERNAMES)
update_control_panel(cp_id, status)
