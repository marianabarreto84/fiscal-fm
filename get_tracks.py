import requests
import constantes
import sys
import time
from file_manager import get_lines_from_file

def get_spotify_track(track_name, artist_name):
    search_url = 'https://api.spotify.com/v1/search'

    # Faz a busca na API do Spotify
    headers = {
        'Authorization': 'Bearer {}'.format(constantes.SPOTIFY_ACCESS_TOKEN)
    }

    params = {
        'q': f"{track_name} artist:{artist_name}",
        'type': 'track',
        'market': 'BR',
    }

    search_response = requests.get(search_url, headers=headers, params=params)

    # Verifica se houve algum resultado
    if search_response.status_code == 200:
        results = search_response.json()
        if results['tracks']['items']:
            track_info = {
                'id': results['tracks']['items'][0]['id'],
                'artist': results['tracks']['items'][0]['artists'][0]['name'],
                'name': results['tracks']['items'][0]['name'],
                'album': results['tracks']['items'][0]['album']['name']
            }
            return track_info
        else:
            return None
    else:
        print("[get_spotify_track] Erro ao fazer a busca:", search_response.status_code)
        return None

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        track_name = " ".join(sys.argv[1])
        artist_name = " ".join(sys.argv[2])
        track = get_spotify_track(track_name, artist_name)

        if track:
            print(f"[main] {track['name']} - Artista: {track['artist']} - Album: {track['album']} - ID: {track['id']}")
        else:
            print("[main] Nenhuma música encontrada com esse nome de artista e nome de música.")

    elif len(sys.argv) == 2:
        file = get_lines_from_file(f"files/{sys.argv[1]}.txt")
        track_list = []
        for line in file:
            info = line.split("\t-\t")
            track_list.append([info[0], info[1]])
        track_ids = []
        for track in track_list:
            track = get_spotify_track(track[0], track[1])
            print(f"[main] {track['name']} - Artista: {track['artist']} - Album: {track['album']} - ID: {track['id']}")
            track_ids.append(track['id'])
        time.sleep(0.5)
        print(track_ids)

    else:
        print("[main] Especifique o nome da música assim como o artista. Exemplo:\n\t- python get_tracks.py \"<nome_da_musica>\" \"<nome_do_artista>\"")

