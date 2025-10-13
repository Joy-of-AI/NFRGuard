#!/bin/bash
# AWS Infrastructure Setup Script for NFRGuard Agents
# This script sets up all required AWS services for the agent system

set -e

# Configuration
AWS_REGION=${AWS_REGION:-"ap-southeast-2"}
PROJECT_NAME=${PROJECT_NAME:-"fintech-ai-aws"}
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID:-"491085381971"}
TIMESTAMP=$(date +%s)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Setting up AWS Infrastructure for NFRGuard Agents${NC}"

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}❌ AWS credentials not configured. Run 'aws configure' first.${NC}"
        exit 1
    fi
    
    # Verify AWS Account ID
    DETECTED_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    if [ "$DETECTED_ACCOUNT_ID" != "$AWS_ACCOUNT_ID" ]; then
        echo -e "${RED}❌ AWS Account ID mismatch! Expected: ${AWS_ACCOUNT_ID}, Detected: ${DETECTED_ACCOUNT_ID}${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ AWS Account ID verified: ${AWS_ACCOUNT_ID}${NC}"
    
    # Check eksctl (try local version first)
    if [ -f "./eksctl/eksctl.exe" ]; then
        EKSCTL_CMD="./eksctl/eksctl.exe"
        echo -e "${GREEN}✅ Using local eksctl${NC}"
    elif command -v eksctl &> /dev/null; then
        EKSCTL_CMD="eksctl"
        echo -e "${GREEN}✅ Using system eksctl${NC}"
    else
        echo -e "${RED}❌ eksctl not found. Please install it first.${NC}"
        echo "Install from: https://eksctl.io/installation/"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Create S3 buckets
create_s3_buckets() {
    echo -e "${YELLOW}📦 Creating S3 buckets...${NC}"
    
    # Documents bucket
    DOCUMENTS_BUCKET="${PROJECT_NAME}-documents-${TIMESTAMP}"
    aws s3 mb s3://${DOCUMENTS_BUCKET} --region ${AWS_REGION}
    echo "export DOCUMENTS_BUCKET=${DOCUMENTS_BUCKET}" >> .env
    
    # Artifacts bucket
    ARTIFACTS_BUCKET="${PROJECT_NAME}-artifacts-${TIMESTAMP}"
    aws s3 mb s3://${ARTIFACTS_BUCKET} --region ${AWS_REGION}
    echo "export ARTIFACTS_BUCKET=${ARTIFACTS_BUCKET}" >> .env
    
    # Model artifacts bucket
    MODEL_ARTIFACTS_BUCKET="${PROJECT_NAME}-model-artifacts-${TIMESTAMP}"
    aws s3 mb s3://${MODEL_ARTIFACTS_BUCKET} --region ${AWS_REGION}
    echo "export MODEL_ARTIFACTS_BUCKET=${MODEL_ARTIFACTS_BUCKET}" >> .env
    
    echo -e "${GREEN}✅ S3 buckets created${NC}"
}

# Create DynamoDB tables
create_dynamodb_tables() {
    echo -e "${YELLOW}🗄️ Creating DynamoDB tables...${NC}"
    
    # Agent state table
    aws dynamodb create-table \
        --table-name ${PROJECT_NAME}-agent-state \
        --attribute-definitions \
            AttributeName=agent_id,AttributeType=S \
            AttributeName=timestamp,AttributeType=N \
        --key-schema \
            AttributeName=agent_id,KeyType=HASH \
            AttributeName=timestamp,KeyType=RANGE \
        --billing-mode PAY_PER_REQUEST \
        --region ${AWS_REGION}
    
    # Transaction events table
    aws dynamodb create-table \
        --table-name ${PROJECT_NAME}-transaction-events \
        --attribute-definitions \
            AttributeName=transaction_id,AttributeType=S \
            AttributeName=timestamp,AttributeType=N \
        --key-schema \
            AttributeName=transaction_id,KeyType=HASH \
            AttributeName=timestamp,KeyType=RANGE \
        --billing-mode PAY_PER_REQUEST \
        --region ${AWS_REGION}
    
    echo -e "${GREEN}✅ DynamoDB tables created${NC}"
}

# Create EventBridge event bus
create_eventbridge() {
    echo -e "${YELLOW}📡 Creating EventBridge event bus...${NC}"
    
    aws events create-event-bus \
        --name ${PROJECT_NAME}-event-bus \
        --region ${AWS_REGION}
    
    echo -e "${GREEN}✅ EventBridge event bus created${NC}"
}

