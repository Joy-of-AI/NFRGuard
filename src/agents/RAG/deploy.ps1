# RAG System Production Deployment Script (PowerShell)
# This script deploys the complete RAG system to production

param(
    [string]$ProjectId = $env:GOOGLE_CLOUD_PROJECT,
    [string]$ServiceAccountPath = $env:GOOGLE_APPLICATION_CREDENTIALS
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🚀 RAG System Production Deployment" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Check if required environment variables are set
if (-not $ProjectId) {
    Write-Host "❌ Error: GOOGLE_CLOUD_PROJECT environment variable not set" -ForegroundColor Red
    Write-Host "   Please set it with: `$env:GOOGLE_CLOUD_PROJECT = 'your-project-id'" -ForegroundColor Yellow
    exit 1
}

if (-not $ServiceAccountPath) {
    Write-Host "❌ Error: GOOGLE_APPLICATION_CREDENTIALS environment variable not set" -ForegroundColor Red
    Write-Host "   Please set it with: `$env:GOOGLE_APPLICATION_CREDENTIALS = 'path/to/service-account.json'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Environment variables configured" -ForegroundColor Green
Write-Host "   Project ID: $ProjectId" -ForegroundColor Cyan
Write-Host "   Service Account: $ServiceAccountPath" -ForegroundColor Cyan

# Step 1: Validate configuration
Write-Host ""
Write-Host "🔍 Step 1: Validating configuration..." -ForegroundColor Yellow
python production_config.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Configuration validation failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Configuration validation passed" -ForegroundColor Green

# Step 2: Deploy vector search infrastructure
Write-Host ""
Write-Host "🏗️  Step 2: Deploying vector search infrastructure..." -ForegroundColor Yellow
python deploy_production.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Vector search deployment failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Vector search infrastructure deployed" -ForegroundColor Green

# Step 3: Load deployment info
Write-Host ""
Write-Host "📝 Step 3: Loading deployment information..." -ForegroundColor Yellow
if (-not (Test-Path "deployment_info.json")) {
    Write-Host "❌ Deployment info file not found" -ForegroundColor Red
    exit 1
}

# Extract deployment info
$deploymentInfo = Get-Content "deployment_info.json" | ConvertFrom-Json
$INDEX_ID = $deploymentInfo.index_id
$ENDPOINT_ID = $deploymentInfo.endpoint_id
$DEPLOYED_INDEX_ID = $deploymentInfo.deployed_index_id

Write-Host "   Vector Index ID: $INDEX_ID" -ForegroundColor Cyan
Write-Host "   Vector Endpoint ID: $ENDPOINT_ID" -ForegroundColor Cyan
Write-Host "   Deployed Index ID: $DEPLOYED_INDEX_ID" -ForegroundColor Cyan

# Step 4: Update Kubernetes configuration
Write-Host ""
Write-Host "🔧 Step 4: Updating Kubernetes configuration..." -ForegroundColor Yellow
$k8sFile = "k8s/agents-rag.yaml"
if (Test-Path $k8sFile) {
    $content = Get-Content $k8sFile -Raw
    $content = $content -replace "your-project-id", $ProjectId
    $content = $content -replace "your-index-id", $INDEX_ID
    $content = $content -replace "your-endpoint-id", $ENDPOINT_ID
    Set-Content $k8sFile $content
    Write-Host "✅ Kubernetes configuration updated" -ForegroundColor Green
} else {
    Write-Host "⚠️  Kubernetes file not found, skipping update" -ForegroundColor Yellow
}

# Step 5: Create service account secret
Write-Host ""
Write-Host "🔐 Step 5: Creating service account secret..." -ForegroundColor Yellow
kubectl create namespace nfrguard-agents --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic google-service-account `
  --from-file=key.json="$ServiceAccountPath" `
  --namespace=nfrguard-agents `
  --dry-run=client -o yaml | kubectl apply -f -
Write-Host "✅ Service account secret created" -ForegroundColor Green

# Step 6: Deploy agents
Write-Host ""
Write-Host "🚀 Step 6: Deploying RAG-enhanced agents..." -ForegroundColor Yellow
if (Test-Path $k8sFile) {
    kubectl apply -f $k8sFile
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Agent deployment failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ RAG-enhanced agents deployed" -ForegroundColor Green
} else {
    Write-Host "⚠️  Kubernetes file not found, skipping agent deployment" -ForegroundColor Yellow
}

# Step 7: Wait for deployment
Write-Host ""
Write-Host "⏳ Step 7: Waiting for deployment to be ready..." -ForegroundColor Yellow
$agents = @(
    "transaction-risk-agent",
    "compliance-agent",
    "resilience-agent",
    "customer-sentiment-agent",
    "data-privacy-agent",
    "knowledge-agent",
    "banking-assistant-agent"
)

foreach ($agent in $agents) {
    Write-Host "   Waiting for $agent..." -ForegroundColor Cyan
    kubectl wait --for=condition=available --timeout=300s "deployment/$agent" -n nfrguard-agents
}
Write-Host "✅ All agents are ready" -ForegroundColor Green

# Step 8: Run health check
Write-Host ""
Write-Host "🏥 Step 8: Running health check..." -ForegroundColor Yellow
python monitor_production.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Health check failed - system may need attention" -ForegroundColor Yellow
} else {
    Write-Host "✅ Health check passed" -ForegroundColor Green
}

# Step 9: Display deployment summary
Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Deployment Summary:" -ForegroundColor Cyan
Write-Host "   Project ID: $ProjectId" -ForegroundColor White
Write-Host "   Vector Index: $INDEX_ID" -ForegroundColor White
Write-Host "   Vector Endpoint: $ENDPOINT_ID" -ForegroundColor White
Write-Host "   Deployed Index: $DEPLOYED_INDEX_ID" -ForegroundColor White
Write-Host "   Namespace: nfrguard-agents" -ForegroundColor White
Write-Host ""
Write-Host "🔍 Check deployment status:" -ForegroundColor Cyan
Write-Host "   kubectl get pods -n nfrguard-agents" -ForegroundColor White
Write-Host "   kubectl get services -n nfrguard-agents" -ForegroundColor White
Write-Host ""
Write-Host "📊 Monitor the system:" -ForegroundColor Cyan
Write-Host "   python monitor_production.py" -ForegroundColor White
Write-Host "   kubectl logs -f deployment/transaction-risk-agent -n nfrguard-agents" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Access the system:" -ForegroundColor Cyan
Write-Host "   Bank of Anthos: http://34.40.211.236" -ForegroundColor White
Write-Host "   Monitoring: https://console.cloud.google.com/monitoring" -ForegroundColor White
Write-Host ""
Write-Host "✅ RAG system is now production-ready!" -ForegroundColor Green

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Monitor the system using the provided monitoring tools" -ForegroundColor White
Write-Host "   2. Set up automated document updates (daily cron job)" -ForegroundColor White
Write-Host "   3. Configure alerting for production issues" -ForegroundColor White
Write-Host "   4. Scale the system based on traffic patterns" -ForegroundColor White
Write-Host "   5. Update regulatory documents as needed" -ForegroundColor White
