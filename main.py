from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

year = "2000-08-12"
URL = f"https://www.billboard.com/charts/hot-100/{year}/"
SPOTIFY_CLIENT_ID = "my_spotify_id"
SPOTIFY_CLIENT_SECRET = "my_secret_id"
SPOTIPY_REDIRECT_URI = "http://example.com/"
OAUTH_TOKEN_URL= 'https://accounts.spotify.com/api/token'

response = requests.get(URL)
top_100 = response.text


soup = BeautifulSoup(top_100, "html.parser")
top_100_songs = []
top_100_artist = []
for names in soup.find_all("h3", class_="a-no-trucate"):
    song_name = names.get_text().split("\n\n\t\n\t\n\t\t\n\t\t\t\t\t")[1].split("\t\t\n\t\n")[0]
    top_100_songs.append(song_name)

for artists in soup.find_all("span", class_="a-no-trucate"):
    artist_name = artists.get_text().split("\n\t\n\t")[1].split("\n")[0]
    top_100_artist.append(artist_name)

scope = "playlist-modify-private"
sp_auth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, scope=scope, state="state", redirect_uri=SPOTIPY_REDIRECT_URI)
sp = spotipy.Spotify(auth_manager=sp_auth)
user_id = sp.current_user()['id']
access_data = {
    'grant_type': 'client_credentials',
    'client_id': SPOTIFY_CLIENT_ID,
    'client_secret': SPOTIFY_CLIENT_SECRET,
}
access_response = requests.post(url=OAUTH_TOKEN_URL, data=access_data)
ACCESS_TOKEN = access_response.json().get('access_token')

song_uri = []
for i in range(0, 100):
    params = {
        "q": f"track:{top_100_songs[i]}, artist:{top_100_artist[i]}",
        "type": "track",
        "market": "ES",
        "limit": 1,
        "offset": 1
    }
    header = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    songs = requests.get(url="https://api.spotify.com/v1/search", params=params, headers=header)
    content = songs.json()
    try:
        song_uris = content['tracks']['items'][0]['uri']
        song_uri.append(song_uris)
    except IndexError:
        continue



name = f"{year} Billboard 100"
public = False
collaborative = False

playlist = sp.user_playlist_create(name=name, user=user_id, public=public, collaborative=collaborative)
playlist_id = playlist['id']
sp.playlist_add_items(playlist_id=playlist_id, items=song_uri)