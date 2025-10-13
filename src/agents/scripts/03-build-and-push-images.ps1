# Build and Push Docker Images to ECR
# Windows PowerShell version

$ErrorActionPreference = "Stop"

# Colors for output
$RED = "Red"
$GREEN = "Green"
$YELLOW = "Yellow"

Write-Host "🐳 Building and pushing Docker images to ECR" -ForegroundColor $GREEN

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found. Please run create_secure_env.ps1 first." -ForegroundColor $RED
    exit 1
}

# Source environment variables
Get-Content ".env" | ForEach-Object {
    if ($_ -match "^export\s+(\w+)=(.*)$") {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

# Check prerequisites
function Check-Prerequisites {
    Write-Host "📋 Checking prerequisites..." -ForegroundColor $YELLOW
    
    # Check Docker
    try {
        docker --version | Out-Null
        Write-Host "✅ Docker found" -ForegroundColor $GREEN
    }
    catch {
        Write-Host "❌ Docker not found. Please install Docker Desktop first." -ForegroundColor $RED
        Write-Host "Download from: https://www.docker.com/products/docker-desktop/" -ForegroundColor $YELLOW
        exit 1
    }
    
    # Check AWS CLI
    try {
        aws --version | Out-Null
        Write-Host "✅ AWS CLI found" -ForegroundColor $GREEN
    }
    catch {
        Write-Host "❌ AWS CLI not found. Please install it first." -ForegroundColor $RED
        exit 1
    }
    
    Write-Host "✅ Prerequisites check passed" -ForegroundColor $GREEN
}

# Login to ECR
function Login-ECR {
    Write-Host "🔐 Logging in to ECR..." -ForegroundColor $YELLOW
    
    $ecrRegistry = "$($env:AWS_ACCOUNT_ID).dkr.ecr.$($env:AWS_REGION).amazonaws.com"
    
    aws ecr get-login-password --region $env:AWS_REGION | docker login --username AWS --password-stdin $ecrRegistry
    
    Write-Host "✅ ECR login successful" -ForegroundColor $GREEN
}

# Build and push agent images
function Build-PushImages {
    Write-Host "🏗️ Building and pushing agent images..." -ForegroundColor $YELLOW
    
    $agents = @("transaction-risk", "compliance", "resilience", "customer-sentiment", "data-privacy", "knowledge", "banking-assistant")
    $ecrRegistry = "$($env:AWS_ACCOUNT_ID).dkr.ecr.$($env:AWS_REGION).amazonaws.com"
    
    foreach ($agent in $agents) {
        Write-Host "Building $agent agent..." -ForegroundColor $YELLOW
        
        # Check if agent directory exists
        $agentDir = "$agent-agent"
        if (-not (Test-Path $agentDir)) {
            Write-Host "⚠️ Directory $agentDir not found, skipping..." -ForegroundColor $YELLOW
            continue
        }
        
        # Build Docker image
        docker build -t "$agent-agent:latest" "./$agentDir/"
        
        # Tag for ECR
        docker tag "$agent-agent:latest" "$ecrRegistry/$agent-agent:latest"
        
        # Push to ECR
        docker push "$ecrRegistry/$agent-agent:latest"
        
        Write-Host "✅ $agent agent built and pushed successfully" -ForegroundColor $GREEN
    }
}

# Main execution
function Main {
    Check-Prerequisites
    Login-ECR
    Build-PushImages
    
    Write-Host "🎉 All Docker images built and pushed successfully!" -ForegroundColor $GREEN
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor $YELLOW
    Write-Host "1. Deploy agents to EKS: .\scripts\deploy_to_eks.ps1" -ForegroundColor $YELLOW
    Write-Host "2. Run tests: .\scripts\run_tests.ps1" -ForegroundColor $YELLOW
}

# Run main function
Main


