
-- Visão: Inserção na Tabela de Rankings
CREATE OR REPLACE VIEW inserir_rankings AS
SELECT artist, username, count(*) as scrobble_count, rank() over (order by count(*) desc) as ranking
FROM scrobbles
WHERE artist = '<nome_do_artista>'
GROUP BY (artist, username);

-- Visão: Estatística de Rankings
CREATE OR REPLACE VIEW estatistica_rankings AS
SELECT username, artist, ranking, user_count, top1, top1_count, diferenca, mb_count, mb_ranking, mb_diferenca
FROM get_mb_ranking_stats('<nome_do_usuario>')
ORDER BY user_count DESC;

-- Visão: Controle de Atualizações
CREATE OR REPLACE VIEW controle_atualizacoes AS
SELECT * FROM control_panel;

-- Visão: Rankings Avançados
CREATE OR REPLACE VIEW rankings_avancados_2024 AS
SELECT lr.artist, fr.ranking AS velho, lr.ranking AS novo,
       lr.scrobble_count - fr.scrobble_count AS diferenca,
       CASE WHEN lr.ranking > fr.ranking THEN '-' ELSE '+' END AS status,
       abs(fr.ranking - lr.ranking) AS posicoes
FROM 
    (SELECT * FROM artists_ranking ar WHERE ranking_date = '2024-01-01') fr,
    (SELECT * FROM artists_ranking ar WHERE ranking_date = '2024-12-31') lr
WHERE fr.artist = lr.artist
  AND fr.username = lr.username
  AND fr.ranking <> lr.ranking
  AND fr.username='<nome_do_usuario>';
