#!/bin/bash
# Cleanup AWS Resources - Stop All Charges
# This script will delete all AWS resources created for the NFRGuard project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}🛑 AWS Resource Cleanup - Stopping All Charges${NC}"
echo -e "${YELLOW}⚠️  This will delete ALL AWS resources for the NFRGuard project!${NC}"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found. Please run create_secure_env.sh first.${NC}"
    exit 1
fi

# Source environment variables
source .env

echo -e "${BLUE}📋 Project Details:${NC}"
echo "   AWS Account ID: ${AWS_ACCOUNT_ID}"
echo "   AWS Region: ${AWS_REGION}"
echo "   Project Name: ${PROJECT_NAME}"
echo ""

# Confirmation prompt
read -p "Are you sure you want to delete ALL resources? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}❌ Cleanup cancelled.${NC}"
    exit 0
fi

echo -e "${YELLOW}🚀 Starting AWS resource cleanup...${NC}"

# Function to delete EKS cluster
function delete_eks_cluster() {
    echo -e "${YELLOW}🗑️  Deleting EKS cluster...${NC}"
    
    # Check for local eksctl first
    if [ -f "./eksctl/eksctl.exe" ]; then
        EKSCTL_CMD="./eksctl/eksctl.exe"
    else
        EKSCTL_CMD="eksctl"
    fi
    
    if ${EKSCTL_CMD} get cluster --name "${PROJECT_NAME}-cluster" --region ${AWS_REGION} &> /dev/null; then
        echo "Deleting EKS cluster: ${PROJECT_NAME}-cluster"
        ${EKSCTL_CMD} delete cluster --name "${PROJECT_NAME}-cluster" --region ${AWS_REGION} --wait
        echo -e "${GREEN}✅ EKS cluster deleted${NC}"
    else
        echo -e "${YELLOW}⚠️  EKS cluster not found or already deleted${NC}"
    fi
}

# Function to delete ECR repositories
function delete_ecr_repositories() {
    echo -e "${YELLOW}🗑️  Deleting ECR repositories...${NC}"
    
    local agents=("transaction_risk-agent" "compliance-agent" "resilience-agent" "customer_sentiment-agent" "data_privacy-agent" "knowledge-agent" "banking_assistant-agent")
    
    for agent in "${agents[@]}"; do
        if aws ecr describe-repositories --repository-names "${agent}" --region ${AWS_REGION} &> /dev/null; then
            echo "Deleting ECR repository: ${agent}"
            aws ecr delete-repository --repository-name "${agent}" --region ${AWS_REGION} --force
            echo -e "${GREEN}✅ ECR repository ${agent} deleted${NC}"
        else
            echo -e "${YELLOW}⚠️  ECR repository ${agent} not found${NC}"
        fi
    done
}

# Function to delete S3 buckets
function delete_s3_buckets() {
    echo -e "${YELLOW}🗑️  Deleting S3 buckets...${NC}"
    
    local buckets=(
        "${PROJECT_NAME}-agent-data"
        "${PROJECT_NAME}-agent-logs"
        "${PROJECT_NAME}-agent-backups"
        "${PROJECT_NAME}-documents"
        "${PROJECT_NAME}-embeddings"
    )
    
    for bucket in "${buckets[@]}"; do
        if aws s3 ls "s3://${bucket}" &> /dev/null; then
            echo "Deleting S3 bucket: ${bucket}"
            aws s3 rb "s3://${bucket}" --force
            echo -e "${GREEN}✅ S3 bucket ${bucket} deleted${NC}"
        else
            echo -e "${YELLOW}⚠️  S3 bucket ${bucket} not found${NC}"
        fi
    done
}

# Function to delete DynamoDB tables
function delete_dynamodb_tables() {
    echo -e "${YELLOW}🗑️  Deleting DynamoDB tables...${NC}"
    
    local tables=(
        "${PROJECT_NAME}-agent-state"
        "${PROJECT_NAME}-agent-metrics"
        "${PROJECT_NAME}-agent-events"
        "${PROJECT_NAME}-agent-conversations"
    )
    
    for table in "${tables[@]}"; do
        if aws dynamodb describe-table --table-name "${table}" --region ${AWS_REGION} &> /dev/null; then
            echo "Deleting DynamoDB table: ${table}"
            aws dynamodb delete-table --table-name "${table}" --region ${AWS_REGION}
            echo -e "${GREEN}✅ DynamoDB table ${table} deleted${NC}"
        else
            echo -e "${YELLOW}⚠️  DynamoDB table ${table} not found${NC}"
        fi
    done
}

