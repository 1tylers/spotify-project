from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

# configure flask application
app = Flask(__name__)
app.secret_key = "bruh"
app.config['SESSION_COOKIE_NAME'] = 'Cookie'
TOKEN_INFO = 'token_info'

# route for the home page
@app.route('/')
def home():
    return render_template("home.html")

# route for login for to user authorization
@app.route('/login')
def login():
    sp_oauth = spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# redirect route
@app.route('/redirect')
def redirectPage():
    sp_oauth = spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('getTopTracks', _external=True))

# this route gets all the user track and artist information
@app.route('/getTopTracks')
def getTopTracks():
    try:
        token_info = get_token()
    except:
        print('user not logged in')
        redirect(url_for("login", _external=False))

    # get stats
    sp = spotipy.Spotify(auth=token_info['access_token'])
    top_tracks_4weeks = sp.current_user_top_tracks(limit=20, time_range='short_term')
    top_tracks_6months = sp.current_user_top_tracks(limit=20, time_range='medium_term')
    top_tracks_alltime = sp.current_user_top_tracks(limit=20, time_range='long_term')
    top_artists_4weeks = sp.current_user_top_artists(limit=20, time_range='short_term')
    top_artists_6months = sp.current_user_top_artists(limit=20, time_range='medium_term')
    top_artists_alltime = sp.current_user_top_artists(limit=20, time_range='long_term')


    track_list_4weeks = []
    track_list_6months = []
    track_list_alltime = []
    artist_list_4weeks = []
    artist_list_6months = []
    artist_list_alltime = []

    # put all the stats into there lists of dictionaries
    for idx, track in enumerate(top_tracks_4weeks['items']):
        artists = ', '.join([artist['name'] for artist in track['artists']])
        track_list_4weeks.append({"index": idx + 1, "track_name": track['name'], "artists": artists})
    
    for idx, track in enumerate(top_tracks_6months['items']):
        artists = ', '.join([artist['name'] for artist in track['artists']])
        track_list_6months.append({"index": idx + 1, "track_name": track['name'], "artists": artists})

    for idx, track in enumerate(top_tracks_alltime['items']):
        artists = ', '.join([artist['name'] for artist in track['artists']])
        track_list_alltime.append({"index": idx + 1, "track_name": track['name'], "artists": artists})

    for idx, artist in enumerate(top_artists_4weeks['items']):
        artist_list_4weeks.append({"index": idx + 1, "artist_name": artist['name']})

    for idx, artist in enumerate(top_artists_6months['items']):
        artist_list_6months.append({"index": idx + 1, "artist_name": artist['name']})

    for idx, artist in enumerate(top_artists_alltime['items']):
        artist_list_alltime.append({"index": idx + 1, "artist_name": artist['name']})

    # send the stats to the stats html template
    return render_template('stats.html',
                           tracks4weeks=track_list_4weeks,
                           tracks6months=track_list_6months,
                           tracksalltime=track_list_alltime,
                           artists4weeks=artist_list_4weeks,
                           artists6months=artist_list_6months,
                           artistsalltime=artist_list_alltime)


# gets the spotify access token (used to make authenticated requests to the spotify api)
def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise Exception("Token not available")
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60

    if (is_expired):
        sp_oauth = spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    
    return token_info


# spotify authentication
def spotify_oauth():
    # spotify authorization object
    return SpotifyOAuth(
        client_id="41aebc98c26541edb4ec6a98b8b04dfa",
        client_secret="45146b5b1751407ab8c4e9194ee59677",
        # external=true means it'll create the absolut path
        redirect_uri = url_for('redirectPage', _external=True),
        scope = "user-top-read"
    )

# runs app
if __name__ == '__main__':
    app.run(debug=True)
