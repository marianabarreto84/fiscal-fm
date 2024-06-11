import requests
import constantes

def get_friends(username, page=1, limit=200):
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

# TODO: fazer uma funcao para pegar o numero de amigos e salvar no banco se a pessoa seguiu um usuario novo ou deixou de seguir pra atualizar a tabela de seguindo