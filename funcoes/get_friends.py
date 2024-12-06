import requests
import constantes
import time
from DAO import execute_db_statement, get_db_query

def get_api_friends(username, page=1, limit=200):
    url = f"http://ws.audioscrobbler.com/2.0/?method=user.getfriends&user={username}&api_key={constantes.API_KEY}&limit={limit}&format=json&page={page}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"[get_friends] Erro {response.status_code} na requisição: {response.text}")
        exit()
    data = response.json()
    lista_friends = data['friends']['user']
    lista_users = [username]
    print(f"[get_friends] Quantidade de usuários que {username} segue: {len(lista_friends)}")
    for friend in lista_friends:
        lista_users.append(friend['name'])
    return lista_users

def get_db_friends(initial_user):
    query = """SELECT following_username FROM follows WHERE follower_username = %s;"""
    params = (initial_user,)
    result = get_db_query(query, params)
    list_of_users = list()
    for t in result:
        list_of_users.append(t[0])
    return list_of_users

def update_friends_table():
    for initial_user in constantes.LIST_OF_INITIAL_USERNAMES:
        api_friends = get_api_friends(initial_user)
        db_friends = get_db_friends(initial_user)
        for user in api_friends:
            if user not in db_friends:
                statement = """INSERT INTO follows(follower_username, following_username) VALUES (%s, %s);"""
                params = (initial_user, user, )
                execute_db_statement(statement, params)
                print(f"[update_friends_table] Novo relacionamento adicionado: {initial_user} e {user}")
        time.sleep(constantes.WAIT_TIME)
    print("[update_friends_table] Tabela de relacionamento entre seguidores atualizada.")
    return

if __name__ == "__main__":
    update_friends_table()
