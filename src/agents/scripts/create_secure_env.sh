#!/bin/bash
# Create secure environment file with AWS credentials
# This script creates a secure .env file that will not be committed to git

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Creating secure environment configuration${NC}"

# Check if .env already exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}WARNING: .env file already exists. Creating backup...${NC}"
    cp .env .env.backup.$(date +%s)
fi

# Create .env file with provided values
cat > .env << EOF
# AWS Configuration - DO NOT COMMIT TO GIT
# Generated on $(date)

# AWS Account Details
export AWS_ACCOUNT_ID=491085381971
export AWS_REGION=ap-southeast-2

# AWS Credentials (Alternative to AWS CLI configuration)
# Note: These are placeholder examples - replace with your actual credentials
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
export SETUP_TIMESTAMP=$(date +%s)
EOF

# Set secure permissions
chmod 600 .env

echo -e "${GREEN}SUCCESS: Secure .env file created with permissions 600${NC}"
echo -e "${YELLOW}IMPORTANT: Never commit .env file to git!${NC}"
echo -e "${YELLOW}IMPORTANT: Keep your AWS credentials secure and never share them!${NC}"

# Verify gitignore
if ! grep -q "\.env" .gitignore; then
    echo -e "${YELLOW}Adding .env to .gitignore...${NC}"
    echo "" >> .gitignore
    echo "# Environment variables" >> .gitignore
    echo ".env" >> .gitignore
fi

echo -e "${GREEN}Environment setup complete!${NC}"

