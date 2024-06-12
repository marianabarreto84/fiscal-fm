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


def date_to_unix(date_string):
    # Parse da data string para um objeto datetime
    date_obj = datetime.strptime(date_string, '%Y-%m-%d')

    # Define o fuso horário de Brasília
    brt = pytz.timezone('America/Sao_Paulo')

    # Combina a data com o horário de meia-noite em BRT
    datetime_brt = brt.localize(datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, 0))

    # Converte para timestamp Unix
    timestamp_unix = int(datetime_brt.timestamp())

    return timestamp_unix

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

def get_api_first_scrobble(username, api_key, page, limit=200):
    # URL da API do Last.fm para obter as informações do usuário
    url = 'https://ws.audioscrobbler.com/2.0/'
    
    # Parâmetros da requisição
    params = {
        'method': 'user.getrecenttracks',
        'user': username,
        'api_key': api_key,
        'limit': limit,
        'page': page,
        'format': 'json'
    }
    
    # Faz a requisição à API do Last.fm
    response = requests.get(url, params=params)
    
    # Verifica se a requisição foi bem-sucedida
    if response.status_code == 200:
        data = response.json()
        if len(data['recenttracks']['track']) > 0:
            track = data['recenttracks']['track'][-1] # Pega o ultimo porque se tiver uma musica tocando no momento ela vai ser retornada como a primeira
            unix_time = int(track['date']['uts'])
            return unix_time
        else:
            print(f"[get_api_first_scrobble] Nenhuma track foi retornada. Dados: {data}")
    else:
        print(f"[get_api_first_scrobble] Erro ao acessar a API: {response.text}")
        exit()
        return None


def get_api_page_count(username, api_key, start_date=None, end_date=None, page=1, limit=200):
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
        print(f"[get_api_page_count] Erro na requisição: {response.status_code} - {response.text}")
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


def get_recent_tracks(username, api_key, start_date=None, end_date=None, page=1, limit=200, tentativas=0):
    time_limit_str = ""
    if start_date is not None:
        time_limit_str += f"&from={start_date}"
    if end_date is not None:
        time_limit_str += f"&to={end_date}"
    url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={api_key}&limit={limit}&format=json&page={page}{time_limit_str}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"[get_recent_tracks] Erro {response.status_code}: {response.text}")
        if tentativas < 5:
            tentativas += 1
            print(f"[get_recent_tracks] Tentando novamente... (tentativa = {tentativas})")
            recent_tracks = get_recent_tracks(username, api_key, start_date=start_date, end_date=start_date, page=page, tentativas=tentativas)
            return recent_tracks
        print(f"[get_recent_tracks] Limite de tentativas estourado. Tente novamente mais tarde")
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


def attempt_fix_inconsistency(user, api_key, api_playcount, db_playcount, start_date=None, end_date=None, page=1, limit=200, tentativas=0):
    track_count = 1
    while db_playcount < api_playcount:
        recent_tracks = get_recent_tracks(user, api_key, start_date=start_date, end_date=end_date, page=page, limit=limit, tentativas=tentativas)
        
        if not recent_tracks:
            break
        
        for track in recent_tracks:
            # Verificar se o scrobble já existe no banco de dados
            query = """
            SELECT COUNT(1)
            FROM scrobbles
            WHERE username = %s
            AND artist = %s AND track = %s AND album = %s
            AND scrobble_date = %s
            """
            params = (user, track['artist'], track['track'], track['album'], track['date'])
            result = get_db_query(query, params)
            
            if result[0][0] == 0:  # Se o scrobble não existe, insira no banco de dados
                print(f"[attempt_fix_inconsistency] {track['track']} - Data do Scrobble: {track['date']} - {(db_playcount/api_playcount)*100:.2f}%")
                save_to_database([track])
                db_playcount += 1  # Atualizar contagem de scrobbles no banco
            else:
                print(f"[attempt_fix_inconsistency] {track['date']} - {db_playcount} de {api_playcount} tracks já foram inseridas. {(db_playcount/api_playcount)*100:.2f}%")

            if db_playcount == api_playcount:
                break
            track_count += 1
        
        page += 1
        time.sleep(constantes.WAIT_TIME)
    
    print(f"[attempt_fix_inconsistency] Tentativa de correção de inconsistência concluída.")
    return 



