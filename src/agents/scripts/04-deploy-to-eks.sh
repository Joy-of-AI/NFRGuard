#!/bin/bash
# Deploy NFRGuard Agents to EKS
# This script deploys all agents to the EKS cluster

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploying NFRGuard Agents to EKS${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found. Please run setup_aws_infrastructure.sh first.${NC}"
    exit 1
fi

# Source environment variables
source .env

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl not found. Please install it first.${NC}"
        exit 1
    fi
    
    # Check if cluster is accessible
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}❌ Cannot access EKS cluster. Please check your kubeconfig.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Deploy namespace and service account
deploy_namespace() {
    echo -e "${YELLOW}📦 Deploying namespace and service account...${NC}"
    
    # Replace variables in namespace.yaml
    sed "s/\${AWS_ACCOUNT_ID}/${AWS_ACCOUNT_ID}/g" k8s/aws/namespace.yaml | kubectl apply -f -
    
    echo -e "${GREEN}✅ Namespace and service account deployed${NC}"
}

# Deploy ConfigMap and Secrets
deploy_config() {
    echo -e "${YELLOW}⚙️ Deploying configuration...${NC}"
    
    # Replace variables in configmap.yaml
    sed -e "s/\${OPENSEARCH_ENDPOINT}/${OPENSEARCH_ENDPOINT}/g" \
        -e "s/\${OPENSEARCH_COLLECTION_ID}/${OPENSEARCH_COLLECTION_ID}/g" \
        k8s/aws/configmap.yaml | kubectl apply -f -
    
    echo -e "${GREEN}✅ Configuration deployed${NC}"
}

# Deploy agents
deploy_agents() {
    echo -e "${YELLOW}🤖 Deploying agents...${NC}"
    
    # Replace variables in agents.yaml
    sed -e "s/\${AWS_ACCOUNT_ID}/${AWS_ACCOUNT_ID}/g" \
        -e "s/\${AWS_REGION}/${AWS_REGION}/g" \
        -e "s/\${ACM_CERTIFICATE_ARN}/${ACM_CERTIFICATE_ARN:-}/g" \
        -e "s/\${INGRESS_HOST}/${INGRESS_HOST:-nfrguard.local}/g" \
        k8s/aws/agents.yaml | kubectl apply -f -
    
    echo -e "${GREEN}✅ Agents deployed${NC}"
}

# Wait for deployments
wait_for_deployments() {
    echo -e "${YELLOW}⏳ Waiting for deployments to be ready...${NC}"
    
    kubectl wait --for=condition=available --timeout=300s deployment/transaction-risk-agent -n nfrguard-agents
    kubectl wait --for=condition=available --timeout=300s deployment/compliance-agent -n nfrguard-agents
    kubectl wait --for=condition=available --timeout=300s deployment/resilience-agent -n nfrguard-agents
    kubectl wait --for=condition=available --timeout=300s deployment/customer-sentiment-agent -n nfrguard-agents
    kubectl wait --for=condition=available --timeout=300s deployment/data-privacy-agent -n nfrguard-agents
    kubectl wait --for=condition=available --timeout=300s deployment/knowledge-agent -n nfrguard-agents
    kubectl wait --for=condition=available --timeout=300s deployment/banking-assistant-agent -n nfrguard-agents
    
    echo -e "${GREEN}✅ All deployments are ready${NC}"
}

# Show deployment status
show_status() {
    echo -e "${YELLOW}📊 Deployment Status:${NC}"
    
    kubectl get pods -n nfrguard-agents
    kubectl get services -n nfrguard-agents
    kubectl get ingress -n nfrguard-agents
}

# Test deployments
test_deployments() {
    echo -e "${YELLOW}🧪 Testing deployments...${NC}"
    
    # Test banking assistant agent
    BANKING_POD=$(kubectl get pods -n nfrguard-agents -l app=banking-assistant-agent -o jsonpath='{.items[0].metadata.name}')
    
    if kubectl exec -n nfrguard-agents $BANKING_POD -- curl -s http://localhost:8080/health; then
        echo -e "${GREEN}✅ Banking assistant agent is healthy${NC}"
    else
        echo -e "${RED}❌ Banking assistant agent health check failed${NC}"
    fi
    
    # Test other agents
    for agent in transaction-risk compliance resilience customer-sentiment data-privacy knowledge; do
        POD=$(kubectl get pods -n nfrguard-agents -l app=${agent}-agent -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
        if [ -n "$POD" ]; then
            echo -e "${GREEN}✅ ${agent} agent is running${NC}"
        else
            echo -e "${RED}❌ ${agent} agent is not running${NC}"
        fi
    done
}

# Main execution
main() {
    check_prerequisites
    deploy_namespace
    deploy_config
    deploy_agents
    wait_for_deployments
    show_status
    test_deployments
    
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo ""
    echo "Access your agents:"
    echo "- Banking Assistant: kubectl port-forward -n nfrguard-agents svc/banking-assistant-agent 8080:8080"
    echo "- Then visit: http://localhost:8080"
    echo ""
    echo "Monitor logs:"
    echo "- kubectl logs -n nfrguard-agents -l app=banking-assistant-agent -f"
}

# Run main function
main "$@"



