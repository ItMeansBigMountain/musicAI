# 🎵 MusicAI Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Copy the template and fill in your API keys:
```bash
cp env.template .env
```

Edit `.env` with your actual API credentials:
```env
# Spotify API
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_CALLBACK_URL=http://localhost:8080/login/

# Genius API  
GENIUS_CLIENT_ID=your_genius_client_id
GENIUS_CLIENT_SECRET=your_genius_client_secret
GENIUS_CALLBACK_URL=http://localhost:8080/gen_login/

# IBM Watson NLU
WATSON_API_KEY=your_watson_api_key
WATSON_SERVICE_URL=your_watson_service_url

# Flask App
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=true

# Imgflip API (optional - for meme generation)
IMGFLIP_USERNAME=your_imgflip_username
IMGFLIP_PASSWORD=your_imgflip_password
```

### 3. Test the App
```bash
python test_app.py
```

### 4. Run the App
```bash
python musicAI.py
```

The app will be available at: http://localhost:8080

## 🔑 Getting API Keys

### Spotify
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Get Client ID and Client Secret
4. Add redirect URI: `http://localhost:8080/login/`

### Genius
1. Go to [Genius API](https://genius.com/api-clients)
2. Create a new API client
3. Get your API key (Client Access Token)
4. Add to your `.env` file (no redirect URI needed)

### IBM Watson
1. Go to [IBM Cloud](https://cloud.ibm.com/catalog/services/natural-language-understanding)
2. Create NLU service
3. Get API key and service URL

### Imgflip (for meme generation)
1. Go to [imgflip.com](https://imgflip.com)
2. Create a free account
3. Get your username and password
4. Add to your `.env` file (optional but recommended)

## 🚀 Features

- **Individual Song Analysis**: Analyze single tracks for audio features and lyrical sentiment
- **Bulk Music Analysis**: Process entire albums, playlists, or liked songs collections
- **AI-Powered Insights**: Uses Watson NLU to analyze song lyrics for emotions and concepts
- **Spotify Integration**: Fetches user's music library and audio features
- **Lyrics Analysis**: Scrapes lyrics from Genius and analyzes them with AI

## 🐛 Troubleshooting

### Common Issues

1. **"Missing environment variables"**
   - Check your `.env` file exists and has all required variables
   - Ensure no spaces around `=` signs

2. **"Spotify token expired"**
   - Re-authenticate with Spotify
   - Check your callback URLs match exactly

3. **"Failed to analyze song"**
   - Verify your Watson API key is valid
   - Check if the song has lyrics available on Genius

4. **App won't start**
   - Run `python test_app.py` to check for issues
   - Ensure all dependencies are installed

### Getting Help

- Check the console output for error messages
- Verify all API keys are correct
- Ensure your redirect URIs match exactly what's configured in the APIs

## 📱 Usage

1. **Login**: Authenticate with Spotify only (Genius API key is handled automatically)
2. **Search**: Look up songs or artists
3. **Analyze**: Get detailed analysis including:
   - Audio features (danceability, energy, etc.)
   - Emotional analysis of lyrics
   - Concept extraction
   - Sentiment analysis
4. **Explore**: Analyze your playlists, albums, and liked songs

## 🔧 Development

- **Debug Mode**: Set `FLASK_DEBUG=true` in `.env`
- **Port**: Change port in `musicAI.py` (default: 8080)
- **Database**: Song analysis results are cached in `song_db.json`
- **Token Management**: Use `python manage_tokens.py` to view/clear stored authentication tokens

## 🔐 Token Management

### Automatic Token Storage
- Spotify tokens are automatically stored locally in `user_tokens.json`
- Tokens are refreshed automatically when expired
- No need to re-authenticate every time you use the app

### Managing Tokens
```bash
# View all stored tokens
python manage_tokens.py

# Clear specific user tokens
python manage_tokens.py

# Clear all tokens (forces re-authentication)
python manage_tokens.py
```
