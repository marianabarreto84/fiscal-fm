from DAO import get_db_query
from create_playlist import create_playlist


def get_top_k_2024(limit=100):
    query = """
    SELECT track, artist
    FROM scrobbles24
    GROUP BY track, artist
    ORDER BY COUNT(DISTINCT username) DESC, COUNT(*) DESC
    LIMIT %s;
    """
    params = (limit,)
    result = get_db_query(query, params)
    tracklist = []
    for t in result:
        name = t[0]
        artist = t[1]
        tracklist.append([name, artist])
    return tracklist


def get_playlist(tracklist):
    tracklist = []
    for track in tracklist:
        track_name = track[0]
        artist_name = track[1]
        track_found = get_spotify_track(track_name, artist_name)
        if track_found:
            print(f"[main] {track_found['name']} - Artista: {track_found['artist']} - Album: {track_found['album']} - ID: {track_found['id']} | Original: {track_name} - {artist_name}")
        else:
            print(f"[main] Não foi possivel encontrar a musica {track_name} de {artist_name}.")
        tracklist.append(track_found['id'])
        time.sleep(0.5)
    return tracklist

def update_playlist(playlist_id, playlist):
    


if __name__ == "__main__":
    tracklist = get_top_k_2024()
    playlist = get_playlist(tracklist)
    update_playlist('4KA1S42t7bszB0MA4f1gc9', playlist)
