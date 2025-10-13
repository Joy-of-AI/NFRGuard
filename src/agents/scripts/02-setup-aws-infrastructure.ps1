# AWS Infrastructure Setup Script for NFRGuard Agents
# Windows PowerShell version

param(
    [string]$AWS_REGION = "ap-southeast-2",
    [string]$PROJECT_NAME = "fintech-ai-aws",
    [string]$AWS_ACCOUNT_ID = "491085381971"
)

$ErrorActionPreference = "Stop"

# Colors for output
$RED = "Red"
$GREEN = "Green"
$YELLOW = "Yellow"

Write-Host "🚀 Setting up AWS Infrastructure for NFRGuard Agents" -ForegroundColor $GREEN

# Check prerequisites
function Check-Prerequisites {
    Write-Host "📋 Checking prerequisites..." -ForegroundColor $YELLOW
    
    # Check AWS CLI
    try {
        aws --version | Out-Null
        Write-Host "✅ AWS CLI found" -ForegroundColor $GREEN
    }
    catch {
        Write-Host "❌ AWS CLI not found. Please install it first." -ForegroundColor $RED
        Write-Host "Download from: https://aws.amazon.com/cli/" -ForegroundColor $YELLOW
        exit 1
    }
    
    # Check AWS credentials
    try {
        $detectedAccountId = aws sts get-caller-identity --query Account --output text 2>$null
        if ($detectedAccountId -ne $AWS_ACCOUNT_ID) {
            Write-Host "❌ AWS Account ID mismatch! Expected: $AWS_ACCOUNT_ID, Detected: $detectedAccountId" -ForegroundColor $RED
            exit 1
        }
        Write-Host "✅ AWS Account ID verified: $AWS_ACCOUNT_ID" -ForegroundColor $GREEN
    }
    catch {
        Write-Host "❌ AWS credentials not configured. Run 'aws configure' first." -ForegroundColor $RED
        exit 1
    }
    
    # Check eksctl
    try {
        eksctl version | Out-Null
        Write-Host "✅ eksctl found" -ForegroundColor $GREEN
    }
    catch {
        Write-Host "❌ eksctl not found. Please install it first." -ForegroundColor $RED
        Write-Host "Install from: https://eksctl.io/installation/" -ForegroundColor $YELLOW
        exit 1
    }
    
    Write-Host "✅ Prerequisites check passed" -ForegroundColor $GREEN
}

# Create S3 buckets
function Create-S3Buckets {
    Write-Host "📦 Creating S3 buckets..." -ForegroundColor $YELLOW
    
    $timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    
    # Documents bucket
    $documentsBucket = "$PROJECT_NAME-documents-$timestamp"
    aws s3 mb "s3://$documentsBucket" --region $AWS_REGION
    Write-Host "export DOCUMENTS_BUCKET=$documentsBucket" | Add-Content ".env"
    
    # Artifacts bucket
    $artifactsBucket = "$PROJECT_NAME-artifacts-$timestamp"
    aws s3 mb "s3://$artifactsBucket" --region $AWS_REGION
    Write-Host "export ARTIFACTS_BUCKET=$artifactsBucket" | Add-Content ".env"
    
    # Model artifacts bucket
    $modelArtifactsBucket = "$PROJECT_NAME-model-artifacts-$timestamp"
    aws s3 mb "s3://$modelArtifactsBucket" --region $AWS_REGION
    Write-Host "export MODEL_ARTIFACTS_BUCKET=$modelArtifactsBucket" | Add-Content ".env"
    
    Write-Host "✅ S3 buckets created" -ForegroundColor $GREEN
}

