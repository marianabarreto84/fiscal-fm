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


def select_updated_artists():
    query = """
    SELECT DISTINCT artist FROM scrobbles WHERE insertion_date > (SELECT max(insertion_date) FROM artists_ranking ar);
    """
    params = ()
    result = get_db_query(query, params)
    artists = []
    for t in result:
        artists.append(t[0])
    return artists


def insert_artist_ranking(artist_name):
    # Consulta SQL para inserir os dados na tabela artists_ranking
    statement = """
    INSERT INTO artists_ranking
    SELECT artist, username, count(*) AS scrobble_count, rank() OVER (ORDER BY count(*) DESC) AS ranking
    FROM scrobbles
    WHERE artist = %s
    GROUP BY artist, username;
    """
    
    # Parâmetros para a consulta SQL
    params = (artist_name,)
    
    # Executa a consulta SQL usando a função
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


def update_artist_ranking(artist_name):
    # delete_artist_ranking(artist_name)
    insert_artist_ranking(artist_name)
    return


if __name__ == "__main__":

    # FAZ PARA TODOS OS ARTISTAS SE NADA FOR ESPECIFICADO
    if len(sys.argv) < 2:
        # print("[main] Por favor, forneça o nome do artista como argumento.\n\t- python generate_artist_ranking.py <nome_do_artista>")
        start = time.time()

        print(f"[main] Atualizando o ranking dos últimos scrobbles ainda não atualizados...")
        updated_artists = select_updated_artists()
        print(f"[main] Foram encontrados {len(updated_artists)} artistas para serem atualizados.")
        for index, artist in enumerate(updated_artists):
            print(f"[main] Atualizando artista: {artist}. ({(index/len(updated_artists)*100):.2f}%)")
            update_artist_ranking(artist)
        print(f"[main] {len(updated_artists)} artistas foram atualizados.")
        

        # Nesse caso a lógica de primeiro atualizar e depois inserir os novos artistas importa porque ele leva em consideração a data da ultima insercao na tabela de rankings.
        print(f"[main] Inserindo rankings de novos artistas que não foram atualizados anteriormente...")
        artists = select_new_ranking_artists()
        print(f"[main] Foram encontrados {len(artists)} artistas para serem inseridos.")
        for index, artist in enumerate(artists):
            print(f"[main] Inserindo artista: {artist}. ({(index/len(artists)*100):.2f}%)")
            insert_artist_ranking(artist)
        print(f"[main] {len(artists)} artistas foram inseridos.")
        
        end = time.time()

        print(f"[main] Tempo total decorrido em segundos: {end - start}.")
        print(f"[main] Tempo total decorrido em minutos: {(end - start)/60}.")

    else:
        artist_name = sys.argv[1]
        update_last_artist_ranking(artist_name)
        print(f"[main] Ranking do {artist_name} atualizado.")
