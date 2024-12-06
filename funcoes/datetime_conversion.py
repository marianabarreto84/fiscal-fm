import pytz
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
    if len(date_string) == 0:
        return None
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

