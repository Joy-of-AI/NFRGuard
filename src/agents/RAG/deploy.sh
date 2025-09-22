#!/bin/bash

# RAG System Production Deployment Script
# This script deploys the complete RAG system to production

set -e  # Exit on any error

echo "🚀 RAG System Production Deployment"
echo "=================================="

# Check if required environment variables are set
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "❌ Error: GOOGLE_CLOUD_PROJECT environment variable not set"
    echo "   Please set it with: export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "❌ Error: GOOGLE_APPLICATION_CREDENTIALS environment variable not set"
    echo "   Please set it with: export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json"
    exit 1
fi

echo "✅ Environment variables configured"
echo "   Project ID: $GOOGLE_CLOUD_PROJECT"
echo "   Service Account: $GOOGLE_APPLICATION_CREDENTIALS"

# Step 1: Validate configuration
echo ""
echo "🔍 Step 1: Validating configuration..."
python production_config.py
if [ $? -ne 0 ]; then
    echo "❌ Configuration validation failed"
    exit 1
fi
echo "✅ Configuration validation passed"

# Step 2: Deploy vector search infrastructure
echo ""
echo "🏗️  Step 2: Deploying vector search infrastructure..."
python deploy_production.py
if [ $? -ne 0 ]; then
    echo "❌ Vector search deployment failed"
    exit 1
fi
echo "✅ Vector search infrastructure deployed"

# Step 3: Load deployment info
echo ""
echo "📝 Step 3: Loading deployment information..."
if [ ! -f "deployment_info.json" ]; then
    echo "❌ Deployment info file not found"
    exit 1
fi

# Extract deployment info
INDEX_ID=$(python -c "import json; print(json.load(open('deployment_info.json'))['index_id'])")
ENDPOINT_ID=$(python -c "import json; print(json.load(open('deployment_info.json'))['endpoint_id'])")
DEPLOYED_INDEX_ID=$(python -c "import json; print(json.load(open('deployment_info.json'))['deployed_index_id'])")

echo "   Vector Index ID: $INDEX_ID"
echo "   Vector Endpoint ID: $ENDPOINT_ID"
echo "   Deployed Index ID: $DEPLOYED_INDEX_ID"

# Step 4: Update Kubernetes configuration
echo ""
echo "🔧 Step 4: Updating Kubernetes configuration..."
sed -i.bak "s/your-project-id/$GOOGLE_CLOUD_PROJECT/g" k8s/agents-rag.yaml
sed -i.bak "s/your-index-id/$INDEX_ID/g" k8s/agents-rag.yaml
sed -i.bak "s/your-endpoint-id/$ENDPOINT_ID/g" k8s/agents-rag.yaml
echo "✅ Kubernetes configuration updated"

# Step 5: Create service account secret
echo ""
echo "🔐 Step 5: Creating service account secret..."
kubectl create namespace nfrguard-agents --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic google-service-account \
  --from-file=key.json="$GOOGLE_APPLICATION_CREDENTIALS" \
  --namespace=nfrguard-agents \
  --dry-run=client -o yaml | kubectl apply -f -
echo "✅ Service account secret created"

# Step 6: Deploy agents
echo ""
echo "🚀 Step 6: Deploying RAG-enhanced agents..."
kubectl apply -f k8s/agents-rag.yaml
if [ $? -ne 0 ]; then
    echo "❌ Agent deployment failed"
    exit 1
fi
echo "✅ RAG-enhanced agents deployed"

# Step 7: Wait for deployment
echo ""
echo "⏳ Step 7: Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/transaction-risk-agent -n nfrguard-agents
kubectl wait --for=condition=available --timeout=300s deployment/compliance-agent -n nfrguard-agents
kubectl wait --for=condition=available --timeout=300s deployment/resilience-agent -n nfrguard-agents
kubectl wait --for=condition=available --timeout=300s deployment/customer-sentiment-agent -n nfrguard-agents
kubectl wait --for=condition=available --timeout=300s deployment/data-privacy-agent -n nfrguard-agents
kubectl wait --for=condition=available --timeout=300s deployment/knowledge-agent -n nfrguard-agents
kubectl wait --for=condition=available --timeout=300s deployment/banking-assistant-agent -n nfrguard-agents
echo "✅ All agents are ready"

# Step 8: Run health check
echo ""
echo "🏥 Step 8: Running health check..."
python monitor_production.py
if [ $? -ne 0 ]; then
    echo "⚠️  Health check failed - system may need attention"
else
    echo "✅ Health check passed"
fi

# Step 9: Display deployment summary
echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "📊 Deployment Summary:"
echo "   Project ID: $GOOGLE_CLOUD_PROJECT"
echo "   Vector Index: $INDEX_ID"
echo "   Vector Endpoint: $ENDPOINT_ID"
echo "   Deployed Index: $DEPLOYED_INDEX_ID"
echo "   Namespace: nfrguard-agents"
echo ""
echo "🔍 Check deployment status:"
echo "   kubectl get pods -n nfrguard-agents"
echo "   kubectl get services -n nfrguard-agents"
echo ""
echo "📊 Monitor the system:"
echo "   python monitor_production.py"
echo "   kubectl logs -f deployment/transaction-risk-agent -n nfrguard-agents"
echo ""
echo "🌐 Access the system:"
echo "   Bank of Anthos: http://34.40.211.236"
echo "   Monitoring: https://console.cloud.google.com/monitoring"
echo ""
echo "✅ RAG system is now production-ready!"

# Clean up backup files
rm -f k8s/agents-rag.yaml.bak

echo ""
echo "🎯 Next Steps:"
echo "   1. Monitor the system using the provided monitoring tools"
echo "   2. Set up automated document updates (daily cron job)"
echo "   3. Configure alerting for production issues"
echo "   4. Scale the system based on traffic patterns"
echo "   5. Update regulatory documents as needed"