# Create OpenSearch Serverless collection
create_opensearch() {
    echo -e "${YELLOW}🔍 Creating OpenSearch Serverless collection...${NC}"
    
    COLLECTION_NAME="${PROJECT_NAME}-regulations"
    
    # Create encryption policy first
    echo "Creating encryption policy..."
    cat > encryption-policy.json << EOF
{
    "Rules": [
        {
            "ResourceType": "collection",
            "Resource": [
                "collection/${COLLECTION_NAME}"
            ]
        }
    ],
    "AWSOwnedKey": true
}
EOF
    
    aws opensearchserverless create-security-policy \
        --name "${COLLECTION_NAME}-encryption" \
        --type encryption \
        --policy file://encryption-policy.json \
        --region ${AWS_REGION}
    
    # Create network policy
    echo "Creating network policy..."
    cat > network-policy.json << EOF
[
    {
        "Rules": [
            {
                "ResourceType": "collection",
                "Resource": [
                    "collection/${COLLECTION_NAME}"
                ]
            }
        ],
        "AllowFromPublic": true
    }
]
EOF
    
    aws opensearchserverless create-security-policy \
        --name "${COLLECTION_NAME}-network" \
        --type network \
        --policy file://network-policy.json \
        --region ${AWS_REGION}
    
    # Create data access policy
    echo "Creating data access policy..."
    cat > data-policy.json << EOF
[
    {
        "Rules": [
            {
                "ResourceType": "collection",
                "Resource": [
                    "collection/${COLLECTION_NAME}"
                ],
                "Permission": [
                    "aoss:CreateCollectionItems",
                    "aoss:DeleteCollectionItems",
                    "aoss:UpdateCollectionItems",
                    "aoss:DescribeCollectionItems"
                ]
            },
            {
                "ResourceType": "index",
                "Resource": [
                    "index/${COLLECTION_NAME}/*"
                ],
                "Permission": [
                    "aoss:CreateIndex",
                    "aoss:DeleteIndex",
                    "aoss:UpdateIndex",
                    "aoss:DescribeIndex",
                    "aoss:ReadDocument",
                    "aoss:WriteDocument"
                ]
            }
        ],
        "Principal": [
            "arn:aws:iam::${AWS_ACCOUNT_ID}:root"
        ]
    }
]
EOF
    
    aws opensearchserverless create-access-policy \
        --name "${COLLECTION_NAME}-data" \
        --type data \
        --policy file://data-policy.json \
        --region ${AWS_REGION}
    
    # Create collection
    aws opensearchserverless create-collection \
        --name ${COLLECTION_NAME} \
        --type VECTORSEARCH \
        --region ${AWS_REGION}
    
    # Wait for collection to be active
    echo "Waiting for OpenSearch collection to be active..."
    aws opensearchserverless wait collection-active \
        --name ${COLLECTION_NAME} \
        --region ${AWS_REGION}
    
    # Get collection endpoint
    OPENSEARCH_ENDPOINT=$(aws opensearchserverless get-collection \
        --name ${COLLECTION_NAME} \
        --region ${AWS_REGION} \
        --query 'collectionDetail.collectionEndpoint' \
        --output text)
    
    echo "export OPENSEARCH_ENDPOINT=${OPENSEARCH_ENDPOINT}" >> .env
    echo "export OPENSEARCH_COLLECTION_ID=${COLLECTION_NAME}" >> .env
    
    # Clean up policy files
    rm -f encryption-policy.json network-policy.json data-policy.json
    
    echo -e "${GREEN}✅ OpenSearch Serverless collection created${NC}"
}

# Create IAM roles and policies
create_iam_resources() {
    echo -e "${YELLOW}🔐 Creating IAM roles and policies...${NC}"
    
    # Create trust policy for Lambda/Bedrock
    cat > lambda-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
    
    # Create trust policy for EKS
    cat > eks-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/oidc.eks.${AWS_REGION}.amazonaws.com/id/$(aws eks describe-cluster --name ${PROJECT_NAME}-cluster --region ${AWS_REGION} --query 'cluster.identity.oidc.issuer' --output text | cut -d'/' -f5)"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "oidc.eks.${AWS_REGION}.amazonaws.com/id/$(aws eks describe-cluster --name ${PROJECT_NAME}-cluster --region ${AWS_REGION} --query 'cluster.identity.oidc.issuer' --output text | cut -d'/' -f5):sub": "system:serviceaccount:nfrguard-agents:nfrguard-sa",
          "oidc.eks.${AWS_REGION}.amazonaws.com/id/$(aws eks describe-cluster --name ${PROJECT_NAME}-cluster --region ${AWS_REGION} --query 'cluster.identity.oidc.issuer' --output text | cut -d'/' -f5):aud": "sts.amazonaws.com"
        }
      }
    }
  ]
}
EOF
    
    # Create agent role
    aws iam create-role \
        --role-name ${PROJECT_NAME}-agent-role \
        --assume-role-policy-document file://eks-trust-policy.json \
        --region ${AWS_REGION}
    
    # Attach policies to agent role
    aws iam attach-role-policy \
        --role-name ${PROJECT_NAME}-agent-role \
        --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
    
    aws iam attach-role-policy \
        --role-name ${PROJECT_NAME}-agent-role \
        --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
    
    aws iam attach-role-policy \
        --role-name ${PROJECT_NAME}-agent-role \
        --policy-arn arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess
    
    aws iam attach-role-policy \
        --role-name ${PROJECT_NAME}-agent-role \
        --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
    
    echo -e "${GREEN}✅ IAM roles and policies created${NC}"
}

