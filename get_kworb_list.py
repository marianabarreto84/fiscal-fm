from bs4 import BeautifulSoup

def get_track_ids(html_file):
    # Lê o conteúdo do arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
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
