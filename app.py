from flask import Flask, render_template, jsonify, request
import psycopg2
import pandas as pd
from constantes import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrobbles')
def scrobbles():
    return render_template('scrobbles.html')

@app.route('/data', methods=['GET'])
def data():
    conn = get_db_connection()
    query = "SELECT username, artist, track, scrobble_date FROM scrobbles_2024"
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Convertendo a coluna de data para o formato desejado
    #df['scrobble_date'] = df['scrobble_date'].dt.strftime('%d/%m/%Y %H:%M:%S')

    # Convertendo o DataFrame para JSON
    data = df.to_dict(orient='records')
    return jsonify(data)


@app.route('/artist/<nome_do_artista>')
def artist(nome_do_artista):
    return render_template('artist.html', artist=nome_do_artista)

@app.route('/artist_data', methods=['GET'])
def artist_data():
    artist = request.args.get('artist')
    conn = get_db_connection()
    print("Nome do artista encontrado:", artist)
    query = """
        SELECT username, COUNT(*) as scrobble_count 
        FROM scrobbles 
        WHERE artist = %s 
        GROUP BY username
    """
    df = pd.read_sql_query(query, conn, params=[artist])
    conn.close()

    # Convertendo o DataFrame para JSON
    data = df.to_dict(orient='records')
    return jsonify(data)


@app.route('/username/<nome_do_usuario>/artists')
def user_artists(nome_do_usuario):
    return render_template('user_artists.html', username=nome_do_usuario)

@app.route('/user_artists_data', methods=['GET'])
def user_artists_data():
    username = request.args.get('username')
    conn = get_db_connection()
    query = """
        WITH user_artist_counts AS (
            SELECT artist, COUNT(*) AS scrobble_count
            FROM scrobbles
            WHERE username = %s
            GROUP BY artist
        ),
        ranked_artists AS (
            SELECT artist, scrobble_count, 
                   RANK() OVER (ORDER BY scrobble_count DESC) AS ranking
            FROM user_artist_counts
        )
        SELECT ra.ranking, ra.artist, ra.scrobble_count, 
               COUNT(*) AS total_users
        FROM ranked_artists ra
        JOIN scrobbles s ON ra.artist = s.artist
        GROUP BY ra.ranking, ra.artist, ra.scrobble_count
        ORDER BY ra.ranking
    """
    df = pd.read_sql_query(query, conn, params=[username])
    conn.close()

    # Convertendo o DataFrame para JSON
    data = df.to_dict(orient='records')
    return jsonify(data)



if __name__ == '__main__':
    app.run(debug=True)
