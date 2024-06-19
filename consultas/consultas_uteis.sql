
-- INSERÇÃO NA TABELA DE RANKINGS
ALTER TABLE artists_ranking ADD CONSTRAINT unique_au UNIQUE (artist, username);

INSERT INTO artists_ranking
SELECT artist, username, count(*) as scrobble_count, rank() over (order by count(*) desc) as ranking
FROM scrobbles WHERE artist = 'Kanye West'
GROUP BY (artist, username);

ALTER TABLE artists_ranking DROP CONSTRAINT unique_au;


-- CONSULTA ESTATISTICA DE RANKINGS
SELECT username, artist, ranking, user_count, top1, top1_count, diferenca, mb_count, mb_ranking, mb_diferenca
FROM get_mb_ranking_stats('Leinadium')
ORDER BY user_count DESC;


-- TABELA DE PAINEL DE CONTROLE
DELETE FROM control_panel;
ALTER SEQUENCE control_panel_id_seq RESTART WITH 1;
INSERT INTO control_panel(start_date, end_date, chave, table_name, status) VALUES
('2024-06-07 17:21:02.593', '2024-06-08 12:44:39.613', 'update_scrobbles', 'scrobbles', 2);
SELECT * FROM control_panel;


-- RANKINGS
SELECT lr.artist, top1.username, top1.scrobble_count AS top1_count,
lr.scrobble_count AS user_count, lr.ranking AS user_ranking,
aa.avg_scrobbles
FROM last_ranking lr, top1_ranking top1, avg_artists aa 
WHERE lr.artist = top1.artist
AND lr.artist = aa.artist 
AND lr.username='mbarretov2' AND lr.ranking > 8
ORDER BY lr.ranking DESC, avg_scrobbles DESC;



-- FUNÇÃO PARA GERAR ESTATISTICAS GERAIS

CREATE OR REPLACE FUNCTION public.get_mb_ranking_stats(username_param text)
 RETURNS TABLE(artist text, username text, ranking integer,
 top1 text, top2 text, top1_count integer, top2_count integer,
 user_count integer, diferenca integer,
 mb_count integer, mb_diferenca integer, mb_ranking integer,
 avg_scrobbles numeric, avg_diferenca numeric, users integer
 )
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY 
    SELECT 
        top1.artist::text,
        username_param,
        usr.ranking as ranking,
        top1.username::text as top1,
        top2.username::text as top2,
        top1.scrobble_count AS top1_count,
        top2.scrobble_count as top2_count,
        usr.scrobble_count AS user_count,
        top1.scrobble_count - usr.scrobble_count AS diferenca,
        mb.scrobble_count as mb_count,
        usr.scrobble_count - mb.scrobble_count as mb_diferenca,
        mb.ranking as mb_ranking,
        avga.avg_scrobbles::numeric as avg_scrobbles,
        avga.avg_scrobbles::numeric - usr.scrobble_count as avg_diferenca,
        avga.users::int
    FROM 
        top1_ranking top1, top2_ranking top2,
        get_user_ranking(username_param) usr,
        get_user_ranking('mbarretov2') mb,
        avg_artists avga
    where top1.artist = usr.artist
    and top2.artist = usr.artist
    and mb.artist = usr.artist
    and avga.artist = usr.artist
    order by usr.scrobble_count desc;
END;
$function$;;

-- ARTISTA MAIS OUVIDO DE ACORDO COM A POPULARIDADE
SELECT
    artist,
    COUNT(DISTINCT username) AS unique_listeners,
    COUNT(*) AS total_plays,
    POWER(COUNT(DISTINCT username), 0.6) * POWER(COUNT(*), 0.4) AS popularity_score
FROM current_year
GROUP BY artist
ORDER BY POWER(COUNT(DISTINCT username), 0.6) * POWER(COUNT(*), 0.4) DESC;

SELECT aa.artist, aa.users, round(avg_scrobbles, 2), COALESCE(scrobble_count, 0) AS mb_count,
round(COALESCE(scrobble_count - avg_scrobbles, -avg_scrobbles), 2) AS diferenca
FROM avg_artists aa LEFT OUTER JOIN get_user_scrobbles('mbarretov2') mb
ON aa.artist = mb.artist
ORDER BY popularity_score desc;

-- VISÃO DE RANKING BONITA

CREATE MATERIALIZED VIEW stats_artists AS
(SELECT aa.artist, aa.avg_scrobbles, aa.users, aa.total_plays, aa.popularity_score AS score,
t1.min_count AS min_scrobbles, t1.max_count AS max_scrobbles, t1.std_dev
FROM avg_artists aa,
(SELECT artist_count.artist,
        min(artist_count.scrobble_count) AS min_count,
        max(artist_count.scrobble_count) AS max_count,
        stddev(artist_count.scrobble_count) AS std_dev
        FROM artist_count
        GROUP BY artist_count.artist) t1
WHERE aa.artist = t1.artist);

