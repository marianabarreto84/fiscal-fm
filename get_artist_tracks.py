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
        print(f"Nome do artista encontrado: {artist['name']}")
        return artist['id']


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
    albums = []
    for album in results['items']:
        albums.append(album['id'])
    print()
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