from flask import Flask, request, redirect
import constantes
import requests
import base64
import json

app = Flask(__name__)

CLIENT_ID = constantes.SPOTIFY_CLIENT_ID
CLIENT_SECRET = constantes.SPOTIFY_CLIENT_SECRET
REDIRECT_URI = 'http://localhost:8888/callback'

@app.route('/')
def home():
    auth_url = (
        'https://accounts.spotify.com/authorize?'
        'response_type=code&client_id=' + CLIENT_ID +
        '&redirect_uri=' + REDIRECT_URI +
        '&scope=user-top-read'
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        token = get_token(code)
        return token
    return 'Authorization failed.'

def get_token(code):
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    headers = {
        'Authorization': f'Basic {b64_auth_str}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    return response.json()

if __name__ == '__main__':
    app.run(port=8888)
