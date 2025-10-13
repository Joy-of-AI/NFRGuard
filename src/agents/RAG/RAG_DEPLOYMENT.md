# 🚀 RAG System Deployment Guide

**Complete guide to deploy RAG system with Amazon OpenSearch Serverless + AWS Bedrock**

---

## ✅ **Prerequisites Checklist**

- [x] EKS cluster running (`fintech-ai-aws-cluster`)
- [x] AWS CLI configured
- [x] kubectl connected to cluster
- [x] Claude 3.5 Sonnet access (already have)
- [ ] **Titan Embeddings V2 access** (need to request)
- [ ] **OpenSearch Serverless** (will create)

---

## 🚀 **Step-by-Step Deployment**

### **Step 1: Request Bedrock Titan Embeddings Access**

**Manual Step Required:**

1. Go to: https://console.aws.amazon.com/bedrock/
2. Navigate to: **Model Access**
3. Request access to:
   - ✅ `anthropic.claude-3-5-sonnet-20240620-v1:0` (already have)
   - ⏳ `amazon.titan-embed-text-v2:0` ← **REQUEST THIS**
4. Wait for approval (usually instant to few minutes)

**Verify access:**
```bash
aws bedrock list-foundation-models --region us-east-1 \
  --query 'modelSummaries[?modelId==`amazon.titan-embed-text-v2:0`]'
```

---

### **Step 2: Create OpenSearch Serverless Collection**

**Run the setup script:**

```bash
cd /d/Joy_of_AI/Fintech_AI_AWS/bank-of-anthos/src/agents

bash scripts/setup_opensearch.sh
```

**What this creates:**
- ✅ OpenSearch Serverless collection: `banking-regulations`
- ✅ Network policy (public access)
- ✅ Encryption policy (AWS managed keys)
- ✅ Data access policy (IAM permissions)
- ✅ Vector index configuration (768-dim, k-NN)

**Time**: ~5-7 minutes (collection activation)

**Expected Output:**
```
✅ OpenSearch Serverless setup complete!

📋 Summary:
  Collection: banking-regulations
  Endpoint: xxxxxx.ap-southeast-2.aoss.amazonaws.com
  Region: ap-southeast-2
  Index: banking-regulations
```

**Save the endpoint URL** - you'll need it!

---

### **Step 3: Update IAM Permissions**

**Add OpenSearch permissions to node role:**

```bash
# Get node role name
NODE_ROLE=$(aws iam list-roles --query "Roles[?contains(RoleName, 'fintech-ai-aws-cluster-node-NodeInstanceRole')].RoleName" --output text)

echo "Node role: $NODE_ROLE"

# Create custom OpenSearch policy
cat > /tmp/opensearch-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "aoss:APIAccessAll"
            ],
            "Resource": "arn:aws:aoss:*:*:collection/*"
        }
    ]
}
EOF

# Create and attach policy
aws iam create-policy \
  --policy-name OpenSearchServerlessAccess \
  --policy-document file:///tmp/opensearch-policy.json \
  --description "Access to OpenSearch Serverless for RAG" 2>/dev/null || echo "Policy exists"

aws iam attach-role-policy \
  --role-name $NODE_ROLE \
  --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/OpenSearchServerlessAccess
```

**Verify:**
```bash
aws iam list-attached-role-policies --role-name $NODE_ROLE
```

---

### **Step 4: Index Documents to OpenSearch**

**Upload 42 regulatory documents:**

```bash
cd /d/Joy_of_AI/Fintech_AI_AWS/bank-of-anthos/src/agents/RAG

# Set OpenSearch endpoint (from Step 2)
export OPENSEARCH_ENDPOINT="xxxxxx.ap-southeast-2.aoss.amazonaws.com"

# Index all documents
python index_documents.py
```

**What happens:**
1. Reads 42 JSON documents
2. Chunks each document (1000 chars, 200 overlap)
3. Generates embeddings using Titan (768-dim vectors)
4. Uploads chunks + embeddings to OpenSearch
5. Creates searchable index

**Time**: ~5-10 minutes (embedding generation)

**Expected Output:**
```
📚 Indexing 42 regulatory documents...
✅ ASIC guidance: 7 documents, 143 chunks
✅ APRA standards: 7 documents, 156 chunks
✅ APRA practice guides: 7 documents, 189 chunks
✅ AUSTRAC obligations: 7 documents, 134 chunks
✅ AFCA rules: 7 documents, 128 chunks
✅ AFCA guidelines: 7 documents, 145 chunks

✅ Total: 42 documents, 895 chunks indexed
```

---

### **Step 5: Deploy RAG-Enhanced Agents**

**Replace simple agents with RAG-enhanced versions:**

```bash
cd /d/Joy_of_AI/Fintech_AI_AWS/bank-of-anthos/src/agents

# Deploy RAG-enhanced agents
bash scripts/deploy_rag_agents.sh
```

**What changes:**
- Agents now use RAG engine for regulatory queries
- Responses include citations
- Better accuracy on compliance questions

**Time**: ~2 minutes

---

### **Step 6: Test RAG System**

**Test with regulatory questions:**

```bash
# Test Compliance Agent with RAG
kubectl port-forward -n nfrguard-agents svc/compliance-agent 8082:8080
```

