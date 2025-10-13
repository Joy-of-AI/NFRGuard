#!/bin/bash
# Setup Amazon OpenSearch Serverless for RAG System

set -e

echo "🔍 Setting up Amazon OpenSearch Serverless for RAG"
echo ""

# Configuration
COLLECTION_NAME="banking-regulations"
REGION=${AWS_DEFAULT_REGION:-ap-southeast-2}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "📋 Configuration:"
echo "  Collection: $COLLECTION_NAME"
echo "  Region: $REGION"
echo "  Account: $ACCOUNT_ID"
echo ""

# Step 1: Create network policy
echo "📡 Creating network policy..."
aws opensearchserverless create-security-policy \
  --name "${COLLECTION_NAME}-network" \
  --type network \
  --policy "[{\"Rules\":[{\"Resource\":[\"collection/${COLLECTION_NAME}\"],\"ResourceType\":\"collection\"}],\"AllowFromPublic\":true}]" \
  --region $REGION 2>/dev/null || echo "Network policy already exists"

# Step 2: Create encryption policy
echo "🔐 Creating encryption policy..."
aws opensearchserverless create-security-policy \
  --name "${COLLECTION_NAME}-encryption" \
  --type encryption \
  --policy "{\"Rules\":[{\"Resource\":[\"collection/${COLLECTION_NAME}\"],\"ResourceType\":\"collection\"}],\"AWSOwnedKey\":true}" \
  --region $REGION 2>/dev/null || echo "Encryption policy already exists"

# Step 3: Create data access policy
echo "🔑 Creating data access policy..."
cat > /tmp/data-access-policy.json <<EOF
[
  {
    "Rules": [
      {
        "Resource": [
          "collection/${COLLECTION_NAME}"
        ],
        "Permission": [
          "aoss:CreateCollectionItems",
          "aoss:DeleteCollectionItems",
          "aoss:UpdateCollectionItems",
          "aoss:DescribeCollectionItems"
        ],
        "ResourceType": "collection"
      },
      {
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
        ],
        "ResourceType": "index"
      }
    ],
    "Principal": [
      "arn:aws:iam::${ACCOUNT_ID}:user/AWS_Acct",
      "arn:aws:iam::${ACCOUNT_ID}:role/eksctl-fintech-ai-aws-cluster-node*"
    ],
    "Description": "Data access for banking regulations collection"
  }
]
EOF

aws opensearchserverless create-access-policy \
  --name "${COLLECTION_NAME}-access" \
  --type data \
  --policy file:///tmp/data-access-policy.json \
  --region $REGION 2>/dev/null || echo "Data access policy already exists"

# Step 4: Create collection
echo "☁️ Creating OpenSearch Serverless collection..."
COLLECTION_OUTPUT=$(aws opensearchserverless create-collection \
  --name "$COLLECTION_NAME" \
  --type VECTORSEARCH \
  --region $REGION 2>&1) || {
    if echo "$COLLECTION_OUTPUT" | grep -q "ConflictException"; then
        echo "Collection already exists"
    else
        echo "Error creating collection: $COLLECTION_OUTPUT"
        exit 1
    fi
}

# Step 5: Wait for collection to be active
echo "⏳ Waiting for collection to be active (takes ~5 minutes)..."
for i in {1..60}; do
    STATUS=$(aws opensearchserverless batch-get-collection \
        --names "$COLLECTION_NAME" \
        --region $REGION \
        --query 'collectionDetails[0].status' \
        --output text 2>/dev/null || echo "PENDING")
    
    if [ "$STATUS" == "ACTIVE" ]; then
        echo "✅ Collection is active!"
        break
    fi
    
    echo "  Status: $STATUS (attempt $i/60)"
    sleep 5
done

# Step 6: Get collection endpoint
echo ""
echo "📍 Getting collection endpoint..."
ENDPOINT=$(aws opensearchserverless batch-get-collection \
    --names "$COLLECTION_NAME" \
    --region $REGION \
    --query 'collectionDetails[0].collectionEndpoint' \
    --output text)

echo "✅ Collection endpoint: $ENDPOINT"

# Step 7: Create vector index
echo ""
echo "🔢 Creating vector index..."
cat > /tmp/index-mapping.json <<EOF
{
  "settings": {
    "index": {
      "knn": true,
      "knn.algo_param.ef_search": 512
    }
  },
  "mappings": {
    "properties": {
      "content": {
        "type": "text"
      },
      "embedding": {
        "type": "knn_vector",
        "dimension": 768,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil",
          "engine": "nmslib",
          "parameters": {
            "ef_construction": 512,
            "m": 16
          }
        }
      },
      "metadata": {
        "properties": {
          "title": { "type": "keyword" },
          "regulator": { "type": "keyword" },
          "document_type": { "type": "keyword" },
          "agent_focus": { "type": "keyword" },
          "chunk_index": { "type": "integer" }
        }
      }
    }
  }
}
EOF

# Note: Index creation via AWS CLI is not directly supported
# Index will be created when first document is uploaded via Python SDK

# Step 8: Update environment variables
echo ""
echo "📝 Updating Kubernetes ConfigMap with OpenSearch endpoint..."
kubectl create configmap opensearch-config \
  --from-literal=OPENSEARCH_ENDPOINT="$ENDPOINT" \
  --from-literal=OPENSEARCH_REGION="$REGION" \
  --from-literal=OPENSEARCH_INDEX="banking-regulations" \
  -n nfrguard-agents \
  --dry-run=client -o yaml | kubectl apply -f -

echo ""
echo "✅ OpenSearch Serverless setup complete!"
echo ""
echo "📋 Summary:"
echo "  Collection: $COLLECTION_NAME"
echo "  Endpoint: $ENDPOINT"
echo "  Region: $REGION"
echo "  Index: banking-regulations"
echo ""
echo "🔜 Next steps:"
echo "  1. Request Bedrock Titan Embeddings access"
echo "  2. Run: python RAG/aws_rag_engine.py --index-documents"
echo "  3. Deploy RAG-enhanced agents"
echo ""

