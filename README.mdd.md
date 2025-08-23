I'll search through your repository to find all the secrets and API keys that need to be added to GitHub Actions secrets.


[6 tools called]

Based on my analysis of your repository, here are **ALL the secrets you need to add to GitHub Actions**:

## 🔐 Required GitHub Actions Secrets

### 1. **Azure Infrastructure Secrets** (for Terraform deployment)
- `AZURE_CREDENTIALS` - Service principal JSON for Azure access
- `AZURE_SUBSCRIPTION_ID` - Your Azure subscription ID

### 2. **Spotify API Secrets** (for music authentication)
- `SPOTIFY_CLIENT_ID` - Your Spotify app client ID
- `SPOTIFY_CLIENT_SECRET` - Your Spotify app client secret
- `SPOTIFY_CALLBACK_URL` - Your Spotify OAuth redirect URI

### 3. **Genius API Secrets** (for lyrics data)
- `GENIUS_CLIENT_ID` - Your Genius app client ID  
- `GENIUS_CLIENT_SECRET` - Your Genius app client secret
- `GENIUS_CALLBACK_URL` - Your Genius OAuth redirect URI

### 4. **IBM Watson Secrets** (for AI text analysis)
- `WATSON_API_KEY` - Your IBM Watson NLU API key
- `WATSON_SERVICE_URL` - Your IBM Watson service URL

### 5. **Flask App Secret**
- `FLASK_SECRET_KEY` - Secret key for Flask sessions

## 📝 How to Set These Up

### **Spotify Setup:**
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Get Client ID and Client Secret
4. Add redirect URI (e.g., `https://yourdomain.com/login/`)

### **Genius Setup:**
1. Go to [Genius API](https://genius.com/api-clients)
2. Create a new API client
3. Get Client ID and Client Secret
4. Add redirect URI

### **IBM Watson Setup:**
1. Go to [IBM Cloud](https://cloud.ibm.com/catalog/services/natural-language-understanding)
2. Create NLU service
3. Get API key and service URL

## 🚀 Updated GitHub Workflow

You'll need to update your workflow to use these secrets. Here's what needs to be added to your `.github/workflows/simple-deploy.yml`:

```yaml
env:
  SPOTIFY_CLIENT_ID: ${{ secrets.SPOTIFY_CLIENT_ID }}
  SPOTIFY_CLIENT_SECRET: ${{ secrets.SPOTIFY_CLIENT_SECRET }}
  GENIUS_CLIENT_ID: ${{ secrets.GENIUS_CLIENT_ID }}
  GENIUS_CLIENT_SECRET: ${{ secrets.GENIUS_CLIENT_SECRET }}
  WATSON_API_KEY: ${{ secrets.WATSON_API_KEY }}
  WATSON_SERVICE_URL: ${{ secrets.WATSON_SERVICE_URL }}
  FLASK_SECRET_KEY: ${{ secrets.FLASK_SECRET_KEY }}
```

## ⚠️ Security Notes

- **Never commit these values** to your repository
- Use GitHub's encrypted secrets feature
- Rotate secrets regularly
- Consider using Azure Key Vault for production

Would you like me to help you update the workflow file to properly use these secrets, or help you set up any of these API services?