import time
import constantes

from DAO import insert_into_control_panel, get_control_panel_info, update_control_panel, update_visions, get_db_query
from get_recent_tracks import save_user_recent_tracks
from get_friends import get_api_friends
from generate_artists_ranking import insert_artist_ranking, select_artists_today

from datetime_conversion import timestamp_to_unix


def get_last_scrobble(user):
    query = """
    SELECT max(scrobble_date)
    FROM scrobbles
    WHERE username = %s;
    """
    params = (user,)
    results = get_db_query(query, params)
    if results is None:
        return None
    return results[0][0]

list_of_users = []
list_of_inconsistent_users = []
status = 1

for initial_username in constantes.LIST_OF_INITIAL_USERNAMES:
    list_of_friends = get_api_friends(initial_username)
    list_of_users.extend(list_of_friends)

if len(constantes.LIST_OF_INITIAL_USERNAMES) > 1:
    list_of_users = list(set(list_of_users))

print(f"[main] Usuarios para serem atualizados: {list_of_users}\n")

insert_into_control_panel(f"update_scrobbles_today")
cp_id = get_control_panel_info()

for index, user in enumerate(list_of_users, start=1):
    print(f"{index} - INFORMAÇÕES DO USUÁRIO {user}")
    last_scrobble = timestamp_to_unix(get_last_scrobble(user))
    if last_scrobble is not None:
        last_scrobble += 1 # adicionando 1 segundo a mais para nao pegar o ultimo scrobble duas vezes
    status = save_user_recent_tracks(user, start_date=last_scrobble)
    if status == -1:
        list_of_inconsistent_users.append(user)
    time.sleep(constantes.WAIT_TIME)
    print(f"[main] Todas as informações de {user} já foram coletadas. Ainda faltam {len(list_of_users) - index} usuários.\n")

status = 2

update_visions(constantes.LIST_OF_INITIAL_USERNAMES)
update_control_panel(cp_id, status)

print(f"[main] Atualizando o ranking dos últimos scrobbles ainda não atualizados...")
updated_artists = select_artists_today()
print(f"[main] Foram encontrados {len(updated_artists)} artistas para serem atualizados.")
insert_artist_ranking()
print(f"[main] {len(updated_artists)} artistas foram atualizados.")

print(f"[main] Lista de usuários inconsistentes: {list_of_inconsistent_users}")