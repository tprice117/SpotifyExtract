import requests
import subprocess
import spotipy
import base64
import os
from requests import post, get
import json
import dotenv
from dotenv import load_dotenv
from flask import Flask, redirect, request, jsonify, session
import urllib.parse
import datetime

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
auth_url = os.getenv("AUTH_URL")
token_url = os.getenv("TOKEN_URL")
api_base_url = os.getenv("API_BASE_URL")

user_id = 'thewaffle360'
SPOTIFY_PLAYLIST_URL = f'https://api.spotify.com/v1/users/{user_id}/playlists'
print(SPOTIFY_PLAYLIST_URL)
# print("Enter your spotify userid: ")
# userID = input()



# curl_cmd = 'curl https://api.spotify.com/v1/users/smedjan/playlists'

# try:
#     proc = subprocess.run(curl_cmd, shell=True, check=True,
#                           capture_output=True, text=True)
#     if proc.returncode == 0:
#         print("Curl incomplete")
#         print(proc.stdout)
#     else:
#         print("Curl failed return code: ", proc.returncode)
# except subprocess.CalledProcessError as e:
#     print("Error executing curl command: ", e)


def get_token():
    auth = client_id + ":" + client_secret
    auth_enc = auth.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_enc), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token



def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers= headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists ")
        return None
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

token = get_token()
result = search_for_artist(token, "ACDC")
artist_id = result["id"]
songs = get_songs_by_artist(token, artist_id)
print(songs)

for idx, song in enumerate(songs):
    print(f"{idx + 1}. {song['name']}. {song['popularity']}")