def save_user_recent_tracks(user, start_date=None, end_date=None):
    user_info = get_user_info(user, constantes.API_KEY)
    rt_info = get_recent_tracks_info(user, constantes.API_KEY)

    api_playcount = get_api_playcount(user_info)
    api_registered = get_api_registered(user_info)
    api_last_scrobble = get_api_last_scrobble(rt_info)
    api_total_scrobbles = get_api_total_scrobbles(rt_info)
    api_total_pages = get_api_page_count(user, constantes.API_KEY)
    api_first_scrobble = get_api_first_scrobble(user, constantes.API_KEY, api_total_pages) # Lembrando que nesse caso o limite tem que ser o mesmo do de cima

    db_playcount = get_db_playcount(user)
    db_first_scrobble = timestamp_to_unix(get_db_first_scrobble(user), in_utc=False)
    db_last_scrobble = timestamp_to_unix(get_db_last_scrobble(user), in_utc=False)

    print(f"[save_user_recent_tracks] Total de Scrobbles da API: {api_playcount} - Total de Scrobbles do DB: {db_playcount}")

    if db_playcount == api_playcount:
        print("[save_user_recent_tracks] Esse usuário já teve todos os scrobbles coletados.")
        return
    elif db_playcount > api_playcount:
        print("[save_user_recent_tracks] Esse usuário possui mais scrobbles no banco do que a API informe. Tente reinserir os scrobbles para garantir a consistência dos dados.")
        return

    # CENARIO EM QUE JA FORAM INSERIDOS SCROBBLES DAQUELE USUARIO
    if db_playcount > 0:
        if start_date is not None and end_date is None:
            if db_last_scrobble > start_date:
                start_date = db_last_scrobble + 1
                end_date = None
        elif end_date is not None and start_date is None:
            if db_first_scrobble < end_date:
                start_date = None
                end_date = db_first_scrobble - 1
        elif start_date is None and db_first_scrobble < api_last_scrobble:
            start_date = db_last_scrobble + 1
            end_date = None
        elif end_date is None and db_last_scrobble > api_first_scrobble:
            start_date = None
            end_date = db_first_scrobble - 1
        if start_date is not None and end_date is not None:
            if start_date > end_date:
                print(f"[save_user_recent_tracks] A data de início da coleta ({format_datetime(start_date)}) é maior do que a do fim ({format_datetime(start_date)}).")
    
    api_page_count = get_api_page_count(user, constantes.API_KEY, start_date, end_date)

    print(f"[save_user_recent_tracks] Faltam inserir {api_playcount - db_playcount} scrobbles - Total de Páginas: {api_page_count}")
    print(f"[save_user_recent_tracks] Período de Scrobbles de acordo com a API: {format_datetime(api_first_scrobble)} até {format_datetime(api_last_scrobble)}")
    if db_playcount > 0:
        print(f"[save_user_recent_tracks] Período de Scrobbles de acordo com o DB: {format_datetime(db_first_scrobble)} até {format_datetime(db_last_scrobble)}")


    if start_date is None and end_date is None and db_playcount > 1:
        if (api_playcount - db_playcount) <= 1:
            print(f"[save_user_recent_tracks] A inconsistência gerada é de apenas 1 scrobble. Não é necessário consertá-la imediatamente.")
            return
        print(f"[save_user_recent_tracks] Uma inconsistência foi gerada com o last fm e nem todos os dados foram coletados corretamente.")
        attempt_fix_inconsistency(user, constantes.API_KEY, api_playcount, db_playcount)
        return
    elif start_date is None and end_date is None:
        print(f"[save_user_recent_tracks] Coletando scrobbles do usuário {user} sem limite de tempo.")
    else:
        print(f"[save_user_recent_tracks] Coletando scrobbles do usuário {user} de {format_datetime(start_date, in_utc=True)} até {format_datetime(end_date, in_utc=True)}")

    time.sleep(constantes.WAIT_TIME * 2)

    for page in range(1, api_page_count + 1):
        recent_tracks = get_recent_tracks(user, constantes.API_KEY, start_date=start_date, end_date=end_date, page=page)
        if len(recent_tracks) == 0:
            print(f"[save_user_recent_tracks] Não foi possível coletar mais scrobbles, finalizando coleta do usuário.")
            break
        if api_playcount <= db_playcount:
            print(f"[save_user_recent_tracks] A quantidade de scrobbles já foi atingida.")
            break
        db_playcount += save_to_database(recent_tracks)
        print(f"[save_user_recent_tracks] Página: {page} ({len(recent_tracks)}) | Quantidade de scrobbles inseridos: {db_playcount} | Progresso: {(db_playcount/api_total_scrobbles)*100:.2f}%")
        time.sleep(constantes.WAIT_TIME)

    return

def user_verified(user):
    query = """
    SELECT DISTINCT following_username FROM follows;
    """
    params = ()
    result = get_db_query(query, params)
    if len(result) > 0:
        return True
    return False


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("[get_recent_tracks] Especifique o nome de usuário na linha de comando.\n\t- Formato: python get_recent_tracks.py <nome_de_usuario>")
        exit()

    user = sys.argv[1]
    if not user_verified(user):
        confirmed = input(f"[get_recent_tracks] O usuário {user} não foi encontrado nos registros. Tem certeza que deseja incluir seus scrobbles no banco (y, s ou yes para confirmar)? ")
        if confirmed not in ('s', 'y', 'yes', 'sim'):
            print("[get_recent_tracks] Ok. Tente novamente em breve.")
            exit()
    
    if len(sys.argv) >= 3:
        tipo = sys.argv[2]
        if tipo == "d":
            start_date = input(f"[get_recent_tracks] Data de início (formato YYYY-MM-DD): ")
            end_date = input(f"[get_recent_tracks] Data de fim (formato YYYY-MM-DD): ")
        save_user_recent_tracks(user, start_date=date_to_unix(start_date), end_date=date_to_unix(end_date))
    else:
        save_user_recent_tracks(user)

