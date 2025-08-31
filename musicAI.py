# FLASK WEB DEVELOPMENT
import flask
from flask import request, jsonify , render_template ,jsonify


# requesting data and converting api info to base64
import requests
import json
import base64

# string to python class type
import ast

# check files in running machine
from os.path import exists


# debugging
import time
import pprint

# webcrawl lyrics
import bs4

# WATSON AI
import watson


# MATH
import statistics
import random

# Environment variables
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Validate required environment variables
required_env_vars = [
    'SPOTIFY_CLIENT_ID',
    'SPOTIFY_CLIENT_SECRET', 
    'SPOTIFY_CALLBACK_URL',
    'GENIUS_API_KEY',  # Changed from OAuth to direct API key
    'WATSON_API_KEY',
    'WATSON_SERVICE_URL'
]

# Optional but recommended for full functionality
optional_env_vars = [
    'IMGFLIP_USERNAME',
    'IMGFLIP_PASSWORD'
]

missing_vars = []
for var in required_env_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print("WARNING: Missing required environment variables:")
    for var in missing_vars:
        print(f"  - {var}")
    print("\nPlease check your .env file or environment variables.")
    print("The app may not function properly without these variables.\n")

# Check optional variables
missing_optional = []
for var in optional_env_vars:
    if not os.getenv(var):
        missing_optional.append(var)

if missing_optional:
    print("INFO: Missing optional environment variables:")
    for var in missing_optional:
        print(f"  - {var}")
    print("These are not required but enable additional features like meme generation.\n")

# TODO make a json database of all the songs watson has already analyzed
# make a function to apply the database before running the analysis, check if we already have it



# # DISABLE EXTRA INFORMATION FROM LOGS
# import logging
# log = logging.getLogger('werkzeug')
# log.disabled = True




# FLASK INIT VARIABLES
application = flask.Flask(__name__ , static_url_path='', static_folder='static' , template_folder='templates')
application.config["DEBUG"] = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
application.secret_key = os.getenv('FLASK_SECRET_KEY', 'something secret')

# SPOTFIY INIT VARIABLES
spotify_clientId = os.getenv('SPOTIFY_CLIENT_ID', '')
spotify_clientSecret = os.getenv('SPOTIFY_CLIENT_SECRET', '')

# GENIUS INIT VARIABLES - Using direct API key instead of OAuth
genius_api_key = os.getenv('GENIUS_API_KEY', '')

# general use INIT VARIABLES
spotify_callbackURL = os.getenv('SPOTIFY_CALLBACK_URL', '')

# Token storage file
TOKEN_FILE = 'user_tokens.json'

# Imgflip API credentials
imgflip_username = os.getenv('IMGFLIP_USERNAME', '')
imgflip_password = os.getenv('IMGFLIP_PASSWORD', '')

API_COOLDOWN_RATE = 3


# auth SPOTFITY scopes
scopes = [
 'ugc-image-upload',
 'user-read-recently-played',
 'user-top-read',
 'user-read-playback-position',
 'user-read-playback-state',
 'user-modify-playback-state',
 'user-read-currently-playing',
 'app-remote-control',
 'streaming',
 'playlist-modify-public',
 'playlist-modify-private',
 'playlist-read-private',
 'playlist-read-collaborative',
 'user-follow-modify',
 'user-follow-read',
 'user-library-modify',
 'user-library-read',
 'user-read-email',
 'user-read-private'
]
spotty_full_permission = ''
for i in scopes:
    spotty_full_permission += i + ' '


# Token storage functions
def save_user_token(user_id, token_data):
    """Save user tokens to local storage"""
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                tokens = json.load(f)
        else:
            tokens = {}
        
        tokens[user_id] = {
            'spotify_token': token_data.get('spotify_token'),
            'spotify_refresh_token': token_data.get('spotify_refresh_token'),
            'spotify_expires_at': token_data.get('spotify_expires_at'),
            'genius_token': token_data.get('genius_token'),
            'last_updated': time.time()
        }
        
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
            
    except Exception as e:
        print(f"ERROR: Failed to save tokens: {e}")

def load_user_token(user_id):
    """Load user tokens from local storage"""
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                tokens = json.load(f)
                return tokens.get(user_id, {})
        return {}
    except Exception as e:
        print(f"ERROR: Failed to load tokens: {e}")
        return {}

def is_token_expired(expires_at):
    """Check if token is expired (with 5 minute buffer)"""
    if not expires_at:
        return True
    return time.time() > (expires_at - 300)  # 5 minute buffer

