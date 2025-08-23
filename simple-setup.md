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

Add these secrets:
- `AZURE_CREDENTIALS` - the JSON from step 1
- `AZURE_SUBSCRIPTION_ID` - your subscription ID (get with `az account show --query id -o tsv`)

## 3. First Deploy

```bash
# Push to main branch
git add .
git commit -m "Add simple API with Terraform"
git push origin main
```

The workflow will:
1. Build your Docker image
2. Push to ACR
3. Run `terraform init/plan/apply`
4. Deploy container app
5. Output the FQDN

## 4. Test Your Endpoint

The workflow outputs the FQDN. Visit:
- `https://your-fqdn/` - returns service info
- `https://your-fqdn/health` - returns health status

## What You Get

- ✅ Basic endpoint running
- ✅ Auto-deploy on push
- ✅ Simple container app
- ✅ Terraform-managed infrastructure
- ✅ Dedicated resource group: `musicai-rg`
- ✅ Easy to destroy/recreate
- ❌ No production hardening
- ❌ No secrets management
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
