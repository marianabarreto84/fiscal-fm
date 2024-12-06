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
   pip install -r requirements.txt
   ```

## Configuração
1. Clone este repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <NOME_DA_PASTA>
   ```
2. Configure suas credenciais no arquivo `constantes.py`:
   - `API_KEY` para Last FM.
   - `SPOTIFY_CLIENT_ID` e `SPOTIFY_CLIENT_SECRET` para Spotify.

## Uso
### Coletar Scrobbles
Para coletar os dados dos usuários configurados:
```bash
python main.py
```

### Criar Playlists
Para gerar playlists no Spotify:
```bash
python create_playlist.py "<nome_do_arquivo>" "<nome_da_playlist>" [<tipo>]
```
- `tipo` (opcional):
  - `a`: Arquivos de artistas.
  - `t`: Arquivos de músicas (padrão).
  - `ki`: IDs obtidas do kworb.
  - `tm`: Todas as músicas de um artista.

## Para Saber Mais
Consulte a [Wiki do Projeto](https://github.com/marianabarreto84/fiscal-fm/wiki/Wiki-do-Projeto) para obter informações detalhadas sobre arquitetura, comandos avançados, e outros detalhes técnicos.

## Limitações
- **Dependências:** O programa depende do funcionamento das APIs do Last FM e Spotify.
- **Interação:** Todo o controle é feito via linha de comando; a interface gráfica ainda não está implementada.
- **Dados Limitados:** Não inclui informações de gênero musical das faixas.

## Contribuição
Contribuições são bem-vindas! Abra uma issue ou envie um pull request.

## Licença
Este projeto está licenciado sob a MIT License. Consulte o arquivo `LICENSE` para mais informações.
