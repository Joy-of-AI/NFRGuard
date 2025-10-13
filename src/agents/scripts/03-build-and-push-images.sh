#!/bin/bash
# Build and Push Docker Images to ECR
# This script builds Docker images for all agents and pushes them to ECR

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 Building and pushing Docker images to ECR${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found. Please run create_secure_env.sh first.${NC}"
    exit 1
fi

# Source environment variables
source .env

# Check prerequisites
function check_prerequisites() {
    echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found. Please install Docker Desktop first.${NC}"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker is not running. Please start Docker Desktop.${NC}"
        exit 1
    fi
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Login to ECR
function login_ecr() {
    echo -e "${YELLOW}🔐 Logging in to ECR...${NC}"
    
    local ecr_registry="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    
    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ecr_registry}
    
    echo -e "${GREEN}✅ ECR login successful${NC}"
}

# Create ECR repositories if they don't exist
function create_ecr_repositories() {
    echo -e "${YELLOW}📦 Creating ECR repositories...${NC}"
    
    local agents=("transaction_risk" "compliance" "resilience" "customer_sentiment" "data_privacy" "knowledge" "banking_assistant")
    
    for agent in "${agents[@]}"; do
        echo "Creating repository for ${agent} agent..."
        
        # Check if repository exists
        if aws ecr describe-repositories --repository-names "${agent}-agent" --region ${AWS_REGION} &> /dev/null; then
            echo "Repository ${agent}-agent already exists"
        else
            aws ecr create-repository --repository-name "${agent}-agent" --region ${AWS_REGION}
            echo "Created repository ${agent}-agent"
        fi
    done
    
    echo -e "${GREEN}✅ ECR repositories ready${NC}"
}

# Build and push agent images
function build_push_images() {
    echo -e "${YELLOW}🏗️ Building and pushing agent images...${NC}"
    
    local agents=("transaction_risk" "compliance" "resilience" "customer_sentiment" "data_privacy" "knowledge" "banking_assistant")
    local ecr_registry="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    
    for agent in "${agents[@]}"; do
        echo "Building ${agent} agent..."
        
        # Check if agent directory exists
        local agent_dir="${agent}_agent"
        if [ ! -d "$agent_dir" ]; then
            echo -e "${YELLOW}⚠️ Directory $agent_dir not found, skipping...${NC}"
            continue
        fi
        
        # Copy shared directory to agent directory for build context
        cp -r shared "./${agent_dir}/"
        
        # Build Docker image
        docker build -t "${agent}-agent:latest" "./${agent_dir}/"
        
        # Clean up copied shared directory
        rm -rf "./${agent_dir}/shared"
        
        # Tag for ECR
        docker tag "${agent}-agent:latest" "${ecr_registry}/${agent}-agent:latest"
        
        # Push to ECR
        docker push "${ecr_registry}/${agent}-agent:latest"
        
        echo -e "${GREEN}✅ ${agent} agent built and pushed successfully${NC}"
    done
}

# Main execution
function main() {
    check_prerequisites
    login_ecr
    create_ecr_repositories
    build_push_images
    
    echo -e "${GREEN}🎉 All Docker images built and pushed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Deploy agents to EKS: bash scripts/deploy_to_eks.sh"
    echo "2. Run tests: bash scripts/run_tests.sh"
}

# Run main function
main

