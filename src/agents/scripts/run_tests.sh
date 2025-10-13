#!/bin/bash
# Run AWS Integration Tests
# This script runs comprehensive tests for all AWS components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Running AWS Integration Tests${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pip install -r requirements_aws.txt

# Set test environment variables
export AWS_REGION="us-east-1"
export BEDROCK_MODEL_ID="anthropic.claude-3-5-sonnet-20241022-v2:0"
export BEDROCK_EMBEDDING_MODEL="amazon.titan-embed-text-v2:0"
export S3_BUCKET_NAME="test-bucket"
export OPENSEARCH_ENDPOINT="test-endpoint"
export EVENT_BUS_NAME="test-event-bus"
export USE_AWS_MESSAGING="false"  # Use local mode for tests

# Run tests
echo -e "${YELLOW}🧪 Running tests...${NC}"
python tests/test_aws_integration.py

# Run specific test suites
echo -e "${YELLOW}🧪 Running Bedrock Agent tests...${NC}"
python -m pytest tests/test_aws_integration.py::TestBedrockAgent -v

echo -e "${YELLOW}🧪 Running AWS Messaging tests...${NC}"
python -m pytest tests/test_aws_integration.py::TestAWSMessaging -v

echo -e "${YELLOW}🧪 Running S3 Storage tests...${NC}"
python -m pytest tests/test_aws_integration.py::TestS3Storage -v

echo -e "${YELLOW}🧪 Running RAG Engine tests...${NC}"
python -m pytest tests/test_aws_integration.py::TestAWSRAGEngine -v

echo -e "${YELLOW}🧪 Running Integration tests...${NC}"
python -m pytest tests/test_aws_integration.py::TestAgentIntegration -v

echo -e "${GREEN}✅ All tests completed successfully!${NC}"



