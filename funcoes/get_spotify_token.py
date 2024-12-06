import spotipy.util as util
import constantes

def get_access_token():
    token = util.prompt_for_user_token("maripbarreto", "user-read-private playlist-modify-public playlist-modify-private", client_id=constantes.SPOTIFY_CLIENT_ID, client_secret=constantes.SPOTIFY_CLIENT_SECRET, redirect_uri=constantes.SPOTIFY_REDIRECT_URI)
    return token

if __name__ == "__main__":
    token = get_access_token()
    print(f"[main] Token de acesso: {token}")