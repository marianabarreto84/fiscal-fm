from DAO import execute_db_statement, get_db_query
import sys
import time


def select_artists_today():
    query = """
    SELECT DISTINCT artist FROM scrobbles WHERE date(scrobble_date) = current_date;
    """
    params = ()
    result = get_db_query(query, params)
    artists = []
    for t in result:
        artists.append(t[0])
    return artists


def insert_artist_ranking():
    statement = """
    INSERT INTO artists_ranking(artist, ranking, scrobble_count, username, ranking_date)
    SELECT 
        artist,
        RANK() OVER (PARTITION BY artist ORDER BY COUNT(*) DESC) AS ranking,
        COUNT(*) AS scrobble_count,
        username,
        CURRENT_DATE
    FROM 
        scrobbles
    WHERE 
        DATE(scrobble_date) <= CURRENT_DATE
    GROUP BY 
        artist, username
    ON CONFLICT (artist, ranking_date, username) 
    DO UPDATE SET
        scrobble_count = EXCLUDED.scrobble_count,
        ranking = EXCLUDED.ranking;
    """
    params = ()
    execute_db_statement(statement, params)
    return


def delete_artist_ranking(artist_name):
    statement = """
    DELETE FROM artists_ranking ar WHERE ar.artist = %s
    AND ar.insertion_date IN (SELECT max(ar2.insertion_date) FROM artists_ranking ar2 WHERE ar.artist = ar2.artist)
    """
    params = (artist_name,)

    execute_db_statement(statement, params)
    return


if __name__ == "__main__":
    start = time.time()

    print(f"[main] Atualizando o ranking dos últimos scrobbles ainda não atualizados...")
    updated_artists = select_artists_today()
    print(f"[main] Foram encontrados {len(updated_artists)} artistas para serem atualizados.")
    insert_artist_ranking()
    print(f"[main] {len(updated_artists)} artistas foram atualizados.")
    
    end = time.time()

    print(f"[main] Tempo total decorrido em segundos: {end - start}.")
    print(f"[main] Tempo total decorrido em minutos: {(end - start)/60}.")