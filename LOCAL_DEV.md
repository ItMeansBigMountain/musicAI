# Local Development Setup

## Quick Start

1. **Copy environment template:**
   ```bash
   cp env.template .env
   ```

2. **Fill in your API keys in `.env`:**
   - Get Spotify credentials from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Get Genius credentials from [Genius API](https://genius.com/api-clients)
   - Get Watson credentials from [IBM Cloud](https://cloud.ibm.com/catalog/services/natural-language-understanding)

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run locally:**
   ```bash
   python musicAI.py
   ```

5. **Visit:** `http://localhost:5000`

## Environment Variables

### Required for Local Development
- `SPOTIFY_CLIENT_ID` - Your Spotify app client ID
- `SPOTIFY_CLIENT_SECRET` - Your Spotify app client secret
- `SPOTIFY_CALLBACK_URL` - Must be `http://localhost:5000/login/`
- `GENIUS_CLIENT_ID` - Your Genius app client ID
- `GENIUS_CLIENT_SECRET` - Your Genius app client secret
- `GENIUS_CALLBACK_URL` - Must be `http://localhost:5000/gen_login/`
- `WATSON_API_KEY` - Your IBM Watson NLU API key
- `WATSON_SERVICE_URL` - Your IBM Watson service URL

### Optional (with defaults)
- `FLASK_SECRET_KEY` - Random string for sessions (default: auto-generated)
- `FLASK_DEBUG` - Set to `true` for development (default: `false`)
- `FLASK_ENV` - Environment name (default: `development`)

## Testing OAuth

1. **Spotify OAuth:**
   - Visit `/login/` endpoint
   - Redirects to Spotify for authorization
   - Returns to your callback URL with code
   - App exchanges code for access token

2. **Genius OAuth:**
   - Visit `/gen_login/` endpoint
   - Similar flow to Spotify
   - Stores token in session

## CORS Issues Fixed

The previous CORS errors were caused by:
- Including `client_secret` in the authorization URL (should only be in token exchange)
- Improper error handling in the OAuth flow

**Fixed in this update:**
- ✅ Removed `client_secret` from authorization URL
- ✅ Added proper error handling
- ✅ Better debugging and logging
- ✅ Cleaner OAuth flow

## Troubleshooting

### Common Issues:
- **"Invalid redirect URI"** - Make sure callback URLs match exactly in your API app settings
- **"Missing client_id"** - Check your `.env` file has all required variables
- **"Import errors"** - Run `pip install -r requirements.txt`
- **"CORS errors"** - These should now be resolved with the updated OAuth flow

### Debug Mode:
Set `FLASK_DEBUG=true` in your `.env` for detailed error messages and auto-reload.

## Production vs Development

- **Development:** Uses `.env` file, debug mode, localhost callbacks
- **Production:** Uses GitHub secrets, no debug, production callbacks
- **CI/CD:** Automatically uses production environment variables
