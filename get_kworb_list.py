import requests
from bs4 import BeautifulSoup
from get_artist_tracks import get_artist_id

def get_track_ids(artist_name):
    # Define a URL da página do artista
    artist_id = get_artist_id(artist_name)
    url = f"https://kworb.net/spotify/artist/{artist_id}_songs.html"
    
    # Faz a requisição HTTP para obter o conteúdo da página
    response = requests.get(url)
    
    # Verifica se a requisição foi bem-sucedida
    if response.status_code != 200:
        raise Exception(f"Erro ao acessar a URL: {url}")
    
    # Lê o conteúdo da página HTML
    content = response.text
    
    # Cria um objeto BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    
    # Encontra todas as tags <a> com atributo href
    links = soup.find_all('a', href=True)
    
    # Lista para armazenar os IDs das faixas do Spotify
    track_ids = []
    
    # Itera sobre os links encontrados
    for link in links:
        href = link['href']
        if 'open.spotify.com/track/' in href:
            # Extrai o ID da faixa do URL
            track_id = href.split('open.spotify.com/track/')[-1]
            track_ids.append(track_id)
    
    return track_ids

if __name__ == "__main__":
    # Exemplo de uso
    html_file = 'files/kanye_all_songs.html'  # Substitua pelo caminho do seu arquivo HTML
    track_ids = extract_spotify_track_ids(html_file)
