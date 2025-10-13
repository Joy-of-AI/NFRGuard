# Deploy NFRGuard Agents to EKS
# Windows PowerShell version

$ErrorActionPreference = "Stop"

# Colors for output
$RED = "Red"
$GREEN = "Green"
$YELLOW = "Yellow"

Write-Host "🚀 Deploying NFRGuard Agents to EKS" -ForegroundColor $GREEN

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
    
    # Check kubectl
    try {
        kubectl version --client | Out-Null
        Write-Host "✅ kubectl found" -ForegroundColor $GREEN
    }
    catch {
        Write-Host "❌ kubectl not found. Please install it first." -ForegroundColor $RED
        Write-Host "Download from: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/" -ForegroundColor $YELLOW
        exit 1
    }
    
    # Check if cluster is accessible
    try {
        kubectl cluster-info | Out-Null
        Write-Host "✅ EKS cluster accessible" -ForegroundColor $GREEN
    }
    catch {
        Write-Host "❌ Cannot access EKS cluster. Please check your kubeconfig." -ForegroundColor $RED
        exit 1
    }
    
    Write-Host "✅ Prerequisites check passed" -ForegroundColor $GREEN
}

# Deploy namespace and service account
function Deploy-Namespace {
    Write-Host "📦 Deploying namespace and service account..." -ForegroundColor $YELLOW
    
    # Replace variables in namespace.yaml
    $namespaceContent = Get-Content "k8s/aws/namespace.yaml" -Raw
    $namespaceContent = $namespaceContent -replace '\$\{AWS_ACCOUNT_ID\}', $env:AWS_ACCOUNT_ID
    $namespaceContent | kubectl apply -f -
    
    Write-Host "✅ Namespace and service account deployed" -ForegroundColor $GREEN
}

# Deploy ConfigMap and Secrets
function Deploy-Config {
    Write-Host "⚙️ Deploying configuration..." -ForegroundColor $YELLOW
    
    # Replace variables in configmap.yaml
    $configContent = Get-Content "k8s/aws/configmap.yaml" -Raw
    $configContent = $configContent -replace '\$\{OPENSEARCH_ENDPOINT\}', $env:OPENSEARCH_ENDPOINT
    $configContent = $configContent -replace '\$\{OPENSEARCH_COLLECTION_ID\}', $env:OPENSEARCH_COLLECTION_ID
    $configContent | kubectl apply -f -
    
    Write-Host "✅ Configuration deployed" -ForegroundColor $GREEN
}

# Deploy agents
function Deploy-Agents {
    Write-Host "🤖 Deploying agents..." -ForegroundColor $YELLOW
    
    # Replace variables in agents.yaml
    $agentsContent = Get-Content "k8s/aws/agents.yaml" -Raw
    $agentsContent = $agentsContent -replace '\$\{AWS_ACCOUNT_ID\}', $env:AWS_ACCOUNT_ID
    $agentsContent = $agentsContent -replace '\$\{AWS_REGION\}', $env:AWS_REGION
    $agentsContent = $agentsContent -replace '\$\{ACM_CERTIFICATE_ARN\}', ""
    $agentsContent = $agentsContent -replace '\$\{INGRESS_HOST\}', "nfrguard.local"
    $agentsContent | kubectl apply -f -
    
    Write-Host "✅ Agents deployed" -ForegroundColor $GREEN
}

# Wait for deployments
function Wait-ForDeployments {
    Write-Host "⏳ Waiting for deployments to be ready..." -ForegroundColor $YELLOW
    
    $deployments = @(
        "transaction-risk-agent",
        "compliance-agent", 
        "resilience-agent",
        "customer-sentiment-agent",
        "data-privacy-agent",
        "knowledge-agent",
        "banking-assistant-agent"
    )
    
    foreach ($deployment in $deployments) {
        Write-Host "Waiting for $deployment..." -ForegroundColor $YELLOW
        kubectl wait --for=condition=available --timeout=300s "deployment/$deployment" -n nfrguard-agents
    }
    
    Write-Host "✅ All deployments are ready" -ForegroundColor $GREEN
}

# Show deployment status
function Show-Status {
    Write-Host "📊 Deployment Status:" -ForegroundColor $YELLOW
    
    Write-Host "`nPods:" -ForegroundColor $YELLOW
    kubectl get pods -n nfrguard-agents
    
    Write-Host "`nServices:" -ForegroundColor $YELLOW
    kubectl get services -n nfrguard-agents
    
    Write-Host "`nIngress:" -ForegroundColor $YELLOW
    kubectl get ingress -n nfrguard-agents
}

# Test deployments
function Test-Deployments {
    Write-Host "🧪 Testing deployments..." -ForegroundColor $YELLOW
    
    # Test banking assistant agent
    try {
        $bankingPod = kubectl get pods -n nfrguard-agents -l app=banking-assistant-agent -o jsonpath='{.items[0].metadata.name}' 2>$null
        if ($bankingPod) {
            kubectl exec -n nfrguard-agents $bankingPod -- curl -s http://localhost:8080/health
            Write-Host "✅ Banking assistant agent is healthy" -ForegroundColor $GREEN
        }
    }
    catch {
        Write-Host "❌ Banking assistant agent health check failed" -ForegroundColor $RED
    }
    
    # Test other agents
    $agents = @("transaction-risk", "compliance", "resilience", "customer-sentiment", "data-privacy", "knowledge")
    foreach ($agent in $agents) {
        try {
            $pod = kubectl get pods -n nfrguard-agents -l "app=$agent-agent" -o jsonpath='{.items[0].metadata.name}' 2>$null
            if ($pod) {
                Write-Host "✅ $agent agent is running" -ForegroundColor $GREEN
            }
            else {
                Write-Host "❌ $agent agent is not running" -ForegroundColor $RED
            }
        }
        catch {
            Write-Host "❌ $agent agent is not running" -ForegroundColor $RED
        }
    }
}

# Main execution
function Main {
    Check-Prerequisites
    Deploy-Namespace
    Deploy-Config
    Deploy-Agents
    Wait-ForDeployments
    Show-Status
    Test-Deployments
    
    Write-Host "🎉 Deployment completed successfully!" -ForegroundColor $GREEN
    Write-Host ""
    Write-Host "Access your agents:" -ForegroundColor $YELLOW
    Write-Host "- Banking Assistant: kubectl port-forward -n nfrguard-agents svc/banking-assistant-agent 8080:8080" -ForegroundColor $YELLOW
    Write-Host "- Then visit: http://localhost:8080" -ForegroundColor $YELLOW
    Write-Host ""
    Write-Host "Monitor logs:" -ForegroundColor $YELLOW
    Write-Host "- kubectl logs -n nfrguard-agents -l app=banking-assistant-agent -f" -ForegroundColor $YELLOW
}

# Run main function
Main


