import requests
import sys
from get_spotify_token import get_access_token
import time


def get_artist_id(artist_name):
    search_url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=2"
    
    headers = {
        'Authorization': 'Bearer {}'.format(get_access_token())
    }

    search_response = requests.get(search_url, headers=headers)
    results = search_response.json()

    for artist in results['artists']['items']:
        if artist['name'].lower() == artist_name.lower():
            return artist['id']
    
    print("[get_artist_id] O artista {artist_name} não foi encontrado de primeira. Vamos analisar os resultados retornados.")
    
    # Crie uma lista de nomes de artistas
    artist_names = [artist["name"] for artist in results['artists']['items']]

    # Encontre o nome mais parecido usando difflib
    artist_match = difflib.get_close_matches(artist_name, artist_names, n=1)

    # Se um nome parecido foi encontrado, retorne o id correspondente
    if artist_match:
        artist_match = artist_match[0]
        for artist in results['artists']['items']:
            if artist["name"] == artist_match:
                id_found = artist["id"]
                name_found = artist["name"]
                print(f"[get_artist_id] O id do artista com nome mais parecido é: {name_found} - ID: {id_found}")
                return id_found
    return


def get_album_tracks(album_id):
    search_url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"

    headers = {
        'Authorization': 'Bearer {}'.format(get_access_token())
    }

    search_response = requests.get(search_url, headers=headers)
    results = search_response.json()
    tracks = []
    for track in results['items']:
        print(f"Nome: {track['name']} - ID: {track['id']}")
        tracks.append(track['id'])
    
    return tracks

def get_artist_albums(artist_id):
    search_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?market=BR"

    headers = {
        'Authorization': 'Bearer {}'.format(get_access_token())
    }

    search_response = requests.get(search_url, headers=headers)
    results = search_response.json()
    albums_info = []
    for album in results['items']:
        album = {'id': album['id'], 'name': album['name'], 'release_date': album['release_date']}
        print(f"[get_artist_albums] Nome do Álbum: {album['name']} - Data da Lançamento: {album['release_date']}")
        albums_info.append(album)
    albums_info = sorted(albums_info, key=lambda x: x['release_date'])
    albums = []
    for album in albums_info:
        albums.append(album['id'])
    return albums

def get_spotify_track(artist_name):
    artist_name = artist_name.replace("'", "")
    search_url = 'https://api.spotify.com/v1/search'

    # Faz a busca na API do Spotify
    headers = {
        'Authorization': 'Bearer {}'.format(get_access_token())
    }

    params = {
        'q': f"artist:{artist_name}",
        'type': 'track',
        'market': 'BR',
        'limit': 50
    }

    search_response = requests.get(search_url, headers=headers, params=params)
    total_tracks = 0

    while search_response.status_code == 200:
        results = search_response.json()

        for track in results['tracks']['items']:
            print(f"Nome: {track['name']} - ID: {track['id']}")
            artists = track['artists']
            for artist in artists:
                print(f"Artista Reconhecido: {artist['name']} - ID: {artist['id']}")
            total_tracks += 1
    
        search_url = results['tracks']['next']
        if search_url is None:
            break
        print(f"Nova URL: {search_url}")
        time.sleep(5)
        search_response = requests.get(search_url, headers=headers)
    
    print(f"Todas as musicas foram obtidas. Total de musicas: {total_tracks}")
    return

def get_artist_tracks(artist_name):
    artist_id = get_artist_id(artist_name)
    album_list = get_artist_albums(artist_id)
    playlist = []
    for album_id in album_list:
        print(f"ALBUM DE ID: {album_id} -------------")
        album_tracks = get_album_tracks(album_id)
        playlist.extend(album_tracks)
        time.sleep(2)
    return playlist


if __name__ == "__main__":
    artist_name = sys.argv[1]
    artist_id = get_artist_id(artist_name)
    album_list = get_artist_albums(artist_id)
    playlist = []
    for album_id in album_list:
        print(f"ALBUM DE ID: {album_id} -------------")
        album_tracks = get_album_tracks(album_id)
        playlist.extend(album_tracks)
        time.sleep(2)
    print(playlist)
    print(f"Quantidade de músicas encontradas: {len(playlist)}")