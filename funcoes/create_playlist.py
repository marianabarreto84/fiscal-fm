import requests
import time
import constantes
import playlists
import sys
from get_top_tracks import get_artist_top_tracks
from get_tracks import get_spotify_track
from file_manager import get_lines_from_file
from get_spotify_token import get_access_token
from get_kworb_list import get_track_ids
from get_artist_tracks import get_artist_tracks

def create_playlist(playlist_name, track_ids):
    # Criar a playlist
    create_playlist_url = "https://api.spotify.com/v1/me/playlists"
    headers = {
        'Authorization': f'Bearer {get_access_token()}',
        'Content-Type': 'application/json'
    }
    data = {
        'name': playlist_name,
        'public': True  # Altere para True se quiser que a playlist seja pública
    }
    response = requests.post(create_playlist_url, headers=headers, json=data)

    if response.status_code == 201:
        playlist_data = response.json()
        playlist_id = playlist_data['id']

        # Adicionar as músicas à playlist em lotes de no máximo 100 faixas
        for i in range(0, len(track_ids), 100):
            batch_track_ids = track_ids[i:i+100]
            add_tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
            data = {
                'uris': [f'spotify:track:{track_id}' for track_id in batch_track_ids]
            }
            response = requests.post(add_tracks_url, headers=headers, json=data)

            if response.status_code != 201 and response.status_code != 200:
                print(f"[create_playlist] Falha ao adicionar as músicas à playlist: {response.status_code}")
                return False

        print(f"[create_playlist] A playlist '{playlist_name}' foi criada com sucesso e as músicas foram adicionadas.")
        return True
    else:
        print(f"[create_playlist] Falha ao criar a playlist: {response.status_code}")
        return False


if __name__ == "__main__":

    tipo = "t"
    playlist = []

    if len(sys.argv) < 3:
        print("[main] Por favor insira o nome da playlist e o nome do arquivo original que será criada nos argumentos da linha de comando.")
        print("\t- python create_playlist.py \"<nome_do_arquivo>\"|\"<nome_do_artista>\" \"<nome_da_playlist>\" [<tipo>]")
        print("\t- <tipo>: \"a\" para arquivos de artistas, \"t\" para arquivos de musicas, \"ki\" para ids obtidas do kworb e \"tm\" para pegar todas as músicas de um determinado artista. O padrão é \"t\".")
        exit()
    elif len(sys.argv) > 3:
        tipo = sys.argv[3]

    playlist_name = sys.argv[2]

    if tipo == "a":
        file_name = sys.argv[1]
        artists = get_lines_from_file(f"files/{file_name}")
        for artist in artists:
            top_tracks = get_artist_top_tracks(artist)
            if top_tracks:
                for track in top_tracks:
                    print(f"[main] {artist} - {track['name']} - Album: {track['album']} - Popularidade: {track['popularity']} - ID: {track['id']}")
                    playlist.append(track['id'])
            
            time.sleep(0.5)
    elif tipo == "ki":
        artist_name = sys.argv[1]
        playlist = get_track_ids(artist_name)
    elif tipo == "tm" or tipo == "tt":
        artist_name = sys.argv[1]
        playlist = get_artist_tracks(artist_name)
    else: # tipo = t
        file_name = sys.argv[1]
        tracks_lines = get_lines_from_file(f"files/{file_name}")
        for track in tracks_lines:
            track = track.split("\t-\t")
            track_name = track[0]
            artist_name = track[1]
            track_found = get_spotify_track(track_name, artist_name)
            if track_found:
                print(f"[main] {track_found['name']} - Artista: {track_found['artist']} - Album: {track_found['album']} - ID: {track_found['id']} | Original: {track_name} - {artist_name}")
                playlist.append(track_found['id'])
            else:
                print(f"[main] Não foi possivel encontrar a musica {track_name} de {artist_name}.")
            time.sleep(0.5)

    
    time.sleep(2)
    create_playlist(playlist_name, playlist)