# Function to delete EventBridge resources
function delete_eventbridge_resources() {
    echo -e "${YELLOW}🗑️  Deleting EventBridge resources...${NC}"
    
    # Delete custom event bus
    if aws events describe-event-bus --name "${PROJECT_NAME}-agent-bus" --region ${AWS_REGION} &> /dev/null; then
        echo "Deleting EventBridge event bus: ${PROJECT_NAME}-agent-bus"
        aws events delete-event-bus --name "${PROJECT_NAME}-agent-bus" --region ${AWS_REGION}
        echo -e "${GREEN}✅ EventBridge event bus deleted${NC}"
    else
        echo -e "${YELLOW}⚠️  EventBridge event bus not found${NC}"
    fi
}

# Function to delete IAM roles and policies
function delete_iam_resources() {
    echo -e "${YELLOW}🗑️  Deleting IAM resources...${NC}"
    
    # Delete IAM role
    if aws iam get-role --role-name "${PROJECT_NAME}-agent-role" &> /dev/null; then
        echo "Deleting IAM role: ${PROJECT_NAME}-agent-role"
        
        # Detach policies first
        aws iam list-attached-role-policies --role-name "${PROJECT_NAME}-agent-role" --query 'AttachedPolicies[].PolicyArn' --output text | while read policy_arn; do
            if [ ! -z "$policy_arn" ]; then
                aws iam detach-role-policy --role-name "${PROJECT_NAME}-agent-role" --policy-arn "$policy_arn"
            fi
        done
        
        # Delete the role
        aws iam delete-role --role-name "${PROJECT_NAME}-agent-role"
        echo -e "${GREEN}✅ IAM role deleted${NC}"
    else
        echo -e "${YELLOW}⚠️  IAM role not found${NC}"
    fi
    
    # Delete IAM policy
    if aws iam get-policy --policy-arn "arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${PROJECT_NAME}-agent-policy" &> /dev/null; then
        echo "Deleting IAM policy: ${PROJECT_NAME}-agent-policy"
        aws iam delete-policy --policy-arn "arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${PROJECT_NAME}-agent-policy"
        echo -e "${GREEN}✅ IAM policy deleted${NC}"
    else
        echo -e "${YELLOW}⚠️  IAM policy not found${NC}"
    fi
}

# Function to delete OpenSearch Serverless (if exists)
function delete_opensearch_resources() {
    echo -e "${YELLOW}🗑️  Deleting OpenSearch Serverless resources...${NC}"
    
    # Note: OpenSearch Serverless was not created due to complexity
    echo -e "${YELLOW}⚠️  OpenSearch Serverless resources were not created${NC}"
}

# Main cleanup execution
function main() {
    echo -e "${BLUE}🚀 Starting cleanup process...${NC}"
    
    # Delete resources in reverse order of creation
    delete_eks_cluster
    delete_ecr_repositories
    delete_s3_buckets
    delete_dynamodb_tables
    delete_eventbridge_resources
    delete_iam_resources
    delete_opensearch_resources
    
    echo ""
    echo -e "${GREEN}🎉 AWS resource cleanup completed!${NC}"
    echo -e "${GREEN}✅ All resources deleted - no more charges${NC}"
    echo ""
    echo -e "${BLUE}📋 What was deleted:${NC}"
    echo "   ✅ EKS cluster and node groups"
    echo "   ✅ ECR repositories and images"
    echo "   ✅ S3 buckets and data"
    echo "   ✅ DynamoDB tables"
    echo "   ✅ EventBridge event bus"
    echo "   ✅ IAM roles and policies"
    echo ""
    echo -e "${YELLOW}💡 To restart the project later:${NC}"
    echo "   1. Run: bash scripts/setup_aws_infrastructure.sh"
    echo "   2. Request Bedrock model access in AWS Console"
    echo "   3. Run: bash scripts/build_and_push_images.sh"
    echo "   4. Run: bash scripts/deploy_to_eks.sh"
    echo ""
    echo -e "${GREEN}🔒 Your local code and configurations are preserved!${NC}"
}

# Run main function
main
