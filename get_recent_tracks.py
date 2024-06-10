import requests
import constantes
import time
import pytz
import sys
from DAO import get_db_query, save_to_database
from datetime import datetime


def unix_to_timestamp(unix_time, in_utc=True):
    if unix_time is None:
        return
    # Define o fuso horário de Brasília
    brt = pytz.timezone('America/Sao_Paulo')
    if in_utc:
        # Converte o timestamp Unix para um objeto de data e hora UTC
        dt_utc = datetime.utcfromtimestamp(unix_time)
        # Adiciona o fuso horário de Brasília ao objeto de data e hora
        dt_brt = dt_utc.replace(tzinfo=pytz.utc).astimezone(brt)
    else:
        # Retorna o timestamp diretamente no horário de Brasília
        dt_brt = datetime.fromtimestamp(unix_time, brt)
    return dt_brt


def timestamp_to_unix(dt, in_utc=False):
    if dt is None:
        return
    if in_utc:
        # Retorna o timestamp diretamente em UTC
        return int(dt.timestamp())
    # Define o fuso horário de Brasília
    brt = pytz.timezone('America/Sao_Paulo')
    # Converte o objeto de data e hora para o fuso horário de Brasília
    dt_brt = brt.localize(dt)
    # Converte o objeto de data e hora de Brasília para UTC
    dt_utc = dt_brt.astimezone(pytz.utc)
    # Converte o objeto de data e hora UTC para timestamp Unix
    unix_time = int(dt_utc.timestamp())
    return unix_time


def format_datetime(unix_time, in_utc=True):
    if unix_time is None:
        return
    dt = unix_to_timestamp(unix_time, in_utc=in_utc)
    return dt.strftime("%d/%m/%Y - %H:%M:%S")


def get_user_info(username, api_key):
    # Defina a URL da API com os parâmetros necessários
    url = 'https://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'user.getinfo',
        'user': username,
        'api_key': api_key,
        'format': 'json'
    }
    # Faça a requisição GET à API
    response = requests.get(url, params=params)
    
    # Verifique se a requisição foi bem-sucedida
    if response.status_code == 200:
        data = response.json()
        # Extrai o playcount dos dados retornados
        return data
    return


def get_api_playcount(data):
    return int(data['user']['playcount'])


def get_api_registered(data):
    return int(data['user']['registered']['unixtime'])


def get_recent_tracks_info(username, api_key, limit=200):
    # URL da API do Last.fm para obter as informações do usuário
    url = 'https://ws.audioscrobbler.com/2.0/'
    
    # Parâmetros da requisição
    params = {
        'method': 'user.getrecenttracks',
        'user': username,
        'api_key': api_key,
        'limit': limit,
        'format': 'json'
    }
    
    # Faz a requisição à API do Last.fm
    response = requests.get(url, params=params)
    
    # Verifica se a requisição foi bem-sucedida
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"[get_recent_tracks_info] Erro ao acessar a API: {response.text}")
        exit()
        return None


def get_api_last_scrobble(rt_info):
    # Extrai a data do último scrobble em formato Unix
    for track in rt_info['recenttracks']['track']:
        if track.get('date', None) is None:
            continue
        else:
            unix_time = int(track['date']['uts'])
            return unix_time
    return None


def get_api_total_pages(username, api_key, start_date=None, end_date=None, page=1, limit=200):
    time_limit_str = ""
    if start_date is not None:
        time_limit_str += f"&from={start_date}"
    elif end_date is not None:
        time_limit_str += f"&to={end_date}"
    url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={api_key}&limit={limit}&format=json&page={page}{time_limit_str}"
    response = requests.get(url)
    
    # Verifica se a requisição foi bem-sucedida
    if response.status_code == 200:
        data = response.json()
        return int(data['recenttracks']['@attr']['totalPages'])
    else:
        print(f"[get_api_total_pages] Erro na requisição: {response.status_code} - {response.text}")
        return


def get_api_total_scrobbles(rt_info):
    return int(rt_info['recenttracks']['@attr']['total'])


def get_db_playcount(username):
    query = "SELECT COUNT(*) FROM scrobbles WHERE username = %s"
    params = (username,)
    result = get_db_query(query, params)
    if len(result) != 0:
        return result[0][0]
    return int(result)


def get_db_first_scrobble(username):
    query = "SELECT scrobble_date FROM scrobbles WHERE username = %s ORDER BY scrobble_date ASC LIMIT 1;"
    params = (username,)
    result = get_db_query(query, params)
    if len(result) != 0:
        return result[0][0]
    return result


def get_db_last_scrobble(username):
    query = "SELECT scrobble_date FROM scrobbles WHERE username = %s ORDER BY scrobble_date DESC LIMIT 1;"
    params = (username,)
    result = get_db_query(query, params)
    if len(result) != 0:
        return result[0][0]
    return result


