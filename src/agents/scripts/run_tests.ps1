# Run AWS Integration Tests
# Windows PowerShell version

$ErrorActionPreference = "Stop"

# Colors for output
$RED = "Red"
$GREEN = "Green"
$YELLOW = "Yellow"

Write-Host "🧪 Running AWS Integration Tests" -ForegroundColor $GREEN

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor $YELLOW
    python -m venv venv
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor $YELLOW
& "venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor $YELLOW
pip install -r requirements_aws.txt

# Set test environment variables
$env:AWS_REGION = "ap-southeast-2"
$env:BEDROCK_MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"
$env:BEDROCK_EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"
$env:S3_BUCKET_NAME = "test-bucket"
$env:OPENSEARCH_ENDPOINT = "test-endpoint"
$env:EVENT_BUS_NAME = "test-event-bus"
$env:USE_AWS_MESSAGING = "false"  # Use local mode for tests

# Run tests
Write-Host "🧪 Running tests..." -ForegroundColor $YELLOW
python tests/test_aws_integration.py

# Run specific test suites
Write-Host "🧪 Running Bedrock Agent tests..." -ForegroundColor $YELLOW
python -m pytest tests/test_aws_integration.py::TestBedrockAgent -v

Write-Host "🧪 Running AWS Messaging tests..." -ForegroundColor $YELLOW
python -m pytest tests/test_aws_integration.py::TestAWSMessaging -v

Write-Host "🧪 Running S3 Storage tests..." -ForegroundColor $YELLOW
python -m pytest tests/test_aws_integration.py::TestS3Storage -v

Write-Host "🧪 Running RAG Engine tests..." -ForegroundColor $YELLOW
python -m pytest tests/test_aws_integration.py::TestAWSRAGEngine -v

Write-Host "🧪 Running Integration tests..." -ForegroundColor $YELLOW
python -m pytest tests/test_aws_integration.py::TestAgentIntegration -v

Write-Host "✅ All tests completed successfully!" -ForegroundColor $GREEN


