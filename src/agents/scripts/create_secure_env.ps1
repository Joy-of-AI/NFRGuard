# Create secure environment file with AWS credentials
# Windows PowerShell version

Write-Host "🔐 Creating secure environment configuration" -ForegroundColor Green

# Check if .env already exists
if (Test-Path ".env") {
    Write-Host "⚠️ .env file already exists. Creating backup..." -ForegroundColor Yellow
    Copy-Item ".env" ".env.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
}

# Create .env file with provided values
$envContent = @"
# AWS Configuration - DO NOT COMMIT TO GIT
# Generated on $(Get-Date)

# AWS Account Details
export AWS_ACCOUNT_ID=491085381971
export AWS_REGION=ap-southeast-2

# AWS Credentials (Alternative to AWS CLI configuration)
export AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID_HERE
export AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY_HERE

# Project Configuration
export PROJECT_NAME=fintech-ai-aws

# Bedrock Models
export BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
export BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v2:0

# S3 Buckets (will be created automatically with timestamps)
export S3_BUCKET_NAME=fintech-ai-aws-documents
export S3_ARTIFACTS_BUCKET=fintech-ai-aws-artifacts
export S3_MODEL_ARTIFACTS_BUCKET=fintech-ai-aws-model-artifacts

# OpenSearch (will be set after creation)
export OPENSEARCH_ENDPOINT=
export OPENSEARCH_COLLECTION_ID=fintech-ai-aws-regulations

# EventBridge
export EVENT_BUS_NAME=fintech-ai-aws-event-bus
export USE_AWS_MESSAGING=true

# DynamoDB Tables
export AGENT_STATE_TABLE=fintech-ai-aws-agent-state
export TRANSACTION_EVENTS_TABLE=fintech-ai-aws-transaction-events

# EKS Configuration
export EKS_CLUSTER_NAME=fintech-ai-aws-cluster
export EKS_NODE_TYPE=t3.medium
export EKS_MIN_NODES=1
export EKS_MAX_NODES=3
export EKS_DESIRED_NODES=2

# Cost Management
export ENABLE_SPOT_INSTANCES=true
export ENABLE_CLUSTER_AUTOSCALER=true

# Security
export ENABLE_ENCRYPTION=true
export ENABLE_VPC_ENDPOINTS=false

# Monitoring
export ENABLE_CLOUDWATCH_LOGS=true
export ENABLE_ALARMS=true

# Generated timestamp
export SETUP_TIMESTAMP=$(Get-Date -UFormat %s)
"@

# Write to .env file
$envContent | Out-File -FilePath ".env" -Encoding UTF8

Write-Host "✅ Secure .env file created" -ForegroundColor Green
Write-Host "⚠️ IMPORTANT: Never commit .env file to git!" -ForegroundColor Yellow
Write-Host "⚠️ Keep your AWS credentials secure and never share them!" -ForegroundColor Yellow

# Verify gitignore
$gitignoreContent = Get-Content ".gitignore" -ErrorAction SilentlyContinue
if ($gitignoreContent -notcontains ".env") {
    Write-Host "Adding .env to .gitignore..." -ForegroundColor Yellow
    Add-Content ".gitignore" "`n# Environment variables`n.env"
}

Write-Host "🔐 Environment setup complete!" -ForegroundColor Green