CREATE OR REPLACE VIEW stats_mb AS (
SELECT ar.artist, mb.ranking AS ranking,
ar.max_scrobbles, ar.min_scrobbles, ar.users, ar.total_plays,
round(ar.score, 2) AS score, round(ar.std_dev, 2) AS std_dev, round(ar.avg_scrobbles, 2) AS avg,
mb.scrobble_count AS mb_count, round(mb.scrobble_count - ar.avg_scrobbles, 2) AS diferenca
FROM stats_artists ar, get_user_ranking('mbarretov2') mb
WHERE ar.artist = mb.artist);

-- REGEX QUE TIRA O DELUXE
SELECT regexp_replace(album, ' \(Deluxe\)', ''), count(*)
FROM scrobbles WHERE artist='Kendrick Lamar'
GROUP BY regexp_replace(album, ' \(Deluxe\)', '') ORDER BY count(*) DESC;

SELECT username, count(*)
FROM scrobbles WHERE album='DAMN.'
GROUP BY username ORDER BY count(*) DESC;

SELECT username, scrobble_count
FROM get_artist_count('Beyoncé')
ORDER BY scrobble_count DESC;

-- EXEMPLOS DE PLAYLIST PARA O SHOW
SELECT 
    track, 
    artist, 
    count(*) AS total_scrobbles, 
    count(DISTINCT username) AS unique_users,
    (count(DISTINCT username) * 6 + count(*)) AS popularity_score
FROM 
    scrobbles
WHERE 
    artist IN ('Anitta', 'Alceu Valença', 'Elba Ramalho', 'Geraldo Azevedo', 'Zeca Pagodinho', 
               'Seu Jorge', 'Planet Hemp', 'Pabllo Vittar', 'Matuê', 'Joelma', 'Nando Reis',
               'Mart''nália', 'Ed Motta', 'Nação Zumbi', 'CPM22', 'Letrux', 'Petra Gil', 
               'MV Bill', 'Papatinho', 'Buchecha', 'Boogarins')
GROUP BY 
    track, artist
ORDER BY 
    popularity_score DESC;

-- MONITORAMENTO DO RANKING

-- esse pega o primeiro ranking total
SELECT DISTINCT velho.artist, velho.ranking AS velho, novo.ranking AS novo,
CASE WHEN velho.ranking > novo.ranking THEN '+' ELSE '-' END AS status,
velho.ranking - novo.ranking AS mudanca
FROM artists_ranking velho, artists_ranking novo
WHERE velho.username = 'mbarretov2'
AND velho.artist = novo.artist 
AND velho.username = novo.username 
AND velho.insertion_date IN (SELECT min(insertion_date) FROM artists_ranking WHERE artist = velho.artist)
AND novo.insertion_date IN (SELECT max(insertion_date) FROM artists_ranking WHERE artist = novo.artist)
AND velho.ranking <> novo.ranking
ORDER BY mudanca;

-- esse pega o ultimo ranking do artista e compara com o novo
SELECT DISTINCT velho.artist, velho.ranking AS velho, novo.ranking AS novo,
CASE WHEN velho.ranking > novo.ranking THEN '+' ELSE '-' END AS status,
velho.ranking - novo.ranking AS mudanca
FROM artists_ranking velho, artists_ranking novo
WHERE velho.username = 'mbarretov2'
AND velho.artist = novo.artist 
AND velho.username = novo.username 
AND velho.insertion_date IN (SELECT max(insertion_date) FROM artists_ranking WHERE artist = velho.artist AND insertion_date NOT IN (SELECT max(insertion_date) FROM artists_ranking WHERE artist = velho.artist))
AND novo.insertion_date IN (SELECT max(insertion_date) FROM artists_ranking WHERE artist = novo.artist)
AND velho.ranking <> novo.ranking
ORDER BY mudanca;

-- esse eh sem filtrar o username

CREATE OR REPLACE VIEW monitoramento_total AS (
SELECT velho.username, velho.artist, velho.ranking AS velho, novo.ranking AS novo,
CASE WHEN velho.ranking > novo.ranking THEN '+' ELSE '-' END AS status,
velho.ranking - novo.ranking AS mudanca
FROM artists_ranking velho JOIN artists_ranking novo
ON velho.artist = novo.artist and velho.username = novo.username
AND velho.insertion_date IN  (SELECT min(insertion_date) FROM artists_ranking WHERE artist = velho.artist)
AND novo.insertion_date IN (SELECT max(insertion_date) FROM artists_ranking WHERE artist = novo.artist)
AND velho.ranking <> novo.ranking
ORDER BY abs(velho.ranking - novo.ranking) desc, velho.ranking - novo.ranking);



