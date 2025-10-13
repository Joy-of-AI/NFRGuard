# 🧠 RAG System for Australian Banking Regulations

This directory contains a complete **Retrieval-Augmented Generation (RAG)** system that provides AI agents with access to Australian banking regulatory documents. The system uses **Amazon OpenSearch Serverless** for vector storage and **AWS Bedrock Titan Embeddings** for document retrieval, enabling agents to make fact-based decisions with regulatory citations.

---

## 🚀 **Deployment Status**

### **✅ Available (Code Ready)**
- **EKS Cluster**: `fintech-ai-aws-cluster` (ap-southeast-2)
- **Namespace**: `nfrguard-agents`
- **AI Model**: Claude 3.5 Sonnet (AWS Bedrock)
- **Embeddings**: Titan Embeddings V2 (768 dimensions)
- **Documents**: 42 Australian regulatory documents
- **Agents**: 7 agents ready for RAG integration

### **⏳ Deployment Required**
- [ ] Amazon OpenSearch Serverless collection
- [ ] Request Bedrock Titan Embeddings access
- [ ] Index 42 documents with embeddings
- [ ] Deploy RAG-enhanced agents
- [ ] IAM permissions for OpenSearch

---

## 📚 **42 Regulatory Documents**

### **Document Categories:**

| Regulator | Acronym | Documents | Focus Area |
|-----------|---------|-----------|------------|
| Australian Securities & Investments Commission | **ASIC** | 7 | Financial services, consumer protection |
| Australian Prudential Regulation Authority | **APRA** | 14 | Prudential standards + practice guides |
| Australian Transaction Reports & Analysis Centre | **AUSTRAC** | 7 | AML/CTF, transaction monitoring |
| Australian Financial Complaints Authority | **AFCA** | 14 | Rules + guidelines for disputes |

**Total**: 42 documents covering all major Australian banking regulations

### **Key Documents:**

**APRA CPS 230**: Operational Risk Management (Critical Infrastructure Resilience)  
**APRA CPS 234**: Information Security  
**AUSTRAC AML/CTF**: Anti-Money Laundering & Counter-Terrorism Financing  
**AFCA Rules**: Complaint handling and dispute resolution  

**Location**: `RAG/documents/*.json` (42 files)

---

## 🏗️ **AWS RAG Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                  RAG System - AWS Stack                      │
└─────────────────────────────────────────────────────────────┘

42 Regulatory Documents (JSON)
         ↓
┌──────────────────────────┐
│  Document Processor      │  ← Chunks: 1000 chars, 200 overlap
│  (Python)                │     Metadata: regulator, type, sections
└──────────────────────────┘
         ↓
┌──────────────────────────┐
│  AWS Bedrock             │  ← Titan Embeddings V2
│  Titan Embeddings        │     Model: amazon.titan-embed-text-v2:0
│                          │     Output: 768-dimensional vectors
└──────────────────────────┘
         ↓
┌──────────────────────────┐
│  Amazon OpenSearch       │  ← Vector Database
│  Serverless              │     k-NN search (cosine similarity)
│                          │     Metadata filtering
│                          │     Auto-scaling
└──────────────────────────┘
         ↓
┌──────────────────────────┐
│  RAG Engine              │  ← Query orchestration
│  (aws_rag_engine.py)     │     Top-k retrieval
│                          │     Context assembly
└──────────────────────────┘
         ↓
┌──────────────────────────┐
│  AWS Bedrock             │  ← Claude 3.5 Sonnet
│  Claude 3.5 Sonnet       │     Generates answers with citations
│                          │     Context-aware responses
└──────────────────────────┘
```

---

## 🔧 **Components Explained**

### **1. AWS RAG Wrapper (`aws_rag_engine.py`)**

**Purpose**: Integrates AWS services for RAG functionality

**Key Classes:**

**a) BedrockEmbeddings**
- Converts text → 768-dim vectors
- Model: `amazon.titan-embed-text-v2:0`
- Used for both documents and queries

**b) OpenSearchVectorStore**
- Manages OpenSearch Serverless collection
- Stores document chunks + embeddings
- Performs k-NN similarity search
- Filters by metadata (regulator, agent focus)

**c) AWSRAGEngine**
- Main orchestrator
- Methods:
  - `initialize()` - Setup connections
  - `index_documents()` - Upload docs with embeddings
  - `search()` - Find relevant chunks
  - `query()` - Complete RAG pipeline

---

### **2. Document Processor**

**Chunking Strategy:**
- **Size**: 1000 characters per chunk
- **Overlap**: 200 characters (maintains context)
- **Smart Breaking**: Breaks at sentence boundaries

**Metadata Captured:**
- Regulator (ASIC, APRA, AUSTRAC, AFCA)
- Document type (standard, guideline, rule)
- Sections covered
- Agent focus (which agents need this doc)
- Relevance score

**Why Chunking?**
- OpenSearch works best with smaller text segments
- Embeddings are more precise for specific topics
- Retrieves exact relevant sections, not entire documents

---

### **3. k-NN Search**

**Algorithm**: k-Nearest Neighbors  
**Similarity**: Cosine similarity  
**Why k-NN (not ANN)?**

| Aspect | k-NN | ANN |
|--------|------|-----|
| **Accuracy** | 100% exact | ~98-99% approximate |
| **Speed (42 docs)** | Fast enough | Overkill |
| **Complexity** | Simple | Complex indexing |
| **Best for** | Small datasets (<10K docs) | Large datasets (>100K docs) |
| **Our choice** | ✅ k-NN | Later if needed |

**Decision**: Use k-NN for now. Switch to ANN when document count exceeds 10,000.

---

## 🚀 **Deploy RAG System**

### **Step 1: Request Bedrock Titan Access**

1. Go to: https://console.aws.amazon.com/bedrock/
2. Model Access → Request access
3. Select: `amazon.titan-embed-text-v2:0`
4. Wait for approval (~few minutes)

---

### **Step 2: Create OpenSearch Serverless Collection**

See: `scripts/setup_opensearch.sh` (created next)

---

### **Step 3: Index Documents**

```bash
cd /d/Joy_of_AI/Fintech_AI_AWS/bank-of-anthos/src/agents/RAG