In another terminal:
```bash
# Query about APRA CPS 230
curl -X POST http://localhost:8082/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the key requirements of APRA CPS 230 for operational resilience?"}'

# Query about AUSTRAC
curl -X POST http://localhost:8082/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain AUSTRAC transaction monitoring obligations for banks"}'

# Query about AFCA
curl -X POST http://localhost:8082/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the timeframe requirements for AFCA complaint handling?"}'
```

**Expected**: Detailed answers with specific citations from regulatory documents!

---

## 📊 **Verify Deployment**

**Check OpenSearch:**
```bash
# List collections
aws opensearchserverless list-collections --region ap-southeast-2

# Check collection status
aws opensearchserverless batch-get-collection \
  --names banking-regulations \
  --region ap-southeast-2
```

**Check Agents:**
```bash
# All agents should be running
kubectl get pods -n nfrguard-agents

# Check agent logs for RAG initialization
kubectl logs -n nfrguard-agents deployment/compliance-agent | grep -i "rag\|opensearch\|embedding"
```

---

##  🔧 **Troubleshooting**

### **Issue: Titan Embeddings Access Denied**

```bash
# Request model access in Bedrock console
# Then verify:
aws bedrock get-foundation-model \
  --model-identifier amazon.titan-embed-text-v2:0 \
  --region us-east-1
```

### **Issue: OpenSearch Connection Failed**

```bash
# Check collection is active
aws opensearchserverless batch-get-collection \
  --names banking-regulations \
  --region ap-southeast-2 \
  --query 'collectionDetails[0].status'

# Verify network policy
aws opensearchserverless get-security-policy \
  --name banking-regulations-network \
  --type network \
  --region ap-southeast-2
```

### **Issue: IAM Permissions Denied**

```bash
# Verify node role has policies
NODE_ROLE=$(aws iam list-roles --query "Roles[?contains(RoleName, 'fintech-ai-aws-cluster-node')].RoleName" --output text)

aws iam list-attached-role-policies --role-name $NODE_ROLE

# Should see:
# - AmazonBedrockFullAccess
# - OpenSearchServerlessAccess
```

---

## 💰 **Cost Breakdown**

| Component | Cost | Frequency |
|-----------|------|-----------|
| **OpenSearch Collection** | ~$0.24/OCU-hour | Continuous |
| **Minimum OCUs** | 2 (search) + 2 (indexing) = 4 | Required |
| **Base Cost** | 4 × $0.24 = $0.96/hour | ~$700/month |
| **Titan Embeddings** | $0.0001/1K tokens | One-time indexing |
| **Query Embeddings** | $0.0001/1K tokens | Per query |
| **Claude** | Same as before | No change |

**Total Additional**: ~$700/month for production RAG

**Note**: OpenSearch Serverless minimum is expensive. For development, consider:
- Using OpenSearch on EC2 (cheaper)
- Pausing/deleting when not in use
- Using mock RAG for testing

---

## 🎯 **What You Get with RAG**

**Before (Simple Agents):**
```
Q: "What are CPS 230 requirements?"
A: "CPS 230 covers operational risk management..."
   (Generic, no citations)
```

**After (RAG-Enhanced):**
```
Q: "What are CPS 230 requirements?"
A: "According to APRA CPS 230 (Operational Risk Management):
   
   1. Maintain operational resilience
   2. Identify critical operations
   3. Set tolerance levels
   4. Test resilience regularly
   5. Document recovery plans
   
   Source: APRA CPS 230, Section 2.1-2.5
   Retrieved from: apra_standard_1758505131.json"
   
   (Specific, with citations, auditable)
```

---

## 📝 **Post-Deployment**

**Update agent environment:**
```bash
# Set OpenSearch endpoint for all agents
kubectl set env deployment -n nfrguard-agents --all \
  OPENSEARCH_ENDPOINT="xxxxxx.ap-southeast-2.aoss.amazonaws.com" \
  OPENSEARCH_REGION="ap-southeast-2" \
  USE_RAG="true"

# Restart agents
kubectl rollout restart deployment -n nfrguard-agents
```

**Monitor performance:**
```bash
# Check query latency
kubectl logs -n nfrguard-agents deployment/compliance-agent | grep "RAG query"

# Check retrieval accuracy
kubectl logs -n nfrguard-agents deployment/transaction-risk-agent | grep "Retrieved.*chunks"
```

---

## 🎊 **Summary**

| Step | Time | Cost | Status |
|------|------|------|--------|
| 1. Request Titan access | 1 min | $0 | Manual |
| 2. Create OpenSearch | 7 min | ~$700/mo | Automated |
| 3. IAM permissions | 2 min | $0 | Automated |
| 4. Index documents | 10 min | ~$1 one-time | Automated |
| 5. Deploy agents | 2 min | $0 | Automated |
| 6. Test system | 5 min | $0 | Manual |

**Total Time**: ~30 minutes  
**Additional Cost**: ~$700/month (OpenSearch)

---

**For Development**: Consider mock RAG or pause OpenSearch when not testing  
**For Production**: Full RAG deployment as described above

---

**Next**: Create `index_documents.py` script...

