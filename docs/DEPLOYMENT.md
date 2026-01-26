# Deployment Guide

This guide walks through deploying Enterprise AI Search to production on Azure.

## Prerequisites

- Azure subscription
- Azure CLI installed and configured
- Python 3.8+
- Git

## Quick Deploy to Azure

### Option 1: Azure App Service (Recommended for small-medium workloads)

#### 1. Create Azure Resources

```bash
# Set variables
RESOURCE_GROUP="rg-enterprise-search"
LOCATION="eastus"
APP_NAME="enterprise-search-app"
SEARCH_SERVICE="search-$(openssl rand -hex 4)"
OPENAI_SERVICE="openai-$(openssl rand -hex 4)"

# Login to Azure
az login

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Cognitive Search
az search service create \
    --name $SEARCH_SERVICE \
    --resource-group $RESOURCE_GROUP \
    --sku standard \
    --location $LOCATION

# Get Search credentials
SEARCH_ENDPOINT=$(az search service show \
    --name $SEARCH_SERVICE \
    --resource-group $RESOURCE_GROUP \
    --query "endpoint" -o tsv)

SEARCH_KEY=$(az search admin-key show \
    --service-name $SEARCH_SERVICE \
    --resource-group $RESOURCE_GROUP \
    --query "primaryKey" -o tsv)

# Create Azure OpenAI
az cognitiveservices account create \
    --name $OPENAI_SERVICE \
    --resource-group $RESOURCE_GROUP \
    --kind OpenAI \
    --sku S0 \
    --location $LOCATION

# Get OpenAI credentials
OPENAI_ENDPOINT=$(az cognitiveservices account show \
    --name $OPENAI_SERVICE \
    --resource-group $RESOURCE_GROUP \
    --query "properties.endpoint" -o tsv)

OPENAI_KEY=$(az cognitiveservices account keys list \
    --name $OPENAI_SERVICE \
    --resource-group $RESOURCE_GROUP \
    --query "key1" -o tsv)

az cognitiveservices account deployment create \
# Deploy models (update names/versions to match your deployments)
az cognitiveservices account deployment create \
    --name $OPENAI_SERVICE \
    --resource-group $RESOURCE_GROUP \
    --deployment-name text-embedding-3-small \
    --model-name text-embedding-3-small \
    --model-version "1" \
    --model-format OpenAI \
    --scale-settings-scale-type "Standard"

az cognitiveservices account deployment create \
    --name $OPENAI_SERVICE \
    --resource-group $RESOURCE_GROUP \
    --deployment-name chat-gpt-4o-mini \
    --model-name gpt-4o-mini \
    --model-version "1" \
    --model-format OpenAI \
    --scale-settings-scale-type "Standard"
```

#### 2. Deploy Application

```bash
# Create App Service Plan
az appservice plan create \
    --name "${APP_NAME}-plan" \
    --resource-group $RESOURCE_GROUP \
    --sku B1 \
    --is-linux

# Create Web App
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan "${APP_NAME}-plan" \
    --runtime "PYTHON:3.11"

# Configure environment variables
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        SEARCH_ENDPOINT="$SEARCH_ENDPOINT" \
        SEARCH_KEY="$SEARCH_KEY" \
        INDEX_NAME="docs-index" \
        OPENAI_ENDPOINT="$OPENAI_ENDPOINT" \
        OPENAI_KEY="$OPENAI_KEY" \
        EMBEDDING_MODEL="text-embedding-3-small" \
        CHAT_MODEL="chat-gpt-4o-mini"

# Deploy code
cd /path/to/enterprise-ai-search
zip -r deploy.zip . -x "*.git*" "*.venv*" "__pycache__*" "data/documents/*"

az webapp deployment source config-zip \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --src deploy.zip
```

### Option 2: Azure Container Instances