def validate_token_scopes(token):
    """Validate token and check available scopes"""
    try:
        headers = {"Authorization": "Bearer " + token}
        response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"DEBUG: Token validation successful for user: {user_data.get('display_name', 'Unknown')}")
            return True
        elif response.status_code == 401:
            print(f"DEBUG: Token is expired or invalid (401)")
            return False
        elif response.status_code == 403:
            print(f"DEBUG: Token has insufficient scopes (403)")
            return False
        else:
            print(f"DEBUG: Token validation failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"DEBUG: Error validating token: {e}")
        return False


# database check
path_to_file = "song_db.json"
if exists(path_to_file):
    pass
else:
    with open("song_db.json" , "w") as f:
        f.write("{}")





# homepage
@application.route('/', methods=['GET'])
def home():
    if "amount" not in flask.session:
       flask.session['amount'] = 0

    content = {
        'implciit_url' : authorize_spotify_IMPLICIT(),
        'refreshable_url' : authorize_spotify_REFRESHABLE()
    }
    return render_template('homepage.html' , content = content)


# spotify login
@application.route('/login/')
def logging_in():
    # Check if we have an authorization code
    if 'code' in flask.request.args:
        auth_code = flask.request.args['code']
        token_data = _retrieve_refreshable_token(auth_code)
        
        if not token_data:
            print("ERROR: Failed to retrieve Spotify tokens")
            return flask.redirect('/')
        
        # Get user info to create user ID
        user_info = fetch_spotify_data(token_data['access_token'], 'https://api.spotify.com/v1/me')
        if user_info == "ERROR":
            print("ERROR: Failed to get user info")
            return flask.redirect('/')
        
        user_id = user_info.get('id', user_info.get('email', 'unknown'))
        
        # Save tokens to local storage
        save_user_token(user_id, {
            'spotify_token': token_data['access_token'],
            'spotify_refresh_token': token_data.get('refresh_token'),
            'spotify_expires_at': time.time() + token_data.get('expires_in', 3600),
            'genius_token': genius_api_key  # Use our API key directly
        })
        
        # Store user info in session
        flask.session['user_id'] = user_id
        flask.session['spotify_token'] = token_data['access_token']
        flask.session['spotify_expired'] = False
        flask.session['username'] = user_info.get('display_name', 'User')
        
        print(f"SUCCESS: User {user_id} authenticated and tokens saved")
        return flask.redirect('/Dashboard')
    
    return flask.redirect("/")

# Genius API key is now handled automatically - no user login needed



# User Dashboard
@application.route('/Dashboard', methods=['GET'])
def Dashboard():
    # Check if user is authenticated
    if 'user_id' not in flask.session:
        print(f"\n\n\n------------\nAccess denied (no user session): {request.remote_addr}\n------------")
        return flask.redirect('/')
    
    user_id = flask.session['user_id']
    
    # Load stored tokens
    token_data = load_user_token(user_id)
    if not token_data:
        print(f"\n\n\n------------\nAccess denied (no stored tokens): {request.remote_addr}\n------------")
        return flask.redirect('/')
    
    # Check if Spotify token is expired and refresh if needed
    spotify_token = token_data.get('spotify_token')
    if not spotify_token or is_token_expired(token_data.get('spotify_expires_at')):
        print(f"INFO: Spotify token expired for user {user_id}, attempting refresh...")
        
        if token_data.get('spotify_refresh_token'):
            new_tokens = _refresh_spotify_token(token_data['spotify_refresh_token'])
            if new_tokens:
                # Update stored tokens
                token_data.update(new_tokens)
                save_user_token(user_id, token_data)
                spotify_token = new_tokens['access_token']
                flask.session['spotify_token'] = spotify_token
                print(f"SUCCESS: Refreshed Spotify token for user {user_id}")
            else:
                print(f"ERROR: Failed to refresh Spotify token for user {user_id}")
                return flask.redirect('/')
        else:
            print(f"ERROR: No refresh token available for user {user_id}")
            return flask.redirect('/')
    
    # Store current token in session for compatibility
    flask.session['spotify_token'] = spotify_token
    flask.session['genius_token'] = token_data.get('genius_token', genius_api_key)

    # fetch user data from spotify after auth functions
    user_data = fetch_spotify_data(spotify_token , 'https://api.spotify.com/v1/me' )



    # retrive amount analyzed
    if "amount" in flask.session:
        amount_analyzed = flask.session['amount']
    else:
        flask.session['amount'] = 0

    
    # USING TRY METHOD TO FIND KEYS IN user_data RESPONSE
    try:
        print(f"DEBUG: user_data keys: {list(user_data.keys()) if isinstance(user_data, dict) else 'Not a dict'}")
        print(f"DEBUG: user_data type: {type(user_data)}")
        
        if not isinstance(user_data, dict) or 'error' in user_data:
            print(f"ERROR: Invalid user_data: {user_data}")
            flask.session['spotify_expired'] = True
            return flask.redirect(authorize_spotify_REFRESHABLE())
        
        if 'display_name' not in user_data:
            print(f"ERROR: Missing display_name in user_data: {user_data}")
            flask.session['spotify_expired'] = True
            return flask.redirect(authorize_spotify_REFRESHABLE())
        
        # save username throughout session
        flask.session['username'] = user_data['display_name']
        flask.session['email'] = user_data.get('email', 'No email')
        
        # Generate meme with error handling
        try:
            meme_result = fetch_meme(flask.session["username"])
            meme_url = meme_result['data']['url']
        except Exception as meme_error:
            print(f"ERROR: Meme generation failed: {meme_error}")
            meme_url = '/static/fallback.svg'

        # Get recently played tracks
        try:
            recent_tracks = user_recently_played(spotify_token, limit=10)
        except Exception as e:
            print(f"ERROR: Failed to fetch recently played tracks: {e}")
            recent_tracks = []
        
        # final display
        context = {
            'data': user_data,
            'username': flask.session['username'],
            'email': flask.session['email'], 
            'meme': meme_url,
            "amount_analyzed": amount_analyzed,
            "recent_tracks": recent_tracks,
        }
        return render_template('user_dashboard.html', context=context)

    except Exception as e:
        print(f"ERROR: Dashboard() - {e}")
        print(f"ERROR: user_data content: {user_data}")
        flask.session['spotify_expired'] = True
        return flask.redirect(authorize_spotify_REFRESHABLE())



# SEARCH A SONG
@application.route('/search-form', methods=['GET'])
def search_form():
    return flask.render_template('search_form.html' )
@application.route('/search-results', methods=['POST'])
def search_results():
    try:
        spotify_token = flask.session.get('spotify_token')
        if not spotify_token:
            return flask.redirect('/')
        
        q = flask.request.form.get('q')
        if not q:
            return "Search query is required", 400
            
        q_type = flask.request.form.get('q_type')

        artists = []
        tracks = []
        
        # SEARCHING FOR TRACKS
        if q_type == None or q_type == 'None':
            q_type = 'track'
            # search spotify
            data = fetch_spotify_data(spotify_token, f'https://api.spotify.com/v1/search?q={q}&type={q_type}')
            
            if data == "ERROR":
                return "Failed to search Spotify. Please try again.", 500
                
            q_type += 's'
            tracks = data.get(q_type, {}).get('items', [])
            
            # add images safely
            for i in tracks:
                try:
                    if i.get('artists') and len(i['artists']) > 0:
                        artist_href = i['artists'][0].get('href')
                        if artist_href:
                            artist_data = fetch_spotify_data(spotify_token, artist_href)
                            if artist_data != "ERROR" and artist_data.get('images'):
                                i['thumbnail'] = artist_data['images'][-1]['url']
                            else:
                                i['thumbnail'] = '/static/fallback.svg'
                        else:
                            i['thumbnail'] = '/static/fallback.svg'
                    else:
                        i['thumbnail'] = '/static/fallback.svg'
                except Exception as e:
                    print(f"ERROR adding thumbnail for track {i.get('name', 'Unknown')}: {e}")
                    i['thumbnail'] = '/static/fallback.svg'

        # SEARCHING FOR ARTISTS
        else:
            q_type = 'artist'
            # search spotify
            data = fetch_spotify_data(spotify_token, f'https://api.spotify.com/v1/search?q={q}&type={q_type}')
            
            if data == "ERROR":
                return "Failed to search Spotify. Please try again.", 500
                
            q_type += 's'
            artists = data.get(q_type, {}).get('items', [])

        content = {
            'artists' : artists ,
            'tracks' : tracks,
            'query': q
        }
        return flask.render_template('search_results.html' , content = content )
        
    except Exception as e:
        print(f"ERROR in search_results: {e}")
        return "An error occurred while searching. Please try again.", 500
@application.route('/song-analysis', methods=['POST'  ])
def song_analysis():
    try:
        spotify_token = flask.session.get('spotify_token')
        if not spotify_token:
            return flask.redirect('/')
        
        song_id = flask.request.form.get("analysis_id")
        song_title = flask.request.form.get("song_name")
        song_artist_name = flask.request.form.get("song_artist_name")
        
        if not song_id or not song_title or not song_artist_name:
            return "Missing song information", 400
        
        stats = _song_analysis_details(spotify_token , song_id , False , song_title , song_artist_name)
        
        if not stats or stats == "ERROR":
            print(stats)
            error_message = f"Unable to analyze '{song_title}' by {song_artist_name}. "
            error_message += "This song may not be available for analysis due to regional restrictions or premium content requirements."
            return error_message, 500
        
        stats['song_title'] = song_title
        stats['song_artist_name'] = song_artist_name

        # add to total amount analyzed
        flask.session['amount'] += 1

        print("\nSEARCHED SONG "  )

        # DATA POINTS FOR BAR GRAPH
        spotty_chart_datapoint_labels = [
            'danceability',
            'energy',
            'speechiness',
            'acousticness',
            # 'instrumentalness',
            'liveness',
            'valence',
        ]

        # PIE CHART
        ai_response = False
        if stats['ai']['lyrics'] is not None : 
            ai_response = True
            emotionsLabels = list(stats['ai']['nlu']['averageEmotion'].keys())
            emotionValues = [    stats['ai']['nlu']['averageEmotion'][i] for i in emotionsLabels  ]

        if ai_response: #kinda redundant but i mean.... why not have the modularity?
            content = {
                'stats'  : stats,
                'ai_response'  : ai_response,

                # spotify data
                'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
                'spotty_chart_data' :  [stats[i] for i in spotty_chart_datapoint_labels   ]  ,

                # watson data
                'emotionLabels' : emotionsLabels,
                'emotionValues' : emotionValues,
            }
        else: #NO LYRICS
            content = {
                'stats'  : stats,
                'ai_response'  : ai_response,
                'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
                'spotty_chart_data' :  [stats[i] for i in spotty_chart_datapoint_labels   ]  ,

                # watson data
                'emotionLabels' : None,
                'emotionValues' : None,
            }

        return flask.render_template('song_analysis.html' , content = content)
        
    except Exception as e:
        print(f"ERROR in song_analysis: {e}")
        return "An error occurred while analyzing the song. Please try again.", 500




# NOTE:
    # GROUP ANALYSIS IS A LITTLE DIFFERENT FROM LIKES ANALYSIS
    # both variables are dictionaries with numbers as keys starting at zero
    # each value is another dictionary with keys :  ['owner', 'name', 'description', 'id', 'songs']
    # musicGroup['songs'] is an array with tuples 
    # each tuple is ( "id" ,  "title" , ["artists"]  )


# Album Analysis
@application.route('/album-analysis', methods=['GET'])
def album_analysis():
    # grab music
    spotify_token = flask.session.get('spotify_token')
    albums = user_albums(spotify_token)

    # GROUP ANALYSIS FUNCTION USES THE  liked_group_average() function
    final  = group_music_analysis(spotify_token, albums)

    # Add amount to total analyized
    flask.session['amount'] += final['ai']['amount']

    # GRAPHING

    # DATA POINTS FOR BAR GRAPH
    spotty_chart_datapoint_labels = [
        'danceability',
        'energy',
        'speechiness',
        'acousticness',
        # 'instrumentalness',
        'liveness',
        'valence',
    ]

    # PIE CHART
    ai_response = False
    if final['ai'] is not None : 
        ai_response = True
        emotionsLabels = list(final['ai']['averageEmotion'].keys())
        emotionValues = [    final['ai']['averageEmotion'][i] for i in emotionsLabels  ]

    # No point to change as it is the same code as the song analysis from here to the components in html...
    USERNAME = fetch_spotify_data( spotify_token , 'https://api.spotify.com/v1/me' )
    final['song_title'] = USERNAME['display_name']
    final['song_artist_name'] = "Playlist Total Analyses"


    #kinda redundant but i mean.... why not have the modularity?
    if ai_response:
        content = {
            'stats'  : final,
            'ai_response'  : ai_response,
            # 'each_song_stats'  : each_song_stats,

            # spotify data
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [final[i] for i in spotty_chart_datapoint_labels   ]  ,

            # watson data
            'emotionLabels' : emotionsLabels,
            'emotionValues' : emotionValues,
        }

    #NO LYRICS
    else:
        content = {
            'stats'  : final,
            # 'each_song_stats'  : each_song_stats,
            'ai_response'  : ai_response,
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [final[i] for i in spotty_chart_datapoint_labels   ]  ,
            # watson data
            'emotionLabels' : None,
            'emotionValues' : None,
        }


    # sessions for passed songs on html

    return flask.render_template('Liked_Group_analysis.html' , content = content)

# Playlist Analysis
@application.route('/playlist-analysis', methods=['GET'])
def playlist_analysis():

    # grab music
    spotify_token = flask.session.get('spotify_token')
    playlist_response = user_playlists(spotify_token)

    # GROUP ANALYSIS FUNCTION USES THE  liked_group_average() function
    final  = group_music_analysis(spotify_token, playlist_response)

    # Add amount to total analyized
    flask.session['amount'] += final['ai']['amount']


    # GRAPHING

    # DATA POINTS FOR BAR GRAPH
    spotty_chart_datapoint_labels = [
        'danceability',
        'energy',
        'speechiness',
        'acousticness',
        # 'instrumentalness',
        'liveness',
        'valence',
    ]

    # PIE CHART
    ai_response = False
    if final['ai'] is not None : 
        ai_response = True
        emotionsLabels = list(final['ai']['averageEmotion'].keys())
        emotionValues = [    final['ai']['averageEmotion'][i] for i in emotionsLabels  ]

    # No point to change as it is the same code as the song analysis from here to the components in html...
    USERNAME = fetch_spotify_data( spotify_token , 'https://api.spotify.com/v1/me' )
    final['song_title'] = USERNAME['display_name']
    final['song_artist_name'] = "Playlist Total Analyses"


    #kinda redundant but i mean.... why not have the modularity?
    if ai_response:
        content = {
            'stats'  : final,
            'ai_response'  : ai_response,
            # 'each_song_stats'  : each_song_stats,

            # spotify data
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [final[i] for i in spotty_chart_datapoint_labels   ]  ,

            # watson data
            'emotionLabels' : emotionsLabels,
            'emotionValues' : emotionValues,
        }

    #NO LYRICS
    else:
        content = {
            'stats'  : final,
            # 'each_song_stats'  : each_song_stats,
            'ai_response'  : ai_response,
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [final[i] for i in spotty_chart_datapoint_labels   ]  ,
            # watson data
            'emotionLabels' : None,
            'emotionValues' : None,
        }


    # sessions for passed songs on html

    return flask.render_template('Liked_Group_analysis.html' , content = content)




# INDIVISUAL GROUP DISPLAY
# Display all albums and links next to them to pictures of the album
@application.route('/indivisual-album-display', methods=['GET'])
def indivisualAlbumDisplay():

    # going to hold every album and their display data ['pictures'] , ['popularity'], ['name'] , ['uri']
    display_data = {
        'username' : flask.session['username'] 
    }

    # grab music
    spotify_token = flask.session.get('spotify_token')
    albums = user_albums(spotify_token)

    # gather pictures
    for album in albums:
        album_id = albums[album]["id"]
        data = fetch_spotify_data(spotify_token , f"https://api.spotify.com/v1/albums/{album_id}")

        # add to display data
        display_data[album] = {}
        display_data[album]['name'] = albums[album]['name']
        display_data[album]['id'] = album_id
        display_data[album]['pictures'] = data['images']
        display_data[album]['popularity'] = albums[album]['popularity']
        display_data[album]['amount'] = len(  albums[album]['songs']  )
        display_data[album]['release_date'] = data['release_date']
        display_data[album]['spotify_page'] = f"https://open.spotify.com/track/{album_id}"
        display_data[album]['songs'] = albums[album]['songs']




    # debug = fetch_spotify_data(spotify_token , f"https://api.spotify.com/v1/albums/5SKnXCvB4fcGSZu32o3LRY?si=17b25a68a03c497b")


    
    return flask.render_template('indivisual_group_listing.html' , display_data = display_data)

@application.route('/indivisual-playlist-display', methods=['GET'])
def indivisualPlaylistDisplay():
    # grab music
    spotify_token = flask.session.get('spotify_token')
    playlist_response = user_playlists(spotify_token)

    # going to hold every album and their display data ['pictures'] , ['popularity'], ['name'] , ['uri']
    display_data = {
        'username' : flask.session['username'] 
    }

    # gather pictures
    for pl in playlist_response:
        playlist_id = playlist_response[pl]["id"]
        data = fetch_spotify_data(spotify_token , f"https://api.spotify.com/v1/playlists/{playlist_id}")

        # add to display data
        display_data[ pl ] = {}
        display_data[ pl ]['name'] = playlist_response[pl]['name']
        display_data[ pl ]['id'] = playlist_id
        display_data[ pl ]['pictures'] = data['images']
        display_data[ pl ]['amount'] = len(  playlist_response[pl]['songs']  )
        display_data[ pl ]['spotify_page'] = f"https://open.spotify.com/playlist/{playlist_id}"
        display_data[ pl ]['popularity'] = f"{data['followers']['total']} listeners"
        display_data[ pl ]['songs'] =  playlist_response[pl]['songs']
        

        # PLAYLIST DATA DOESNT RETURN (fetch_album does)
        # display_data[ pl ]['release_date'] = data['release_date']

    return flask.render_template('indivisual_group_listing.html' , display_data = display_data)

# ALMBUM FINAL ANALYSIS
@application.route('/indivisual-album-analysis', methods=['POST'])
def indivisual_album_analysis():
    spotify_token = flask.session.get('spotify_token')



    # grab context from form POST  from /indivisual-playlist-display 
    user_form_args = flask.request.form
    # print(user_form_args)
    
    # display page passed in list of songs from the form
    music_list = flask.request.form.get('songs[]') 

    # convert string return from form into list
    music_list = ast.literal_eval(music_list)
    # music_list = music_list.strip('][').split(', ')


    # clean list into format that fits the liked_group_average() format
    for x in range(0 , len(music_list) , 1):
        # print(   music_list[x] )

        song_info = {
            "artists"  : music_list[x][2],
            "name"  :  music_list[x][1] ,
            "id"  :  music_list[x][0],
        }

        # replace music list with song info
        music_list[x] = song_info


    # this function returns two for parallel display of each (song) & grouped ai
    song_stats , each_song_stats = liked_group_average(spotify_token , music_list)
    
    # Add amount to total analyized
    flask.session['amount'] += song_stats['ai']['amount']

    # GRAPHING

    # DATA POINTS FOR BAR GRAPH
    spotty_chart_datapoint_labels = [
        'danceability',
        'energy',
        'speechiness',
        'acousticness',
        # 'instrumentalness',
        'liveness',
        'valence',
    ]

    # PIE CHART
    ai_response = False
    if song_stats['ai'] is not None : 
        ai_response = True
        emotionsLabels = list(song_stats['ai']['averageEmotion'].keys())
        emotionValues = [    song_stats['ai']['averageEmotion'][i] for i in emotionsLabels  ]

    # No point to change as it is the same code as the song analysis from here to the components in html...
    USERNAME = fetch_spotify_data( spotify_token , 'https://api.spotify.com/v1/me' )
    song_stats['song_title'] = USERNAME['display_name']
    song_stats['song_artist_name'] = user_form_args["group_name"]


    #kinda redundant but i mean.... why not have the modularity?
    if ai_response:
        content = {
            'stats'  : song_stats,
            'ai_response'  : ai_response,
            'each_song_stats'  : each_song_stats,

            # spotify data
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [song_stats[i] for i in spotty_chart_datapoint_labels   ]  ,

            # watson data
            'emotionLabels' : emotionsLabels,
            'emotionValues' : emotionValues,
        }

    #NO LYRICS
    else:
        content = {
            'stats'  : song_stats,
            'each_song_stats'  : each_song_stats,
            'ai_response'  : ai_response,
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [song_stats[i] for i in spotty_chart_datapoint_labels   ]  ,
            # watson data
            'emotionLabels' : None,
            'emotionValues' : None,
        }


    # sessions for passed songs on html

    return flask.render_template('Liked_Group_analysis.html' , content = content)

# Playlist FINAL ANALYSIS
@application.route('/indivisual-playlist-analysis', methods=['POST'])
def indivisual_playlist_analysis():
    spotify_token = flask.session.get('spotify_token')



    # grab context from form POST  from /indivisual-playlist-display 
    user_form_args = flask.request.form
    # print(user_form_args)
    
    # display page passed in list of songs from the form
    music_list = flask.request.form.get('songs[]') 

    # convert string return from form into list
    music_list = ast.literal_eval(music_list)
    # music_list = music_list.strip('][').split(', ')


    # clean list into format that fits the liked_group_average() format
    for x in range(0 , len(music_list) , 1):
        # print(   music_list[x] )

        song_info = {
            "artists"  : music_list[x][2],
            "name"  :  music_list[x][1] ,
            "id"  :  music_list[x][0],
        }

        # replace music list with song info
        music_list[x] = song_info


    # this function returns two for parallel display of each (song) & grouped ai
    song_stats , each_song_stats = liked_group_average(spotify_token , music_list)
    
    # Add amount to total analyized
    flask.session['amount'] += song_stats['ai']['amount']

    # GRAPHING

    # DATA POINTS FOR BAR GRAPH
    spotty_chart_datapoint_labels = [
        'danceability',
        'energy',
        'speechiness',
        'acousticness',
        # 'instrumentalness',
        'liveness',
        'valence',
    ]

    # PIE CHART
    ai_response = False
    if song_stats['ai'] is not None : 
        ai_response = True
        emotionsLabels = list(song_stats['ai']['averageEmotion'].keys())
        emotionValues = [    song_stats['ai']['averageEmotion'][i] for i in emotionsLabels  ]

    # No point to change as it is the same code as the song analysis from here to the components in html...
    USERNAME = fetch_spotify_data( spotify_token , 'https://api.spotify.com/v1/me' )
    song_stats['song_title'] = USERNAME['display_name']
    song_stats['song_artist_name'] = user_form_args["group_name"]


    #kinda redundant but i mean.... why not have the modularity?
    if ai_response:
        content = {
            'stats'  : song_stats,
            'ai_response'  : ai_response,
            'each_song_stats'  : each_song_stats,

            # spotify data
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [song_stats[i] for i in spotty_chart_datapoint_labels   ]  ,

            # watson data
            'emotionLabels' : emotionsLabels,
            'emotionValues' : emotionValues,
        }

    #NO LYRICS
    else:
        content = {
            'stats'  : song_stats,
            'each_song_stats'  : each_song_stats,
            'ai_response'  : ai_response,
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [song_stats[i] for i in spotty_chart_datapoint_labels   ]  ,
            # watson data
            'emotionLabels' : None,
            'emotionValues' : None,
        }


    # sessions for passed songs on html

    return flask.render_template('Liked_Group_analysis.html' , content = content)


# Recently played tracks analysis
@application.route('/recent-analysis', methods=['GET'])
def recent_analysis():
    spotify_token = flask.session.get('spotify_token')
    if not spotify_token:
        return flask.redirect('/')
    
    # Get recently played tracks
    recent_tracks = user_recently_played(spotify_token, limit=50)
    
    if not recent_tracks:
        return "No recently played tracks found.", 404
    
    # Convert to format expected by liked_group_average
    tracks_for_analysis = []
    for track in recent_tracks:
        track_info = {
            'id': track['id'],
            'name': track['name'],
            'artists': track['artists']
        }
        tracks_for_analysis.append(track_info)
    
    # Analyze tracks using existing function
    song_stats, each_song_stats = liked_group_average(spotify_token, tracks_for_analysis)
    
    # Add amount to total analyzed
    flask.session['amount'] += song_stats['ai']['amount'] if song_stats.get('ai') else 0
    
    # Prepare chart data
    spotty_chart_datapoint_labels = [
        'danceability',
        'energy',
        'speechiness',
        'acousticness',
        'liveness',
        'valence',
    ]
    
    # Check if we have AI analysis
    ai_response = False
    emotionsLabels = None
    emotionValues = None
    
    if song_stats.get('ai') and song_stats['ai']:
        ai_response = True
        if song_stats['ai'].get('averageEmotion'):
            emotionsLabels = list(song_stats['ai']['averageEmotion'].keys())
            emotionValues = [song_stats['ai']['averageEmotion'][i] for i in emotionsLabels]
    
    # Prepare context
    if ai_response:
        content = {
            'stats': song_stats,
            'ai_response': ai_response,
            'spotty_chart_labels': spotty_chart_datapoint_labels,
            'spotty_chart_data': [song_stats[i] for i in spotty_chart_datapoint_labels],
            'emotionLabels': emotionsLabels,
            'emotionValues': emotionValues,
        }
    else:
        content = {
            'stats': song_stats,
            'ai_response': ai_response,
            'spotty_chart_labels': spotty_chart_datapoint_labels,
            'spotty_chart_data': [song_stats[i] for i in spotty_chart_datapoint_labels],
            'emotionLabels': None,
            'emotionValues': None,
        }
    
    # Add metadata
    USERNAME = fetch_spotify_data(spotify_token, 'https://api.spotify.com/v1/me')
    song_stats['song_title'] = USERNAME['display_name']
    song_stats['song_artist_name'] = "Recently Played Tracks"
    
    return flask.render_template('Liked_Group_analysis.html', content=content)

# liked songs Analysis
@application.route('/liked-analysis', methods=['GET'])
def liked_analysis():
    spotify_token = flask.session.get('spotify_token')
    likes = user_likes(spotify_token)

    # this function returns two for parallel display of each (song) & grouped ai
    song_stats , each_song_stats = liked_group_average(spotify_token , likes)
    
    # Add amount to total analyized
    flask.session['amount'] += song_stats['ai']['amount']



    # GRAPHING

    # DATA POINTS FOR BAR GRAPH
    spotty_chart_datapoint_labels = [
        'danceability',
        'energy',
        'speechiness',
        'acousticness',
        # 'instrumentalness',
        'liveness',
        'valence',
    ]

    # PIE CHART
    ai_response = False
    if song_stats['ai'] is not None : 
        ai_response = True
        emotionsLabels = list(song_stats['ai']['averageEmotion'].keys())
        emotionValues = [    song_stats['ai']['averageEmotion'][i] for i in emotionsLabels  ]

    # No point to change as it is the same code as the song analysis from here to the components in html...
    USERNAME = fetch_spotify_data( spotify_token , 'https://api.spotify.com/v1/me' )
    song_stats['song_title'] = USERNAME['display_name']
    song_stats['song_artist_name'] = "❤"


    #kinda redundant but i mean.... why not have the modularity?
    if ai_response:
        content = {
            'stats'  : song_stats,
            'ai_response'  : ai_response,
            'each_song_stats'  : each_song_stats,

            # spotify data
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [song_stats[i] for i in spotty_chart_datapoint_labels   ]  ,

            # watson data
            'emotionLabels' : emotionsLabels,
            'emotionValues' : emotionValues,
        }

    #NO LYRICS
    else:
        content = {
            'stats'  : song_stats,
            'each_song_stats'  : each_song_stats,
            'ai_response'  : ai_response,
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [song_stats[i] for i in spotty_chart_datapoint_labels   ]  ,
            # watson data
            'emotionLabels' : None,
            'emotionValues' : None,
        }


    # sessions for passed songs on html

    return flask.render_template('Liked_Group_analysis.html' , content = content)











# FLASK ERRORS
@application.errorhandler(404)
def page_not_found(e):
    return flask.render_template('error.html', 
                               error_title='Page Not Found',
                               error_message='The page you are looking for does not exist.'), 404

@application.errorhandler(500)
def handle_internal_error(e):
    return flask.redirect('/Dashboard')

@application.errorhandler(400)
def handle_bad_request(e):
    return flask.render_template('error.html',
                               error_title='Bad Request',
                               error_message='The request could not be processed. Please check your input and try again.')

@application.errorhandler(401)
def handle_unauthorized(e):
    return flask.redirect('/')

# Custom error route
@application.route('/error')
def show_error():
    error_title = flask.request.args.get('title', 'An error occurred')
    error_message = flask.request.args.get('message', 'Something went wrong')
    error_details = flask.request.args.get('details', '')
    
    return flask.render_template('error.html',
                               error_title=error_title,
                               error_message=error_message,
                               error_details=error_details)







# SPOTIFY AND GENIUS AUTHORIZATIONS

#  Authorization by getting token
def authorize_spotify_NO_USER():
    url = "https://accounts.spotify.com/api/token"
    headers = {}
    data = {}

    # Encode as Base64
    message = f"{spotify_clientId}:{spotify_clientSecret}"
    messageBytes = message.encode('ascii')
    base64Bytes = base64.b64encode(messageBytes)
    base64Message = base64Bytes.decode('ascii')

    headers['Authorization'] = f"Basic {base64Message}"
    data['grant_type'] = "client_credentials"


    r = requests.post(url, headers=headers, data=data).json()

    token = r['access_token']
    return token
def authorize_spotify_IMPLICIT(): 

    headers = {
        'client_id' : spotify_clientId,
        'response_type' : 'token',
        'redirect_uri' : spotify_callbackURL,
        'scope' : spotty_full_permission,
    }

    # open url on browser
    url = f"https://accounts.spotify.com/authorize?client_id={headers['client_id']}&response_type={headers['response_type']}&redirect_uri={headers['redirect_uri']}&scope={headers['scope']}"

    return url
def authorize_spotify_REFRESHABLE(): 

    headers = {
        'client_id' : spotify_clientId,
        'response_type' : 'code',
        'redirect_uri' : spotify_callbackURL,
        'scope' : spotty_full_permission,
    }

    # open url on browser
    url = f"https://accounts.spotify.com/authorize?client_id={headers['client_id']}&response_type={headers['response_type']}&redirect_uri={headers['redirect_uri']}&scope={headers['scope']}"
    return url
def _retrieve_refreshable_token(auth_code):
    """Exchange authorization code for access and refresh tokens"""
    url = "https://accounts.spotify.com/api/token"
    headers = {}
    data = {}

    # Encode as Base64
    message = f"{spotify_clientId}:{spotify_clientSecret}"
    messageBytes = message.encode('ascii')
    base64Bytes = base64.b64encode(messageBytes)
    base64Message = base64Bytes.decode('ascii')

    headers['Authorization'] = f"Basic {base64Message}"
    data['grant_type'] = "authorization_code"
    data['code'] = auth_code
    data['redirect_uri'] = spotify_callbackURL

    try:
        r = requests.post(url, headers=headers, data=data)
        r.raise_for_status()
        response_data = r.json()
        
        return {
            'access_token': response_data['access_token'],
            'refresh_token': response_data.get('refresh_token'),
            'expires_in': response_data.get('expires_in', 3600)
        }
    except Exception as e:
        print(f"ERROR: Failed to retrieve Spotify tokens: {e}")
        return None

def _refresh_spotify_token(refresh_token):
    """Refresh expired Spotify access token"""
    url = "https://accounts.spotify.com/api/token"
    headers = {}
    data = {}

    # Encode as Base64
    message = f"{spotify_clientId}:{spotify_clientSecret}"
    messageBytes = message.encode('ascii')
    base64Bytes = base64.b64encode(messageBytes)
    base64Message = base64Bytes.decode('ascii')

    headers['Authorization'] = f"Basic {base64Message}"
    data['grant_type'] = "refresh_token"
    data['refresh_token'] = refresh_token

    try:
        r = requests.post(url, headers=headers, data=data)
        r.raise_for_status()
        response_data = r.json()
        
        return {
            'access_token': response_data['access_token'],
            'refresh_token': response_data.get('refresh_token', refresh_token),  # Keep old refresh token if new one not provided
            'expires_in': response_data.get('expires_in', 3600)
        }
    except Exception as e:
        print(f"ERROR: Failed to refresh Spotify token: {e}")
        return None
def _retrieve_genius_token(auth_code):
    # Exchange authorization code for access token
    url = "https://api.genius.com/oauth/token"
    
    data = {
        'code': auth_code,
        'client_id': genius_clientId,
        'client_secret': genius_clientsECRET,
        'grant_type': "authorization_code",
        'redirect_uri': genius_callbackURL
    }
    
    try:
        r = requests.post(url, data=data)
        r.raise_for_status()  # Raise exception for bad status codes
        
        response_data = r.json()
        
        if 'access_token' in response_data:
            token = response_data['access_token']
            print(f"SUCCESS: Retrieved Genius token for {flask.request.remote_addr}")
            return token
        else:
            print(f"ERROR: No access_token in Genius response: {response_data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request failed for Genius token: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Failed to retrieve Genius token: {e}")
        return None

# Genius 
def Oauth_function(base_url, CLIENT_ID, callback, scope, clientsECRET, res_type):
    # For Genius OAuth, we don't need client_secret in the authorization URL
    # Only include the required parameters for the authorization step
    url = f'{base_url}?client_id={CLIENT_ID}&redirect_uri={callback}&scope={scope}&response_type={res_type}'
    return url



# SPOTIFFY ENDPOINTS
def fetch_spotify_data(token , endpoint ):
    try:
        headers = {"Authorization": "Bearer " + token}
        response = requests.get(url=endpoint, headers=headers)
        response.raise_for_status()
        res = response.json()
        
        if 'error' in res:
            error_msg = res['error'].get('message', 'Unknown error')
            print(f"\n{flask.request.remote_addr} -------\nERROR {error_msg} \n")
            flask.session['spotify_expired'] = True
            return f"ERROR"
        
        return res
    except requests.exceptions.RequestException as e:
        print(f"\n{flask.request.remote_addr} -------\nREQUEST ERROR: {str(e)} \n")
        flask.session['spotify_expired'] = True
        return f"ERROR"
    except Exception as e:
        print(f"\n{flask.request.remote_addr} -------\nUNEXPECTED ERROR: {str(e)} \n")
        flask.session['spotify_expired'] = True
        return f"ERROR"





# grab music groups
def user_likes(token):
   
    # LOOKUP SONGS
    # headers = {"Authorization": "Bearer " + token}
    results = fetch_spotify_data(token , 'https://api.spotify.com/v1/me/tracks' )
    all_songs = []
    totalLikedSongs = int(results['total'])
    while results:   
        for idx, item in enumerate(results['items']):
            track = item['track']
            song_info = {
                "artists"  : [  track['artists'][i]['name']  for i in range(len(track['artists']))  ],
                "name"  :  track['name'] ,
                "id"  :  track['id'],
                "popularity"  :  track['popularity']
            }
            all_songs.append( song_info )
       
        #next page check
        if results['next']: 
            results = fetch_spotify_data(token , results['next'] )
        else:
            results = None

    return all_songs
def user_albums(token):
    playlistUrl = f"https://api.spotify.com/v1/me/albums"
    headers = {"Authorization": "Bearer " + token}
    results = requests.get(url=playlistUrl, headers=headers).json()

    # GRAB ALBUMS
    all_albums = {}
    count = 0
    while results:  
        for item in results['items']:
            album = item['album']
            all_albums[count] =  {
                'name' : item['album']['name'],
                "genres" : album['genres'],
                "id" : album['id'],
                "popularity" : album['popularity'],
                "songs" : [],
            }
            # ADD SONGS
            for track in item['album']['tracks']['items']:
                all_albums[count]['songs'].append(   (track['id'] , track['name']    ,  [i['name'] for i in track['artists']  ]  )   )
            count += 1

        if results['next']: #next page check
            results = requests.get(url=results['next'], headers=headers).json()
        else:
            results = None
    
    
    
    return all_albums
def user_playlists(token):
    playlistUrl = f"https://api.spotify.com/v1/me/playlists"
    headers = {"Authorization": "Bearer " + token}
    results = requests.get(url=playlistUrl, headers=headers).json()

    all_playlists = {}
    count = 0
    # EVERY PLAYLIST
    while results:   
        for item in results['items']:
            all_playlists[count] =  {
                'owner' : item['owner']['display_name'],
                'name' : item['name'],
                "description" : item['description'],
                "id" : item['id'],
                "songs" : [],
            }

            # LOOKUP SONGS (pagination using key next)
            pl_tracks_call = requests.get(url=item['tracks']['href'] , headers = headers).json()
            while pl_tracks_call:
                for track in pl_tracks_call['items']:
                    
                    all_playlists[count]['songs'].append(   (track['track']['id'] , track['track']['name']  ,[ i['name'] for i in track['track']['artists']  ] )   )
            
                # PAGINATION [TRACKS]
                if pl_tracks_call['next']:
                    pl_tracks_call = requests.get(url=pl_tracks_call['next'] , headers = headers).json()
                else:
                    pl_tracks_call = None
            
            count += 1

         # PAGINATION [PLAYLISTS]
        if results['next']:
            results = requests.get(url=item['next'] , headers = headers).json()
        else:
            results = None
    return all_playlists

def user_recently_played(token, limit=20):
    """Fetch user's recently played tracks from Spotify"""
    try:
        # Get recently played tracks
        endpoint = f"https://api.spotify.com/v1/me/player/recently-played?limit={limit}"
        results = fetch_spotify_data(token, endpoint)
        
        if results == "ERROR":
            print("ERROR: Failed to fetch recently played tracks")
            return []
        
        recent_tracks = []
        for item in results.get('items', []):
            track = item['track']
            played_at = item['played_at']
            
            # Get artist image for thumbnail
            thumbnail = '/static/fallback.svg'
            if track.get('artists') and len(track['artists']) > 0:
                artist_href = track['artists'][0].get('href')
                if artist_href:
                    artist_data = fetch_spotify_data(token, artist_href)
                    if artist_data != "ERROR" and artist_data.get('images'):
                        thumbnail = artist_data['images'][-1]['url']
            
            # GET TRACK INFO
            track_info = {
                'id': track['id'],
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'album': track['album']['name'],
                'thumbnail': thumbnail,
                'played_at': played_at,
                'popularity': track.get('popularity', 0)
            }
            recent_tracks.append(track_info)
        
        return recent_tracks
        
    except Exception as e:
        print(f"ERROR: Failed to fetch recently played tracks: {e}")
        return []






# song AI  analysis 
def _song_analysis_details(token , song_id , details : bool , song_title , artist_name): 

    # check if song in database already
    try:
        with open('song_db.json' , "r") as db:
            loaded = json.load(db)
            if song_id in loaded:
                return loaded[song_id]
    except (FileNotFoundError, json.JSONDecodeError):
        # Create empty database if it doesn't exist
        loaded = {}

    endpoint = f"https://api.spotify.com/v1/audio-features/{song_id}"
    titleInfo = fetch_spotify_data(token, f'https://api.spotify.com/v1/tracks/{song_id}')
    
    if titleInfo == "ERROR":
        print(f"ERROR: Failed to fetch track info for {song_id}")
        return None
        
    try:
        song_title = titleInfo['name']  
        artist_name = titleInfo['artists'][0]['name']
    except (KeyError, IndexError, TypeError):
        print(f"ERROR: Invalid track info structure for {song_id}")
        return None

    # fetch data
    res = fetch_spotify_data(token , endpoint )
    
    if res == "ERROR":
        print(f"ERROR: Failed to fetch audio features for {song_id}")
        print(f"  Song: {song_title} by {artist_name}")
        print(res)
        # Additional debugging for 403 errors
        try:
            headers = {"Authorization": "Bearer " + token}
            response = requests.get(url=endpoint, headers=headers)
            
            if response.status_code == 403:
                print(f"DEBUG: 403 Forbidden - Checking token scopes...")
                print(f"DEBUG: Token starts with: {token[:20]}...")
                
                # Validate token scopes
                if validate_token_scopes(token):
                    print(f"DEBUG: Token is valid for basic endpoints")
                    print(f"DEBUG: 403 error suggests insufficient scopes for audio features")
                    print(f"DEBUG: Required scopes for audio features: user-read-private, user-read-email")
                    print(f"DEBUG: Current token may be missing required scopes")
                else:
                    print(f"DEBUG: Token validation failed - token may be expired or invalid")
                    
            elif response.status_code == 401:
                print(f"DEBUG: 401 Unauthorized - Token expired or invalid")
            else:
                print(f"DEBUG: HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"DEBUG: Error during debugging: {e}")
        
        return None

    # SONG DETAIL DOUBLE FEATURE of the function
    if details:
        try:
            analysis = requests.get( url = res['analysis_url'], headers = {"Authorization": "Bearer " + token} ).json()
            pprint.pprint( analysis.keys()  );print("\n")
            pprint.pprint( analysis['track']   )
            return analysis
        except Exception as e:
            print(f"ERROR: Failed to fetch detailed analysis: {e}")
            return None

    # check if response was a dictionary
    if isinstance(res , dict):
        pass
    else:
        print(f"ERROR: Invalid response type for {song_id}: {type(res)}")
        return None

    # API COOL DOWN ERROR HANDLING
    while 'error' in res.keys():
        print(f'< {song_id} > got an error\n waiting for api cooldown')
        time.sleep(API_COOLDOWN_RATE)
        res = _song_analysis_details(token, song_id , details, song_title, artist_name )
    
    # append WATSON AI to SOTIFY results  (master dictionary of clean watson frequencies)
    res['ai'] = _watson_lyric_analysis( song_title, artist_name)
    res['song_title'] = song_title
    res['artist_name'] = artist_name

    # adding items to song_db.json DATABASE
    try:
        with open('song_db.json' , 'r') as db:
            loaded = json.load( db )
            loaded[song_id] = res
        with open('song_db.json' , 'w') as db:
            db.write( json.dumps(loaded) )
    except Exception as e:
        print(f"ERROR: Failed to save to database: {e}")

    return res

def _watson_lyric_analysis(  song_title, artist_name):
    print(f"\nAnalyzing {artist_name} : {song_title}")
    genius_token = flask.session.get("genius_token")
    lyrics = _request_song_info(genius_token , song_title , artist_name )

    # NLU
    song_ai = []
    nlu = None
    if lyrics:
        # INSTEAD OF GRABBING AI RESPONSE FOR EACH BAR... JUST RUN THE WHOLE LYRIC STRING
        watson_input = ""
        try:
            # APPEND LYRICS
            for bar in lyrics:
                watson_input += f"{bar} "
            # GET WATSON INFO
            nlu = watson.ai_to_Text( watson_input )
            # AVERAGE CALC IS RETURNING CLEAN DATA by reading an array,
            # WE PLACE ONE ITEM IF WE DECIDE TO RUN LYRICS AS ONE
            nlu =  watson.averages_calc(   [  nlu  ]   )

        except Exception as e:
            nlu = None
            print(f'\n\nWATSON API ERROR: {e}\n\n\n{watson_input}\n')
    else:
        print("No lyrics found\n")

    context = {
        'lyrics' : lyrics,
        'nlu' : nlu,
        # 'tone' : tone
    }
    return context

def _request_song_info(token, song_title, artist_name):
    base_url = 'https://api.genius.com'
    # Use the stored Genius API key directly
    headers = {'Authorization': 'Bearer ' + genius_api_key}
    search_url = base_url + '/search'
    data = {'q': song_title + ' ' + artist_name}
    response = requests.get(search_url, data=data, headers=headers).json()

    # Search for matches in the request response
    remote_song_info = None
    for hit in response['response']['hits']:
        if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
            remote_song_info = hit
            break

    # Extract lyrics from URL if the song was found
    if remote_song_info:
        song_url = remote_song_info['result']['url']
        return _webcrawl_lyrics(song_url)
    else:
        return None

def _webcrawl_lyrics(url):
    # EXTRACT HTML
    page = requests.get(url)
    html = bs4.BeautifulSoup(page.text, 'html.parser')

    try:
        lyrics = html.find("div", {"id": "lyrics-root-pin-spacer"}).get_text()
    except Exception as e:
        print(  '\ndef _webcrawl_lyrics(url):\nERROR FINDING LYRICS: ' , str(e))
        return None


    
    # CREATE ARRAY THAT FINDS A LOWER CASE AND AN UPPERCASE RIGHT NEXT TO EACHOTHER AND SPLITS STRING
    lyrics_text = str(lyrics)
    all_bars = []
    br_point = 0
    previous = 0
    for x in range(0, len(lyrics_text)  - 1 , 1)  :
        if  lyrics_text[x].islower() and lyrics_text[x+1].isupper():
            br_point = x+1
            bar = lyrics_text[previous:br_point]
            all_bars.append(bar)
            previous = br_point
        

    # removing "[ SONG EVENT ]" from each bar
    event_start = None
    event_end = None
    for x in all_bars:
        found = False
        for y in range(len(x)):
            if x[y] == '['  : event_start = y  
            if x[y] == ']'  :
                found = True
                event_end = y
                no_event_bar = x[:event_start] + ' ' + x[event_end+1:]
        if found:
            x = no_event_bar

    all_bars.remove('Share URLCopy')
    if "1Embed" in all_bars:
        all_bars.remove('1Embed')
    if all_bars[-1] == "Embed":
        all_bars.pop(-1)
    if len(all_bars) <= 3:
        all_bars = None

    return all_bars




# music group analysis

def group_music_analysis(token , group:dict() ):
    final  = {
        'acousticness' : [],
        'danceability' : [],
        'duration_ms' : [],
        'energy' : [],
        'instrumentalness' : [],
        'liveness' : [],
        'loudness' : [],
        'speechiness' : [],
        'tempo' : [],
        'valence' : [],
        'ai' : []
    }

    # songs found by WATSON
    watson_arr = []

    for album in group:
        print("\n\n--------" ,  group[album]["name"] , "------"  )
        for song in group[album]['songs']:
            song_id = song[0]
            song_name = song[1]
            song_artists = song[2] #main artist is item number 0
            analysis = _song_analysis_details(token,  song_id , False ,  song_name , song_artists[0] )
            
            # check if response returned a dictionary
            if isinstance(analysis , dict):
                pass
            else:
                print('\n----- DEBUG -----\n------ group_music_analysis(token , group:dict() ) --------')
                print("Spotify returned a Response type instead of JSON")
                continue


            # populates all songs into final song_stat variable
            for x in final.keys():
                final[x].append(analysis[x])
                
            # check if watson ai
            if analysis['ai']['nlu'] is not None:
                print("☁☁☁")
                watson_arr.append(  (analysis['song_title'] , analysis['artist_name']  )   )



    # AVERAGING  SPOTIFY  #every key except ["ai"]
    spotty_keys = list(final.keys())[:-1]
    for attribute in spotty_keys:
        final[attribute] =  statistics.mean(final[attribute])
    


    # ----------------AVERAGING WATSON for FINAL ["ai"]   --------------------
    group_merge_ai = {}

    # CHECKING FOR PROPER nlu DICTIONARY && creating merged dict...
    solid_nlu = False
    for x in range(  len(final['ai'])   ):
        if final['ai'][x]['nlu'] is not None :
            solid_nlu = True
            good_dict = final['ai'][x]['nlu']
            break
    if solid_nlu:
        for key in good_dict :
            if key =='averageEmotion':
                group_merge_ai[key] = []
                continue
            group_merge_ai[key] = {}
            for inner_keys in good_dict[key]:
                group_merge_ai[key][inner_keys] = []
    else: #IMPORTANT CATCH IF NO AI
        final['ai'] = None
        return final 


    # # # DEBUG
    # with open("group_merge_ai.json" , "a") as output:
    #     json.dump(group_merge_ai, output, indent = 2)


    # merge all values in NLU into group_merge_ai
    for x in range( 0 ,   len(final['ai'])   ,   1  ):
        NLU = final['ai'][x]['nlu']
        
        # APPEND ALL WATSON DATA INTO group_merge_ai , otherwise ignore it and move on
        if NLU is not None :
            # append all group emotions ------> EMOTIONS
            group_merge_ai['averageEmotion'].append(NLU['averageEmotion'])

            # create dict keys for all concept frequencies  ------> CONCEPTS
            singularities = []
            for i in NLU['conceptfrequencies']:
                # Singular keys found with empty arr
                if len( NLU['conceptfrequencies'][i] ) < 1:
                    print("DEBUG full group: singularity:   ", i)
                    singularities.append(i)
                    continue
                # if there the key already exists!
                if i in group_merge_ai['conceptfrequencies']:
                    # ITERATE THROUGH NLU['conceptfrequencies'][i]
                    for concept in NLU['conceptfrequencies'][i]:
                        if isinstance(concept, str):
                            group_merge_ai['conceptfrequencies'][i].append(concept)
                        elif isinstance(concept, list):
                            for inner_concept in concept:
                                group_merge_ai['conceptfrequencies'][i].append(inner_concept)
                else:
                    # if the concept is not in the dictionary as a key... add it with it's coentents as well
                    # print(NLU['conceptfrequencies'][i] )
                    group_merge_ai['conceptfrequencies'][i] = []
                    for concept in NLU['conceptfrequencies'][i]:
                        if isinstance(concept, str):
                            group_merge_ai['conceptfrequencies'][i].append(concept)
                        elif isinstance(concept, list):
                            for inner_concept in concept:
                                group_merge_ai['conceptfrequencies'][i].append(inner_concept)
            NLU['conceptfrequencies']['singularities'] = singularities


            # goes through dictionary and populates the merge
            for key in NLU.keys():
                if key == "averageEmotion" or  key == "conceptfrequencies":
                    continue
                for i in NLU[key]:
                    if isinstance(NLU[key][i], int):
                        if  i  in group_merge_ai[key]:
                            if isinstance(group_merge_ai[key][i], list):
                                group_merge_ai[key][i] = 1
                            else:
                                group_merge_ai[key][i] +=  NLU[key][i]
                        else:
                             group_merge_ai[key][i] = NLU[key][i]
                    else:
                        # print( group_merge_ai[key][i]  ) #/// VARIALE IN QUESION!
                        if i  in group_merge_ai[key]:
                            group_merge_ai[key][i].extend(  NLU[key][i]    )
                        else:
                            group_merge_ai[key][i] = NLU[key][i]

    # OVER ALL EMOTION AVERAGE
    temp = {
        "Anger": [],
        "Disgust": [],
        "Fear": [],
        "Joy": [],
        "Sadness": []
      }
    for x in  range( 0 , len(group_merge_ai['averageEmotion'])  ,   1 ):
        for key in group_merge_ai['averageEmotion'][x]:
            temp[key].append(group_merge_ai['averageEmotion'][x][key])
    # replace vars 
    for emotion in temp:
        temp[emotion] = statistics.mean(temp[emotion])


    # LISTS BECOMES MERGED DICTIONARIES
    group_merge_ai['amount'] = len(group_merge_ai['averageEmotion']) #FIND AMOUNT OF ANALYZED SONGS  
    group_merge_ai['averageEmotion'] = temp
    final['ai'] = group_merge_ai
    
    # remember watson_arr? 
    final['ai']['watson_songs'] = watson_arr
    


    # # DEBUG
    # with open("final.json" , "a") as output:
    #     json.dump(final, output, indent = 2)

    return final 

def liked_group_average(token , group : list()  ): 

    #  -------   spotify OUTPUT VARIABLES    -------
    # populate song arr
    song_stats  = {
        'acousticness' : [],
        'danceability' : [],
        'duration_ms' : [],
        'energy' : [],
        'instrumentalness' : [],
        'liveness' : [],
        'loudness' : [],
        'speechiness' : [],
        'tempo' : [],
        'valence' : [],
        'ai' : []
    }
    # populating song_stats arrays with song stats.
    each_song_stats = {}

    # WATSON ai found songs
    watson_arr = []
    
    # iterate through each sonf in group ----> (group is a list)
    for song in group :
        name = song['name']
        song_id = song['id']
        # Song == a specific song's clean data //phase 0
        song = _song_analysis_details(token, song_id , False ,  name , song['artists'][0] )
        # append data to keys of 
        for x in song_stats.keys():
            song_stats[x].append(song[x])
       

        # ADD FINAL SONG PRODUCT as a key in each_song_stats
        each_song_stats[name] = song

        # check if watson ai
        if song['ai']['nlu'] is not None:
            print("☁")
            watson_arr.append(  ( song['song_title'] , song['artist_name'] )    )


 
 
    #    DEBUG
        # each_song_stats[song_id] = song
        # print(each_song_stats[name]['id'])




    # ****************
    # AT THIS POINT song_stats is a dictionary that holds arrays populated with all the user's liked music
    # this is to analyse the average of the whole playlist
    # ****************



    # averaging spotify (turning each key into it's average)
    spotty_keys = list(song_stats.keys())[:-1]  #every key except ["ai"]
    for x in spotty_keys:
        song_stats[x] =  statistics.mean(song_stats[x])




    # averaging watson    ["ai"]
    #  -------  watson  OUTPUT VARIABLES    -------
    group_merge_ai = {}

    # CHECKING FOR PROPER nlu DICTIONARY && creating merged dict...
    solid_nlu = False
    for x in range(len(song_stats['ai'])):
        if song_stats['ai'][x]['nlu'] :
            solid_nlu = True
            good_dict = x
            break
    if solid_nlu:
        for key in song_stats['ai'][x]['nlu']:
            if key =='averageEmotion':
                group_merge_ai[key] = []
                continue
            group_merge_ai[key] = {}
            for inner_keys in song_stats['ai'][x]['nlu'][key]:
                group_merge_ai[key][inner_keys] = []
    else: #IMPORTANT CATCH IF NO AI
        song_stats['ai'] = None

        return song_stats , each_song_stats

    #    NLU IS EACH ITEM IN THE SONG_STATS['ai']  ---> which needs to become a grouped dict of lists avg!!!!!


    # iterate through every SONG TEXT and grab nlu
    # merge all values in NLU into group_merge_ai
    for x in range( 0 ,   len(song_stats['ai'])   ,   1  ):
        NLU = song_stats['ai'][x]['nlu']

        if NLU is not None :
            # append all group emotions ------> EMOTIONS
            group_merge_ai['averageEmotion'].append(NLU['averageEmotion'])

            # create dict keys for all concept frequencies  ------> CONCEPTS
            singularities = []
            for i in NLU['conceptfrequencies']:
                # Singular keys found with empty arr
                if len( NLU['conceptfrequencies'][i] ) < 1:
                    # print("DEBUG: singularity:   ", i)
                    singularities.append(i)
                    continue
                # if there the key already exists!
                if i in group_merge_ai['conceptfrequencies']:
                    # ITERATE THROUGH NLU['conceptfrequencies'][i]
                    for concept in NLU['conceptfrequencies'][i]:
                        if isinstance(concept, str):
                            group_merge_ai['conceptfrequencies'][i].append(concept)
                        elif isinstance(concept, list):
                            for inner_concept in concept:
                                group_merge_ai['conceptfrequencies'][i].append(inner_concept)
                else:
                    # if the concept is not in the dictionary as a key... add it with it's coentents as well
                    # print(NLU['conceptfrequencies'][i] )
                    group_merge_ai['conceptfrequencies'][i] = []
                    for concept in NLU['conceptfrequencies'][i]:
                        if isinstance(concept, str):
                            group_merge_ai['conceptfrequencies'][i].append(concept)
                        elif isinstance(concept, list):
                            for inner_concept in concept:
                                group_merge_ai['conceptfrequencies'][i].append(inner_concept)
            NLU['conceptfrequencies']['singularities'] = singularities


            # goes through dictionary and populates the merge
            for key in NLU.keys():
                if key == "averageEmotion" or  key == "conceptfrequencies":
                    continue
                for i in NLU[key]:
                    if isinstance(NLU[key][i], int):
                        if  i  in group_merge_ai[key]:
                            if isinstance(group_merge_ai[key][i], list):
                                group_merge_ai[key][i] = 1
                            else:
                                group_merge_ai[key][i] +=  NLU[key][i]
                        else:
                             group_merge_ai[key][i] = NLU[key][i]
                    else:
                        # print( group_merge_ai[key][i]  ) #/// VARIALE IN QUESION!
                        if i  in group_merge_ai[key]:
                            group_merge_ai[key][i].extend(  NLU[key][i]    )
                        else:
                            group_merge_ai[key][i] = NLU[key][i]






    # Average all emotions in array
    # OVER ALL EMOTION AVERAGE
    temp = {
        "Anger": [],
        "Disgust": [],
        "Fear": [],
        "Joy": [],
        "Sadness": []
      }
    for x in  range( 0 , len(group_merge_ai['averageEmotion'])  ,   1 ):
        for key in group_merge_ai['averageEmotion'][x]:
            temp[key].append(group_merge_ai['averageEmotion'][x][key])
    # replace vars 
    for emotion in temp:
        temp[emotion] = statistics.mean(temp[emotion])




    # LISTS BECOMES MERGED DICTIONARIES
    group_merge_ai['amount'] = len(group_merge_ai['averageEmotion']) #FIND AMOUNT OF ANALYZED SONGS  
    group_merge_ai['averageEmotion'] = temp
    song_stats['ai'] = group_merge_ai

    
    
    # remember watson_arr?
    song_stats['ai']['watson_songs'] = watson_arr
    
    return song_stats , each_song_stats



# helper functions
def fetch_meme(username):
    try:
        # Check if we have imgflip credentials
        if not imgflip_username or not imgflip_password:
            print("WARNING: Imgflip credentials not found. Using local fallback image.")
            return {'data': {'url': '/static/fallback.svg'}}
        
        # Collection of funny code and music-related meme texts
        meme_texts = [
            # Code-related memes
            (f"{username} thinks", "they're a data scientist..."),
            (f"{username} when", "the code finally compiles"),
            (f"{username} debugging", "at 3 AM"),
            (f"{username} trying to", "understand their own code"),
            (f"{username} after", "fixing one bug"),
            (f"{username} when", "git merge works"),
            (f"{username} coding", "without Stack Overflow"),
            (f"{username} explaining", "their code to others"),
            (f"{username} trying to", "deploy to production"),
            (f"{username} when", "the tests pass"),
            
            # Music-related memes
            (f"{username} listening to", "their own playlist"),
            (f"{username} when", "their favorite song comes on"),
            (f"{username} trying to", "find the perfect song"),
            (f"{username} analyzing", "music like a pro"),
            (f"{username} discovering", "new music"),
            (f"{username} when", "Spotify recommends hits"),
            (f"{username} explaining", "music theory"),
            (f"{username} trying to", "match the beat"),
            (f"{username} when", "the bass drops"),
            (f"{username} analyzing", "song emotions"),
            
            # Code + Music crossover memes
            (f"{username} coding", "to music"),
            (f"{username} when", "music helps debug"),
            (f"{username} trying to", "code and listen"),
            (f"{username} explaining", "code with music analogies"),
            (f"{username} debugging", "with headphones on"),
            (f"{username} when", "music inspires code"),
            (f"{username} coding", "like a DJ"),
            (f"{username} trying to", "sync code and music"),
            (f"{username} when", "the algorithm grooves"),
            (f"{username} analyzing", "code like a song")
        ]
        
        # Randomly select a meme text combination
        text0, text1 = random.choice(meme_texts)

        # fetch all memes
        response = requests.get('https://api.imgflip.com/get_memes')
        response.raise_for_status()
        data = response.json()
        
        if 'data' not in data or 'memes' not in data['data']:
            print("ERROR: Invalid response from imgflip API")
            return {'data': {'url': '/static/fallback.svg'}}
        
        memes = data['data']['memes']
        # List top memes with 2 text slots
        images = [{'name': image['name'], 'url': image['url'], 'id': image['id']} 
                 for image in memes if image['box_count'] == 2]
        
        if not images:
            print("ERROR: No 2-text memes available")
            return {'data': {'url': '/static/fallback.svg'}}
        
        # Take random meme from available ones
        meme = random.choice(images)
        
        # Generate meme with proper authentication
        URL = 'https://api.imgflip.com/caption_image'
        params = {
            'username': imgflip_username,
            'password': imgflip_password,
            'template_id': meme['id'],
            'text0': text0,
            'text1': text1
        }
        
        meme_response = requests.post(URL, data=params)
        meme_response.raise_for_status()
        result = meme_response.json()
        
        if 'success' in result and result['success'] and 'data' in result:
            print(f"SUCCESS: Generated meme with template '{meme['name']}' and text: '{text0}' / '{text1}'")
            return result
        else:
            error_msg = result.get('error_message', 'Unknown error')
            print(f"ERROR: Failed to generate meme: {error_msg}")
            return {'data': {'url': '/static/fallback.svg'}}
            
    except Exception as e:
        print(f"ERROR: fetch_meme failed: {e}")
        return {'data': {'url': '/static/fallback.svg'}}




application.run(host = '0.0.0.0' , port = 8080)
# application.run( port = 8080)


