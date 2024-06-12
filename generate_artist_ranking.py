from DAO import execute_db_statement, get_db_query
import sys
import time

def select_new_ranking_artists():
    query = """
    SELECT artist, count(*)
    FROM scrobbles WHERE artist NOT IN (SELECT artist FROM artists_ranking ar)
    GROUP BY artist ORDER BY count(*) desc;
    """
    params = ()
    result = get_db_query(query, params)
    artists = []
    for t in result:
        artists.append(t[0])
    return artists


def select_artists(date=None):
    if date:
        query = "SELECT DISTINCT artist FROM scrobbles WHERE date(scrobble_date) <= %s;"
        params = (date,)
    else:
        query = """
        SELECT DISTINCT artist FROM scrobbles
        WHERE scrobble_date > (SELECT max(scrobble_date) FROM scrobbles WHERE scrobble_date >= (SELECT max(insertion_date) FROM artists_ranking));
        """
        params = ()
    
    result = get_db_query(query, params)
    return [t[0] for t in result]

def insert_artist_ranking(artist_name, date=None):
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    statement = """
    INSERT INTO artists_ranking
    SELECT artist, username, count(*) AS scrobble_count, rank() OVER (ORDER BY count(*) DESC) AS ranking
    FROM scrobbles
    WHERE artist = %s AND date(scrobble_date) <= %s
    GROUP BY artist, username;
    """
    params = (artist_name, date)
    execute_db_statement(statement, params)


def delete_artist_ranking(artist_name):
    statement = """
    DELETE FROM artists_ranking ar WHERE ar.artist = %s
    AND ar.insertion_date IN (SELECT max(ar2.insertion_date) FROM artists_ranking ar2 WHERE ar.artist = ar2.artist)
    """
    params = (artist_name,)

    execute_db_statement(statement, params)
    return


def update_artist_ranking(artist_name, date=None):
    # delete_artist_ranking(artist_name)
    insert_artist_ranking(artist_name, date=date)
    return


if __name__ == "__main__":

    # FAZ PARA TODOS OS ARTISTAS SE NADA FOR ESPECIFICADO
    if len(sys.argv) <= 1:
        start = time.time()

        print(f"[main] Atualizando o ranking dos últimos scrobbles ainda não atualizados...")
        updated_artists = select_updated_artists()
        print(f"[main] Foram encontrados {len(updated_artists)} artistas para serem atualizados.")
        for index, artist in enumerate(updated_artists):
            print(f"[main] Atualizando artista: {artist}. ({(index/len(updated_artists)*100):.2f}%)")
            update_artist_ranking(artist)
        print(f"[main] {len(updated_artists)} artistas foram atualizados.")
        
        end = time.time()

        print(f"[main] Tempo total decorrido em segundos: {end - start}.")
        print(f"[main] Tempo total decorrido em minutos: {(end - start)/60}.")
    else:
        tipo = sys.argv[1]
        if tipo == "a":
            artist_name = input("Nome do artista: ")
            update_last_artist_ranking(artist_name)
            print(f"[main] Ranking do {artist_name} atualizado.")
        else:
            last_scrobble_date = input("Data do scrobble (formato YYYY-MM-DD): ")
            artists = select_artists(date=last_scrobble_date)
            for index, artist in enumerate(artists):
                print(f"[main] Atualizando artista: {artist}. ({(index/len(artists)*100):.2f}%)")
                update_artist_ranking(artist, date=last_scrobble_date)