# Quick Setup with Terraform - Just Get It Running

## 1. Create Service Principal (one-time setup)

```bash
# Login to Azure
az login

# Create service principal
az ad sp create-for-rbac --name "musicai-sp" --role contributor --scopes /subscriptions/$(az account show --query id -o tsv)

# Save the output JSON - you'll need this for GitHub secrets
```

## 2. Set GitHub Secrets

Go to your repo → Settings → Secrets and variables → Actions

### Azure Infrastructure Secrets:
- `AZURE_CREDENTIALS` - the JSON from step 1
- `AZURE_SUBSCRIPTION_ID` - your subscription ID (get with `az account show --query id -o tsv`)
- `AZURE_TENANT_ID` - your tenant ID
- `AZURE_CLIENT_ID` - client ID from service principal
- `AZURE_CLIENT_SECRET` - client secret from service principal

### API Service Secrets:
- `SPOTIFY_CLIENT_ID` - your Spotify app client ID
- `SPOTIFY_CLIENT_SECRET` - your Spotify app client secret
- `SPOTIFY_CALLBACK_URL` - your production callback URL
- `GENIUS_CLIENT_ID` - your Genius app client ID
- `GENIUS_CLIENT_SECRET` - your Genius app client secret
- `GENIUS_CALLBACK_URL` - your production callback URL
- `WATSON_API_KEY` - your IBM Watson NLU API key
- `WATSON_SERVICE_URL` - your IBM Watson service URL

### App Secrets:
- `FLASK_SECRET_KEY` - random string for Flask sessions

## 3. Local Development

```bash
# Copy environment template
cp env.template .env

# Fill in your API keys in .env file
# See LOCAL_DEV.md for detailed instructions

# Test locally
python musicAI.py
```

## 4. First Deploy

```bash
# Push to main branch
git add .
git commit -m "Add environment variable support"
git push origin main
```

The workflow will:
1. Build your Docker image
2. Push to ACR
3. Run `terraform init/plan/apply`
4. Deploy container app with all environment variables
5. Output the FQDN

## 5. Test Your Endpoint

The workflow outputs the FQDN. Visit:
- `https://your-fqdn/` - returns service info
- `https://your-fqdn/health` - returns health status

## What You Get

- ✅ Basic endpoint running
- ✅ Auto-deploy on push
- ✅ Simple container app
- ✅ Terraform-managed infrastructure
- ✅ Dedicated resource group: `musicai-rg`
- ✅ Environment variables for all APIs
- ✅ Easy local development with `.env`
- ✅ Easy to destroy/recreate
- ❌ No production hardening
- ❌ No monitoring

## Local Terraform (Optional)

```bash
cd infra/terraform

# Login to Azure
az login

# Initialize
terraform init

# Plan
terraform plan -var="subscription_id=YOUR_SUBSCRIPTION_ID"

# Apply
terraform apply -var="subscription_id=YOUR_SUBSCRIPTION_ID"

# Destroy when done
terraform destroy -var="subscription_id=YOUR_SUBSCRIPTION_ID"
```

## Clean Up

```bash
cd infra/terraform
terraform destroy -var="subscription_id=YOUR_SUBSCRIPTION_ID"
```

Or just delete the resource group:
```bash
az group delete --name musicai-rg --yes
```