# Index all 42 documents
python aws_rag_engine.py --index-documents

# Verify indexing
python aws_rag_engine.py --verify
```

---

### **Step 4: Deploy RAG-Enhanced Agents**

```bash
# Deploy RAG-enhanced agents (replaces simple agents)
bash ../scripts/deploy_rag_agents.sh
```

---

### **Step 5: Test RAG System**

```bash
# Test regulatory query
kubectl port-forward -n nfrguard-agents svc/compliance-agent 8082:8080

curl -X POST http://localhost:8082/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are APRA CPS 230 requirements for operational resilience?"}'
```

**Expected Response**: Answer with citations from APRA standards

---

## 📁 **File Structure**

```
RAG/
├── README.md                    # This file
├── aws_rag_engine.py            # AWS RAG wrapper ⭐
├── rag_engine_aws.py            # RAG orchestrator
├── rag_enhanced_agents.py       # Agents with RAG
├── document_downloader.py       # Document fetcher
├── requirements.txt             # Python dependencies
├── documents/                   # 42 regulatory docs
│   ├── asic_guidance_*.json     (7 files)
│   ├── apra_standard_*.json     (7 files)
│   ├── apra_practice_guide_*.json (7 files)
│   ├── austrac_obligations_*.json (7 files)
│   ├── afca_rules_*.json        (7 files)
│   └── afca_guideline_*.json    (7 files)
├── k8s/                         # Kubernetes configs
│   ├── agents-rag.yaml          # RAG agent deployment
│   └── hpa-config.yaml          # Auto-scaling
└── test/                        # Test suite
    ├── test_rag_engine.py
    ├── test_rag_enhanced_agents.py
    └── run_tests.py
```

---

## 🎯 **Why Use RAG?**

### **Without RAG (Current Simple Agents):**
```
User: "What are CPS 230 requirements?"
    ↓
Claude: "CPS 230 generally covers operational risk..."
    ↓
Result: ❌ Generic answer, no citations, may be inaccurate
```

### **With RAG (Enhanced Agents):**
```
User: "What are CPS 230 requirements?"
    ↓
Query embedding (Titan)
    ↓
OpenSearch finds relevant chunks from APRA CPS 230
    ↓
Claude + Retrieved context
    ↓
Result: ✅ Specific answer with exact CPS 230 citations
```

**Benefits:**
- ✅ **Accurate**: Answers based on actual regulations
- ✅ **Citations**: Source attribution for compliance
- ✅ **Current**: Documents can be updated
- ✅ **Auditable**: Trace answers to source documents
- ✅ **Compliant**: Legal requirements met

---

## 💰 **Cost Estimate (When Deployed)**

| Component | Cost | Notes |
|-----------|------|-------|
| **OpenSearch Serverless** | ~$50-100/month | OCU-based pricing |
| **Bedrock Titan Embeddings** | ~$0.0001/1K tokens | One-time indexing + queries |
| **Bedrock Claude** | ~$3/1M input tokens | Same as current |
| **Storage** | ~$1/month | 42 small documents |

**Total Additional**: ~$50-100/month for RAG capabilities

---

## 📊 **Performance Expectations**

| Metric | Target | Notes |
|--------|--------|-------|
| **Query Latency** | <500ms | Embedding + search + Claude |
| **Retrieval Accuracy** | >90% | k-NN with good chunks |
| **Answer Quality** | High | Claude with context |
| **Concurrent Queries** | 100+ | OpenSearch auto-scales |

---

## 🧪 **Testing Strategy**

**Test Queries:**
1. "What are CPS 230 operational risk requirements?"
2. "Explain AUSTRAC AML/CTF obligations"
3. "What are AFCA dispute resolution timeframes?"
4. "Describe ASIC consumer protection guidelines"

**Expected**: Specific answers with document citations

---

## 📝 **Next Steps**

1. Create OpenSearch Serverless collection
2. Request Titan Embeddings access
3. Index 42 documents
4. Deploy RAG-enhanced agents
5. Test regulatory queries

See: **RAG_DEPLOYMENT.md** for deployment guide

---

**🎊 RAG System Ready for Deployment!**
