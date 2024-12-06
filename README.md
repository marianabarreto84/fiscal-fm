# Fiscal FM: Análise de Scrobbles e Gerador de Playlists

Este projeto utiliza as APIs do **Last FM** e do **Spotify** para coletar registros de músicas (scrobbles) e criar playlists personalizadas com base em estatísticas avançadas. Ele também permite análises de dados musicais dos usuários e seus amigos no Last FM.

## Funcionalidades
- **Coleta de Scrobbles:** Criação de um banco de dados com todos os registros de músicas de um usuário e seus amigos no Last FM.
- **Detecção de Inconsistências:** Identificação e solução de discrepâncias entre os dados coletados e os totais informados pelo Last FM.
- **Geração de Playlists:** Criação de playlists no Spotify baseadas em estatísticas, como:
  - Artistas mais ouvidos por um grupo de amigos.
  - Músicas populares que o usuário ainda não ouviu.
- **Consultas Avançadas:** Visões SQL para exploração detalhada dos dados.

## Pré-requisitos
1. **APIs:** Obtenha as chaves de API para:
   - Last FM: [Last FM API](https://www.last.fm/api)
   - Spotify: [Spotify Developer](https://developer.spotify.com/)
2. **Dependências Python:** Instale as bibliotecas necessárias:
   ```bash
   pip install requests pandas spotipy
