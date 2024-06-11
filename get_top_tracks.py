import requests
import constantes
import sys
import time
import requests
from file_manager import get_lines_from_file

def get_artist_top_tracks(artist_name, limit=1, initial=0):
    # Buscar o ID do artista
    search_url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist"
    headers = {
        'Authorization': f'Bearer {constantes.SPOTIFY_ACCESS_TOKEN}'
    }
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        artist_data = response.json()
        artist_id = artist_data['artists']['items'][0]['id'] if artist_data['artists']['items'] else None
        if artist_id:
            # Buscar as músicas mais ouvidas do artista
            top_tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
            params = {
                'limit': limit
            }
            response = requests.get(top_tracks_url, headers=headers, params=params)
            if response.status_code == 200:
                top_tracks_data = response.json()
                if top_tracks_data['tracks']:
                    top_tracks = []
                    for track in top_tracks_data['tracks'][initial:(limit)]:
                        top_tracks.append({
                            'id': track['id'],
                            'name': track['name'],
                            'album': track['album']['name'],
                            'popularity': track['popularity']
                        })
                    return top_tracks
                else:
                    print("[get_artist_top_tracks] Não foram encontradas músicas para este artista.")
            else:
                print(f"[get_artist_top_tracks] Falha ao buscar as músicas mais ouvidas do artista: {response.status_code}")
        else:
            print("[get_artist_top_tracks] Nenhum artista encontrado com esse nome.")
    else:
        print(f"[get_artist_top_tracks] Falha ao buscar o ID do artista: {response.status_code}")
    return None


if __name__ == "__main__":
    # Verificar se o nome do artista foi passado como argumento
    if len(sys.argv) >= 2:
        # Nome do artista
        artist_name = ' '.join(sys.argv[1:])

        # Buscar as músicas mais ouvidas do artista
        top_tracks = get_artist_top_tracks(artist_name)

        # Exibir as músicas mais ouvidas do artista
        if top_tracks:
            for index, track in enumerate(top_tracks, start=1):
                print(f"[main] {track['name']} - Album: {track['album']} - Popularidade: {track['popularity']} - ID: {track['id']}")
    else:
        # Ler a lista de artistas do arquivo
        artists_filename = "artists.txt"
        artists = read_artists_from_file(artists_filename)
        playlist = []
        for artist in artists:
            top_tracks = get_artist_top_tracks(artist)
            time.sleep(constantes.WAIT_TIME)
            if top_tracks:
                for track in top_tracks:
                    print(f"[main] {artist} - {track['name']} - Album: {track['album']} - Popularidade: {track['popularity']} - ID: {track['id']}")
                    playlist.append(track['id'])
        print(playlist)