```bash
# Build and push Docker image
ACR_NAME="acrenterpriseai$(openssl rand -hex 4)"

# Create Azure Container Registry
az acr create \
    --name $ACR_NAME \
    --resource-group $RESOURCE_GROUP \
    --sku Basic \
    --location $LOCATION

# Login to ACR
az acr login --name $ACR_NAME

# Build and push image
docker build -t enterprise-ai-search:latest .
docker tag enterprise-ai-search:latest ${ACR_NAME}.azurecr.io/enterprise-ai-search:latest
docker push ${ACR_NAME}.azurecr.io/enterprise-ai-search:latest

# Create Container Instance
az container create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image ${ACR_NAME}.azurecr.io/enterprise-ai-search:latest \
    --registry-login-server ${ACR_NAME}.azurecr.io \
    --registry-username $(az acr credential show --name $ACR_NAME --query "username" -o tsv) \
    --registry-password $(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv) \
    --environment-variables \
        SEARCH_ENDPOINT="$SEARCH_ENDPOINT" \
        SEARCH_KEY="$SEARCH_KEY" \
        INDEX_NAME="docs-index" \
        OPENAI_ENDPOINT="$OPENAI_ENDPOINT" \
        OPENAI_KEY="$OPENAI_KEY" \
        EMBEDDING_MODEL="text-embedding-3-small" \
        CHAT_MODEL="chat-gpt-4o-mini" \
    --cpu 1 \
    --memory 1.5 \
    --restart-policy OnFailure
```

### Option 3: Azure Kubernetes Service (For large-scale production)

```bash
# Create AKS cluster
AKS_NAME="aks-enterprise-search"

az aks create \
    --name $AKS_NAME \
    --resource-group $RESOURCE_GROUP \
    --node-count 2 \
    --node-vm-size Standard_D2s_v3 \
    --generate-ssh-keys \
    --attach-acr $ACR_NAME

# Get credentials
az aks get-credentials \
    --name $AKS_NAME \
    --resource-group $RESOURCE_GROUP

# Create Kubernetes secrets
kubectl create secret generic enterprise-search-secrets \
    --from-literal=SEARCH_ENDPOINT="$SEARCH_ENDPOINT" \
    --from-literal=SEARCH_KEY="$SEARCH_KEY" \
    --from-literal=INDEX_NAME="docs-index" \
    --from-literal=OPENAI_ENDPOINT="$OPENAI_ENDPOINT" \
    --from-literal=OPENAI_KEY="$OPENAI_KEY" \
    --from-literal=EMBEDDING_MODEL="text-embedding-3-small" \
    --from-literal=CHAT_MODEL="chat-gpt-4o-mini"

# Apply deployment (see k8s/deployment.yaml)
kubectl apply -f k8s/
```

## Production Configuration

### 1. Use Azure Key Vault

```bash
# Create Key Vault
KEYVAULT_NAME="kv-enterprise-$(openssl rand -hex 4)"

az keyvault create \
    --name $KEYVAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Store secrets
az keyvault secret set --vault-name $KEYVAULT_NAME --name "SearchKey" --value "$SEARCH_KEY"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "OpenAIKey" --value "$OPENAI_KEY"

# Enable Managed Identity for your app
az webapp identity assign \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP

# Grant access to Key Vault
PRINCIPAL_ID=$(az webapp identity show --name $APP_NAME --resource-group $RESOURCE_GROUP --query principalId -o tsv)

az keyvault set-policy \
    --name $KEYVAULT_NAME \
    --object-id $PRINCIPAL_ID \
    --secret-permissions get list
```

Update [src/config.py](src/config.py) to use Key Vault:

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url=f"https://{KEYVAULT_NAME}.vault.azure.net/", credential=credential)

SEARCH_KEY = client.get_secret("SearchKey").value
OPENAI_KEY = client.get_secret("OpenAIKey").value
```

### 2. Enable Private Endpoints

```bash
# Create VNet
az network vnet create \
    --name vnet-enterprise-search \
    --resource-group $RESOURCE_GROUP \
    --address-prefix 10.0.0.0/16 \
    --subnet-name subnet-app \
    --subnet-prefix 10.0.1.0/24

