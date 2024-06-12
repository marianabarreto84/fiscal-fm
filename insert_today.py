import time
import pytz
import constantes

from DAO import insert_into_control_panel, get_control_panel_info, update_control_panel, update_visions
from get_recent_tracks import save_user_recent_tracks
from get_friends import get_friends
from datetime import datetime, timedelta
from generate_artist_ranking import select_updated_artists, update_artist_ranking

def get_today_brt_unix():
    # Define o fuso horário de Brasília
    brt = pytz.timezone('America/Sao_Paulo')

    # Obtém a data e hora atual no fuso horário de Brasília
    now_brt = datetime.now(brt)

    # Ajusta para 00:00:00 de hoje
    today_midnight_brt = now_brt.replace(hour=0, minute=0, second=0, microsecond=0)

    # Converte para timestamp Unix
    unix_timestamp = int(today_midnight_brt.timestamp())

    return unix_timestamp

list_of_users = []
status = 1

for initial_username in constantes.LIST_OF_INITIAL_USERNAMES:
    list_of_friends = get_friends(initial_username)
    list_of_users.append(list_of_friends)

list_of_users_set = set().union(*list_of_users)
list_of_users = list(list_of_users_set)

print(f"[main] Usuarios para serem atualizados: {list_of_users}\n")

insert_into_control_panel(f"update_scrobbles_today")
cp_id = get_control_panel_info()

for index, user in enumerate(list_of_users, start=1):
    print(f"{index} - INFORMAÇÕES DO USUÁRIO {user.upper()}")
    status = save_user_recent_tracks(user, start_date=get_today_brt_unix())
    time.sleep(constantes.WAIT_TIME)
    print(f"[main] Todas as informações de {user} já foram coletadas. Ainda faltam {len(list_of_users) - index} usuários.\n")

status = 2

update_visions(constantes.LIST_OF_INITIAL_USERNAMES)
update_control_panel(cp_id, status)

print(f"[main] Atualizando o ranking dos últimos scrobbles ainda não atualizados...")
updated_artists = select_updated_artists()
print(f"[main] Foram encontrados {len(updated_artists)} artistas para serem atualizados.")
for index, artist in enumerate(updated_artists):
    print(f"[main] Atualizando artista: {artist}. ({(index/len(updated_artists)*100):.2f}%)")
    update_artist_ranking(artist)
print(f"[main] {len(updated_artists)} artistas foram atualizados.")