# Create DynamoDB tables
function Create-DynamoDBTables {
    Write-Host "🗄️ Creating DynamoDB tables..." -ForegroundColor $YELLOW
    
    # Agent state table
    aws dynamodb create-table `
        --table-name "$PROJECT_NAME-agent-state" `
        --attribute-definitions `
            AttributeName=agent_id,AttributeType=S `
            AttributeName=timestamp,AttributeType=N `
        --key-schema `
            AttributeName=agent_id,KeyType=HASH `
            AttributeName=timestamp,KeyType=RANGE `
        --billing-mode PAY_PER_REQUEST `
        --region $AWS_REGION
    
    # Transaction events table
    aws dynamodb create-table `
        --table-name "$PROJECT_NAME-transaction-events" `
        --attribute-definitions `
            AttributeName=transaction_id,AttributeType=S `
            AttributeName=timestamp,AttributeType=N `
        --key-schema `
            AttributeName=transaction_id,KeyType=HASH `
            AttributeName=timestamp,KeyType=RANGE `
        --billing-mode PAY_PER_REQUEST `
        --region $AWS_REGION
    
    Write-Host "✅ DynamoDB tables created" -ForegroundColor $GREEN
}

# Create EventBridge event bus
function Create-EventBridge {
    Write-Host "📡 Creating EventBridge event bus..." -ForegroundColor $YELLOW
    
    aws events create-event-bus `
        --name "$PROJECT_NAME-event-bus" `
        --region $AWS_REGION
    
    Write-Host "✅ EventBridge event bus created" -ForegroundColor $GREEN
}

# Create OpenSearch Serverless collection
function Create-OpenSearch {
    Write-Host "🔍 Creating OpenSearch Serverless collection..." -ForegroundColor $YELLOW
    
    $collectionName = "$PROJECT_NAME-regulations"
    
    aws opensearchserverless create-collection `
        --name $collectionName `
        --type VECTORSEARCH `
        --region $AWS_REGION
    
    # Wait for collection to be active
    Write-Host "Waiting for OpenSearch collection to be active..."
    aws opensearchserverless wait collection-active `
        --name $collectionName `
        --region $AWS_REGION
    
    # Get collection endpoint
    $opensearchEndpoint = aws opensearchserverless get-collection `
        --name $collectionName `
        --region $AWS_REGION `
        --query 'collectionDetail.collectionEndpoint' `
        --output text
    
    Write-Host "export OPENSEARCH_ENDPOINT=$opensearchEndpoint" | Add-Content ".env"
    Write-Host "export OPENSEARCH_COLLECTION_ID=$collectionName" | Add-Content ".env"
    
    Write-Host "✅ OpenSearch Serverless collection created" -ForegroundColor $GREEN
}

# Create IAM roles and policies
function Create-IAMResources {
    Write-Host "🔐 Creating IAM roles and policies..." -ForegroundColor $YELLOW
    
    # Create trust policy for EKS
    $trustPolicy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::$AWS_ACCOUNT_ID`:oidc-provider/oidc.eks.$AWS_REGION.amazonaws.com/id/CLUSTER_OIDC_ID"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "oidc.eks.$AWS_REGION.amazonaws.com/id/CLUSTER_OIDC_ID:sub": "system:serviceaccount:nfrguard-agents:nfrguard-sa",
          "oidc.eks.$AWS_REGION.amazonaws.com/id/CLUSTER_OIDC_ID:aud": "sts.amazonaws.com"
        }
      }
    }
  ]
}
"@
    
    $trustPolicy | Out-File -FilePath "eks-trust-policy.json" -Encoding UTF8
    
    # Create agent role
    aws iam create-role `
        --role-name "$PROJECT_NAME-agent-role" `
        --assume-role-policy-document file://eks-trust-policy.json `
        --region $AWS_REGION
    
    # Attach policies to agent role
    $policies = @(
        "arn:aws:iam::aws:policy/AmazonBedrockFullAccess",
        "arn:aws:iam::aws:policy/AmazonS3FullAccess",
        "arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess",
        "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
    )
    
    foreach ($policy in $policies) {
        aws iam attach-role-policy `
            --role-name "$PROJECT_NAME-agent-role" `
            --policy-arn $policy
    }
    
    Write-Host "✅ IAM roles and policies created" -ForegroundColor $GREEN
}

