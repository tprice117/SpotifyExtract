import requests
import spotipy
import os
from requests import post
from dotenv import load_dotenv
from flask import Flask, redirect, request, jsonify, session, url_for
import datetime
from spotipy.oauth2 import SpotifyOAuth
import time
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
auth_url_env = os.getenv("AUTH_URL")
token_url = os.getenv("TOKEN_URL")
api_base_url = os.getenv("API_BASE_URL")
TOKEN_INFO = 'token_info'



app = Flask(__name__)
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
app.secret_key = '234234234234'

@app.route('/')
def index():
    return "<a href='/login'> Login with Spotify</a><br> \
            <a href='/artist-lookup'> See Top songs of X Artist</a>"

@app.route('/login')
def login():
    auth_url = create_spotify_oath().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oath().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('save_discovery_weekly', external = True))



@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    response = requests.get(api_base_url + 'me/playlists', headers=headers)
    playlists = response.json()
    return jsonify(playlists)


@app.route('/saveDiscoveryWeekly')
def save_discovery_weekly():
    try:
        token_info = get_token()
    except:
        print("User not Logged in")
        return redirect('/')
    
    sp = spotipy.Spotify(auth=token_info['access_token'])

    user_id = sp.current_user()['id']
    
    cur_playlists = sp.current_user_playlists()['items']
    saved_weekly_playlist_id = None
    discover_weekly_playlist_id = None

    for playlist in cur_playlists:
        if(playlist['name'] == 'Discover Weekly'):
            discover_weekly_playlist_id = playlist['id']
        if(playlist['name'] == 'Saved Discovery Weekly'):
            saved_weekly_playlist_id = playlist['id']           
             
    if not discover_weekly_playlist_id:
        return('Discovery Playlist not found.')
    
    if not saved_weekly_playlist_id:
        new_playlist = sp.user_playlist_create(user_id, 'Saved Discovery Weekly', True)
        saved_weekly_playlist_id = new_playlist['id']
        
    discover_weekly_playlist = sp.playlist_items(discover_weekly_playlist_id)
    song_uris = []
    for song in discover_weekly_playlist['items']:
        
        song_uri = song['track']['uri']
        song_uris.append(song_uri)
        
    sp.user_playlist_add_tracks(user_id, saved_weekly_playlist_id, song_uris, None)
    return('Discovery weekly songs added to Saved Discovery Weekly')
    # return("OATH SUCCESSFUL")

@app.route('/artist-lookup')
def artist_lookup():
    return redirect('/')

def create_spotify_oath():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=url_for('redirect_page', _external=True),
        scope = 'user-library-read playlist-modify-public playlist-modify-private playlist-read-private'
    )


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', external = False))
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        spotify_oath = create_spotify_oath()
        token_info = spotify_oath.refresh_access_token(token_info['refresh_token'])
    return token_info


app.run(debug=True)