CREATE OR REPLACE VIEW monitoramento_ultimo AS (
SELECT velho.username, velho.artist, velho.ranking AS velho, novo.ranking AS novo,
CASE WHEN velho.ranking > novo.ranking THEN '+' ELSE '-' END AS status,
velho.ranking - novo.ranking AS mudanca
FROM artists_ranking velho JOIN artists_ranking novo
ON velho.artist = novo.artist and velho.username = novo.username
AND velho.insertion_date IN  (SELECT max(insertion_date) FROM artists_ranking WHERE artist = velho.artist AND insertion_date NOT IN (SELECT max(insertion_date) FROM artists_ranking WHERE artist = velho.artist))
AND novo.insertion_date IN (SELECT max(insertion_date) FROM artists_ranking WHERE artist = novo.artist)
AND velho.ranking <> novo.ranking
ORDER BY abs(velho.ranking - novo.ranking) desc, velho.ranking - novo.ranking);


-- EXEMPLO DE COMPARAÇÕES ENTRE OS DIAS
SELECT mb.scrobble_date,
    mb.scrobble_count AS mb_count,
    ms.scrobble_count AS ms_count,
    lb.scrobble_count AS lb_count,
    pk.scrobble_count AS pk_count,
    rm.scrobble_count AS rm_count,
    rp.scrobble_count AS rp_count
FROM
    (SELECT * FROM get_scrobble_counts('2024-01-01', current_date, 'mbarretov2')) mb,
    (SELECT * FROM get_scrobble_counts('2024-01-01', current_date, 'marisalgueiro')) ms,
    (SELECT * FROM get_scrobble_counts('2024-01-01', current_date, 'luizabonazza')) lb,
    (SELECT * FROM get_scrobble_counts('2024-01-01', current_date, 'pedrokuchpil')) pk,
    (SELECT * FROM get_scrobble_counts('2024-01-01', current_date, 'rmottafc')) rm,
    (SELECT * FROM get_scrobble_counts('2024-01-01', current_date, 'rafinhaperry')) rp
WHERE mb.scrobble_date = lb.scrobble_date
AND mb.scrobble_date = pk.scrobble_date
AND mb.scrobble_date = rm.scrobble_date
AND mb.scrobble_date = rp.scrobble_date
AND mb.scrobble_date = ms.scrobble_date;

SELECT username, count(*)
FROM scrobbles WHERE date(scrobble_date) = '2024-06-10'
GROUP BY username
ORDER BY count(*) DESC;


-- GERADOR DA PLAYLIST DE NAO OUVIDOS

SELECT artist FROM stats_artists sa
WHERE artist
NOT IN (SELECT artist FROM scrobbles WHERE username='mbarretov2')
ORDER BY users DESC, score DESC
LIMIT 200;

SELECT artist
FROM scrobbles_vic -- visão apenas com os usuários que ela segue
WHERE artist NOT IN (SELECT artist FROM scrobbles WHERE username='vicisnotonfire')
GROUP BY artist ORDER BY SQRT(COUNT(*) * COUNT(DISTINCT username)) DESC
LIMIT 200;

-- PROCURA DUPLICATAS

SELECT s1.username, s1.scrobble_date, s1.insertion_date::text, s1.track FROM scrobbles s1, scrobbles s2
WHERE s1.username=s2.username
AND s1.artist=s2.artist
AND s1.album=s2.album 
AND s1.track=s2.track 
AND s1.scrobble_date=s2.scrobble_date
AND s1.insertion_date <> s2.insertion_date;


-- MUSICAS FAMOSAS MENOS OUVIDAS

SELECT track || '	-	' || artist
FROM scrobbles
WHERE (track, artist) NOT IN (SELECT track, artist FROM scrobbles
							WHERE username='mbarretov2')
--AND username IN (SELECT * FROM vic_seguindo)
GROUP BY track, artist ORDER BY count(DISTINCT username) DESC, count(*) DESC
LIMIT 100;

-- nova funcao de ranking (a outra tava muito lenta)
INSERT INTO artists_ranking(artist, ranking, scrobble_count, username, ranking_date)
SELECT 
    artist,
    RANK() OVER (PARTITION BY artist ORDER BY COUNT(*) DESC) AS ranking,
    COUNT(*) AS scrobble_count,
    username,
    current_date
FROM 
    scrobbles
WHERE scrobbles.artist IN (SELECT artist FROM scrobbles WHERE date(scrobble_date) = current_date)
GROUP BY 
    artist, username;

SELECT lr.artist, fr.ranking AS velho, lr.ranking AS novo, 
lr.scrobble_count - fr.scrobble_count AS diferenca,
CASE WHEN lr.ranking > fr.ranking THEN '-' ELSE '+' END AS status,
abs(fr.ranking - lr.ranking) AS posicoes
FROM 
(SELECT * FROM artists_ranking ar WHERE ranking_date = '2024-01-01') fr,
(SELECT * FROM artists_ranking ar WHERE ranking_date = '2024-06-19') lr
WHERE fr.artist = lr.artist
AND fr.username = lr.username
AND fr.ranking <> lr.ranking
AND fr.username='mbarretov2';