# Create EKS cluster
function Create-EKSCluster {
    Write-Host "☸️ Creating EKS cluster..." -ForegroundColor $YELLOW
    
    eksctl create cluster `
        --name "$PROJECT_NAME-cluster" `
        --region $AWS_REGION `
        --nodegroup-name standard-workers `
        --node-type t3.medium `
        --nodes 2 `
        --nodes-min 1 `
        --nodes-max 3 `
        --managed `
        --with-oidc `
        --ssh-access `
        --spot
    
    # Update kubeconfig
    aws eks update-kubeconfig `
        --region $AWS_REGION `
        --name "$PROJECT_NAME-cluster"
    
    Write-Host "✅ EKS cluster created" -ForegroundColor $GREEN
}

# Set up IRSA (IAM Roles for Service Accounts)
function Setup-IRSA {
    Write-Host "🔗 Setting up IRSA..." -ForegroundColor $YELLOW
    
    eksctl create iamserviceaccount `
        --name nfrguard-sa `
        --namespace nfrguard-agents `
        --cluster "$PROJECT_NAME-cluster" `
        --role-name "$PROJECT_NAME-agent-role" `
        --attach-policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess `
        --attach-policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess `
        --attach-policy-arn arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess `
        --attach-policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess `
        --approve `
        --region $AWS_REGION
    
    Write-Host "✅ IRSA configured" -ForegroundColor $GREEN
}

# Create ECR repositories
function Create-ECRRepositories {
    Write-Host "🐳 Creating ECR repositories..." -ForegroundColor $YELLOW
    
    $agents = @("transaction-risk", "compliance", "resilience", "customer-sentiment", "data-privacy", "knowledge", "banking-assistant")
    
    foreach ($agent in $agents) {
        try {
            aws ecr create-repository `
                --repository-name "$agent-agent" `
                --region $AWS_REGION
        }
        catch {
            Write-Host "Repository $agent-agent already exists or error occurred" -ForegroundColor $YELLOW
        }
    }
    
    Write-Host "✅ ECR repositories created" -ForegroundColor $GREEN
}

# Request Bedrock model access
function Request-BedrockAccess {
    Write-Host "🤖 Requesting Bedrock model access..." -ForegroundColor $YELLOW
    
    Write-Host "Please go to AWS Console and request access to:" -ForegroundColor $YELLOW
    Write-Host "- Anthropic Claude 3.5 Sonnet" -ForegroundColor $YELLOW
    Write-Host "- Amazon Titan Text Embeddings V2" -ForegroundColor $YELLOW
    Write-Host ""
    Write-Host "URL: https://console.aws.amazon.com/bedrock/home?region=$AWS_REGION#/modelaccess" -ForegroundColor $YELLOW
    Write-Host ""
    Read-Host "Press Enter after requesting model access"
    
    Write-Host "✅ Bedrock model access requested" -ForegroundColor $GREEN
}

# Main execution
function Main {
    Write-Host "Starting AWS infrastructure setup..." -ForegroundColor $GREEN
    
    # Create .env file header
    $envHeader = @"
# AWS Infrastructure Configuration
export AWS_REGION=$AWS_REGION
export AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID
export PROJECT_NAME=$PROJECT_NAME
"@
    
    $envHeader | Out-File -FilePath ".env" -Encoding UTF8
    
    Check-Prerequisites
    Create-S3Buckets
    Create-DynamoDBTables
    Create-EventBridge
    Create-OpenSearch
    Create-IAMResources
    Create-EKSCluster
    Setup-IRSA
    Create-ECRRepositories
    Request-BedrockAccess
    
    Write-Host "🎉 AWS infrastructure setup completed!" -ForegroundColor $GREEN
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor $YELLOW
    Write-Host "1. Source the environment file: . .env" -ForegroundColor $YELLOW
    Write-Host "2. Build and push Docker images: .\scripts\build_and_push_images.ps1" -ForegroundColor $YELLOW
    Write-Host "3. Deploy agents to EKS: .\scripts\deploy_to_eks.ps1" -ForegroundColor $YELLOW
    Write-Host ""
    Write-Host "Environment variables saved to .env file" -ForegroundColor $GREEN
}

# Run main function
Main