# Create EKS cluster
create_eks_cluster() {
    echo -e "${YELLOW}☸️ Creating EKS cluster...${NC}"
    
    ${EKSCTL_CMD} create cluster \
        --name ${PROJECT_NAME}-cluster \
        --region ${AWS_REGION} \
        --nodegroup-name standard-workers \
        --node-type t3.medium \
        --nodes 2 \
        --nodes-min 1 \
        --nodes-max 3 \
        --managed \
        --with-oidc \
        --ssh-access \
        --spot \
        --ssh-public-key $(aws ec2 describe-key-pairs --query 'KeyPairs[0].KeyName' --output text 2>/dev/null || echo "default")
    
    # Update kubeconfig
    aws eks update-kubeconfig \
        --region ${AWS_REGION} \
        --name ${PROJECT_NAME}-cluster
    
    echo -e "${GREEN}✅ EKS cluster created${NC}"
}

# Set up IRSA (IAM Roles for Service Accounts)
setup_irsa() {
    echo -e "${YELLOW}🔗 Setting up IRSA...${NC}"
    
    ${EKSCTL_CMD} create iamserviceaccount \
        --name nfrguard-sa \
        --namespace nfrguard-agents \
        --cluster ${PROJECT_NAME}-cluster \
        --role-name ${PROJECT_NAME}-agent-role \
        --attach-policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess \
        --attach-policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess \
        --attach-policy-arn arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess \
        --attach-policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess \
        --approve \
        --region ${AWS_REGION}
    
    echo -e "${GREEN}✅ IRSA configured${NC}"
}

# Create ECR repositories
create_ecr_repositories() {
    echo -e "${YELLOW}🐳 Creating ECR repositories...${NC}"
    
    AGENTS=("transaction-risk" "compliance" "resilience" "customer-sentiment" "data-privacy" "knowledge" "banking-assistant")
    
    for agent in "${AGENTS[@]}"; do
        aws ecr create-repository \
            --repository-name ${agent}-agent \
            --region ${AWS_REGION} || true
    done
    
    echo -e "${GREEN}✅ ECR repositories created${NC}"
}

# Request Bedrock model access
request_bedrock_access() {
    echo -e "${YELLOW}🤖 Requesting Bedrock model access...${NC}"
    
    echo "Please go to AWS Console and request access to:"
    echo "- Anthropic Claude 3.5 Sonnet"
    echo "- Amazon Titan Text Embeddings V2"
    echo ""
    echo "URL: https://console.aws.amazon.com/bedrock/home?region=${AWS_REGION}#/modelaccess"
    echo ""
    read -p "Press Enter after requesting model access..."
    
    echo -e "${GREEN}✅ Bedrock model access requested${NC}"
}

# Main execution
main() {
    echo -e "${GREEN}Starting AWS infrastructure setup...${NC}"
    
    # Create .env file
    echo "# AWS Infrastructure Configuration" > .env
    echo "export AWS_REGION=${AWS_REGION}" >> .env
    echo "export AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}" >> .env
    echo "export PROJECT_NAME=${PROJECT_NAME}" >> .env
    
    check_prerequisites
    create_s3_buckets
    create_dynamodb_tables
    create_eventbridge
    # create_opensearch  # Skip for now - requires complex policies
    create_iam_resources
    create_eks_cluster
    setup_irsa
    create_ecr_repositories
    request_bedrock_access
    
    echo -e "${GREEN}🎉 AWS infrastructure setup completed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Source the environment file: source .env"
    echo "2. Build and push Docker images: ./scripts/build_and_push_images.sh"
    echo "3. Deploy agents to EKS: ./scripts/deploy_to_eks.sh"
    echo ""
    echo "Environment variables saved to .env file"
}

# Run main function
main "$@"