# Create private endpoints for Search and OpenAI
# (See Azure documentation for detailed steps)
```

### 3. Configure Monitoring

```bash
# Create Application Insights
APP_INSIGHTS_NAME="appi-enterprise-search"

az monitor app-insights component create \
    --app $APP_INSIGHTS_NAME \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
    --app $APP_INSIGHTS_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "instrumentationKey" -o tsv)

# Add to app settings
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings APPINSIGHTS_INSTRUMENTATION_KEY="$INSTRUMENTATION_KEY"
```

### 4. Set Up CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy to Azure

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Login to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Build and push Docker image
      run: |
        az acr build \
          --registry ${{ secrets.ACR_NAME }} \
          --image enterprise-ai-search:${{ github.sha }} \
          --image enterprise-ai-search:latest \
          .
    
    - name: Deploy to Azure Container Instances
      run: |
        az container create \
          --name enterprise-search-app \
          --resource-group ${{ secrets.RESOURCE_GROUP }} \
          --image ${{ secrets.ACR_NAME }}.azurecr.io/enterprise-ai-search:${{ github.sha }} \
          --registry-login-server ${{ secrets.ACR_NAME }}.azurecr.io \
          --registry-username ${{ secrets.ACR_USERNAME }} \
          --registry-password ${{ secrets.ACR_PASSWORD }} \
          --environment-variables-file .env.production
```

## Post-Deployment

### 1. Run Initial Ingestion

```bash
# Connect to your deployment
az container exec \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --exec-command "python src/ingest.py"

# Or for App Service
az webapp ssh --name $APP_NAME --resource-group $RESOURCE_GROUP
python src/ingest.py
```

### 2. Test the Deployment

```bash
# Get app URL
APP_URL=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "defaultHostName" -o tsv)

# Test query endpoint (if you've added an API)
curl https://${APP_URL}/api/query \
    -H "Content-Type: application/json" \
    -d '{"query": "test question"}'
```

### 3. Monitor Performance

```bash
# View logs
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP

# Check metrics
az monitor metrics list \
    --resource-group $RESOURCE_GROUP \
    --resource $APP_NAME \
    --resource-type "Microsoft.Web/sites" \
    --metric "Requests"
```

## Scaling Recommendations

### Small (< 1K documents, < 100 queries/day)
- Azure Search: Basic tier
- App Service: B1
- OpenAI: Standard (10K TPM)

### Medium (1K-100K documents, 100-1K queries/day)
- Azure Search: Standard S1
- App Service: S1 (or Container Instances)
- OpenAI: Standard (100K TPM)

### Large (100K+ documents, 1K+ queries/day)
- Azure Search: Standard S2+ with partitions
- AKS with auto-scaling
- OpenAI: Provisioned throughput

## Cost Estimation

### Monthly costs (approximate):

**Small**:
- Azure Search (Basic): $75
- App Service (B1): $13
- Azure OpenAI: ~$50-100 (usage-based)
- **Total: ~$140-190/month**

**Medium**:
- Azure Search (S1): $250
- App Service (S1): $70
- Azure OpenAI: ~$200-500
- **Total: ~$520-820/month**

**Large**:
- Azure Search (S2): $1,000
- AKS: $200-500
- Azure OpenAI (Provisioned): $1,000+
- **Total: ~$2,200+/month**

## Troubleshooting

### Issue: Deployment fails
```bash
# Check deployment logs
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP

# Verify environment variables
az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP
```

### Issue: Out of memory
- Increase App Service plan size
- Optimize batch size in ingestion
- Use streaming for large documents

### Issue: Slow queries
- Upgrade Azure Search tier
- Optimize HNSW parameters
- Implement caching layer

## Cleanup

```bash
# Delete all resources
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

## Support

For deployment issues:
- Azure Support: https://azure.microsoft.com/support
- Project Issues: https://github.com/najeebpk-dev/enterprise-ai-search/issues (update 'najeebpk-dev')
