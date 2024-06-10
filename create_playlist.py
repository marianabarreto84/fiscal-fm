import requests
import time
import constantes
import playlists
import sys
from get_top_tracks import get_artist_top_tracks
from file_manager import get_lines_from_file

def create_playlist(playlist_name, track_ids):
    # Criar a playlist
    create_playlist_url = "https://api.spotify.com/v1/me/playlists"
    headers = {
        'Authorization': f'Bearer {constantes.SPOTIFY_ACCESS_TOKEN}',
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
    if len(sys.argv) < 2:
        print("[main] Por favor insira o nome da playlist que será criada nos argumentos da linha de comando.\n\t- python create_playlist.py \"<nome_da_playlist>\"")
        exit()

    playlist_name = ' '.join(sys.argv[1:])
    artists = get_lines_from_file("files/pck_artists.txt")

    playlist = []
    for artist in artists:
        top_tracks = get_artist_top_tracks(artist)

        if top_tracks:
            for track in top_tracks:
                print(f"[main] {artist} - {track['name']} - Album: {track['album']} - Popularidade: {track['popularity']} - ID: {track['id']}")
                playlist.append(track['id'])
        
        time.sleep(0.5)

    # print(playlist)
    time.sleep(2)
    create_playlist(playlist_name, playlist)