def get_recent_tracks(username, api_key, start_date=None, end_date=None, page=1, limit=200):
    time_limit_str = ""
    if start_date is not None:
        time_limit_str += f"&from={start_date}"
    elif end_date is not None:
        time_limit_str += f"&to={end_date}"
    url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={api_key}&limit={limit}&format=json&page={page}{time_limit_str}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"[get_recent_tracks] Não foi possível acessar a API: {response.text}")
        exit()
    data = response.json()
    recent_tracks = []
    if len(data['recenttracks']['track']) == 0:
        print("[get_recent_tracks] A lista de scrobbles está vazia.")
        return recent_tracks
    if type(data['recenttracks']['track']) == list:
        lista_tracks_resposta = data['recenttracks']['track']
    else:
        lista_tracks_resposta = [data['recenttracks']['track']]
    primeira_faixa = lista_tracks_resposta[0]
    if primeira_faixa.get('@attr', {'nowplaying': 'false'})['nowplaying'] == 'true':
        # print("[get_recent_tracks] A primeira faixa está sendo tocada, vai ser pulada.")
        lista_tracks_resposta = lista_tracks_resposta[1:]
    for track in lista_tracks_resposta:
        if type(track) != dict:
            print(track)
            print("[get_recent_tracks] Não é possível continuar.")
            return
        track_info = {}
        track_info['user'] = username
        track_info['artist'] = track['artist']['#text']
        track_info['track'] = track['name']
        track_info['album'] = track['album']['#text']
        track_info['date'] = unix_to_timestamp(int(track['date']['uts']))
        recent_tracks.append(track_info)
    return recent_tracks


def save_user_recent_tracks(user):
    user_info = get_user_info(user, constantes.API_KEY)
    rt_info = get_recent_tracks_info(user, constantes.API_KEY)

    api_playcount = get_api_playcount(user_info)
    api_registered = get_api_registered(user_info)
    api_last_scrobble = get_api_last_scrobble(rt_info)
    api_total_scrobbles = get_api_total_scrobbles(rt_info)

    db_playcount = get_db_playcount(user)
    db_first_scrobble = get_db_first_scrobble(user)
    db_last_scrobble = get_db_last_scrobble(user)

    print(f"INFORMAÇÕES DO USUÁRIO {user.upper()}")
    print(f"[save_user_recent_tracks] Total de Scrobbles da API: {api_playcount} - Total de Scrobbles do DB: {db_playcount}")

    if db_playcount == api_playcount:
        print("[save_user_recent_tracks] Esse usuário já teve todos os scrobbles coletados.")
        return
    elif db_playcount > api_playcount:
        print("[save_user_recent_tracks] Esse usuário possui mais scrobbles no banco do que a API informe. Tente reinserir os scrobbles para garantir a consistência dos dados.")
        return

    start_date = None
    end_date = None

    if db_playcount > 0:
        if timestamp_to_unix(db_last_scrobble) < api_last_scrobble:
            start_date = timestamp_to_unix(db_last_scrobble, in_utc=False) + 1
        elif timestamp_to_unix(db_first_scrobble) > api_registered:
            end_date = timestamp_to_unix(db_first_scrobble, in_utc=False) - 1
    
    api_total_pages = get_api_total_pages(user, constantes.API_KEY, start_date, end_date)
    print(f"[save_user_recent_tracks] Faltam inserir {api_playcount - db_playcount} scrobbles - Total de Páginas: {api_total_pages}")
    print(f"[save_user_recent_tracks] Período de Scrobbles de acordo com a API: {format_datetime(api_registered)} até {format_datetime(api_last_scrobble)}")
    if db_playcount > 0:
        print(f"[save_user_recent_tracks] Período de Scrobbles de acordo com o DB: {db_first_scrobble} até {db_last_scrobble}")


    if start_date is None and end_date is None and db_playcount > 0:
        print(f"[save_user_recent_tracks] Aparentemente está tudo certo com o usuário mas uma inconsistência foi gerada com o last fm e nem todos os dados foram coletados corretamente.")
        print(f"[save_user_recent_tracks] Insira os dados de {user} novamente.")
        return -1
    elif start_date is None and end_date is None:
        print(f"[save_user_recent_tracks] Coletando scrobbles do usuário {user} sem limite de tempo.")
    else:
        print(f"[save_user_recent_tracks] Coletando scrobbles do usuário {user} de {format_datetime(start_date, in_utc=True)} até {format_datetime(end_date, in_utc=True)}")
        # print(f"[save_user_recent_tracks] Em UNIX: De {start_date} até {end_date}")

    # print(f"[save_user_recent_tracks] Esperando tempo inicial para coleta...\n")
    time.sleep(constantes.WAIT_TIME * 2)

    for page in range(1, api_total_pages + 1):
        recent_tracks = get_recent_tracks(user, constantes.API_KEY, start_date=start_date, end_date=end_date, page=page)
        if len(recent_tracks) == 0:
            print(f"[save_user_recent_tracks] Não foi possível coletar mais scrobbles, finalizando coleta do usuário.")
            break
        db_playcount += save_to_database(recent_tracks)
        print(f"[save_user_recent_tracks] Página: {page} ({len(recent_tracks)}) | Quantidade de scrobbles inseridos: {db_playcount} | Progresso: {(db_playcount/api_total_scrobbles)*100:.2f}%")
        time.sleep(constantes.WAIT_TIME)

    return


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("[get_recent_tracks] Especifique o nome de usuário na linha de comando.\n\t- Formato: python get_recent_tracks.py <nome_de_usuario>")
        exit()

    user = sys.argv[1]
    save_user_recent_tracks(user)

