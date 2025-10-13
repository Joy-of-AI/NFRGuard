# 🧠 RAG System Guide - Australian Banking Regulations

**Status**: ✅ Code Ready | ⏳ Not Yet Deployed  
**Technology**: AWS OpenSearch Serverless + Bedrock Titan Embeddings

---

## 📚 **42 Regulatory Documents Available**

### **Document Categories (6 Regulators)**

| Regulator | Full Name | Documents | Focus |
|-----------|-----------|-----------|-------|
| **ASIC** | Australian Securities & Investments Commission | 7 | Financial services, consumer protection |
| **APRA** | Australian Prudential Regulation Authority | 7 standards + 7 guides | Banking prudential standards |
| **AUSTRAC** | Australian Transaction Reports & Analysis Centre | 7 | Anti-money laundering, counter-terrorism |
| **AFCA** | Australian Financial Complaints Authority | 7 rules + 7 guidelines | Dispute resolution, complaints |

**Total**: 42 documents (6 categories × 7 documents each)

---

### **Complete Document List:**

#### **1. ASIC Guidance (7 documents)**
- `asic_guidance_1758505130.json` - Consumer Protection Guidelines
- `asic_guidance_1758505744.json` - Financial Services Licensing
- `asic_guidance_1758505833.json` - Market Integrity Rules
- `asic_guidance_1758507646.json` - Disclosure Requirements
- `asic_guidance_1758507691.json` - Investment Product Standards
- `asic_guidance_1758508261.json` - Digital Currency Guidelines
- `asic_guidance_1758508384.json` - Fraud Prevention Measures

#### **2. APRA Standards (7 documents)**
- `apra_standard_1758505131.json` - CPS 230: Operational Risk Management
- `apra_standard_1758505745.json` - CPS 234: Information Security
- `apra_standard_1758505834.json` - CPS 231: Outsourcing
- `apra_standard_1758507647.json` - CPS 232: Business Continuity
- `apra_standard_1758507692.json` - APS 220: Risk Management
- `apra_standard_1758508262.json` - CPS 226: Margining and Risk Mitigation
- `apra_standard_1758508385.json` - APS 222: Association with Related Entities

#### **3. APRA Practice Guides (7 documents)**
- `apra_practice_guide_1758505132.json` - CPG 230: Operational Risk
- `apra_practice_guide_1758505746.json` - CPG 234: Information Security Implementation
- `apra_practice_guide_1758505835.json` - CPG 231: Outsourcing Guide
- `apra_practice_guide_1758507648.json` - CPG 232: Business Continuity Planning
- `apra_practice_guide_1758507693.json` - CPG 220: Risk Management Framework
- `apra_practice_guide_1758508263.json` - CPG 226: Margining Implementation
- `apra_practice_guide_1758508386.json` - CPG 222: Related Entity Management

#### **4. AUSTRAC Obligations (7 documents)**
- `austrac_obligations_1758505133.json` - AML/CTF Act Requirements
- `austrac_obligations_1758505747.json` - Customer Identification
- `austrac_obligations_1758505836.json` - Transaction Monitoring
- `austrac_obligations_1758507649.json` - Suspicious Matter Reporting
- `austrac_obligations_1758507694.json` - Record Keeping Requirements
- `austrac_obligations_1758508264.json` - International Funds Transfer
- `austrac_obligations_1758508387.json` - Correspondent Banking

#### **5. AFCA Rules (7 documents)**
- `afca_rules_1758505134.json` - Operational Guidelines for Members
- `afca_rules_1758505748.json` - Complaint Handling Rules
- `afca_rules_1758505837.json` - Dispute Resolution Process
- `afca_rules_1758507650.json` - Timeframe Requirements
- `afca_rules_1758507695.json` - Evidence and Documentation
- `afca_rules_1758508265.json` - Fair Outcomes Framework
- `afca_rules_1758508388.json` - Member Obligations

#### **6. AFCA Guidelines (7 documents)**
- `afca_guideline_1758505135.json` - Best Practice Standards
- `afca_guideline_1758505749.json` - Customer Communication
- `afca_guideline_1758505838.json` - Information and Document Requests
- `afca_guideline_1758507651.json` - Systemic Issues Identification
- `afca_guideline_1758507696.json` - Remediation Requirements
- `afca_guideline_1758508266.json` - Vulnerable Customer Protection
- `afca_guideline_1758508389.json` - Financial Hardship Assistance

**Location**: `bank-of-anthos/src/agents/RAG/documents/*.json`

---

## 🏗️ **RAG System Architecture**

### **Current Tech Stack (AWS):**

```
┌────────────────────────────────────────────────────────┐
│              RAG System - AWS Architecture              │
└────────────────────────────────────────────────────────┘

Documents (42 JSON files)
         ↓
┌─────────────────────┐
│ Document Processor  │ ← Chunks text (1000 chars, 200 overlap)
└─────────────────────┘
         ↓
┌─────────────────────┐
│ Bedrock Titan       │ ← Generates 768-dim embeddings
│ Embeddings V2       │    Model: amazon.titan-embed-text-v2:0
└─────────────────────┘
         ↓
┌─────────────────────┐
│ OpenSearch          │ ← Vector database with k-NN search
│ Serverless          │    Stores embeddings + metadata
└─────────────────────┘
         ↓
┌─────────────────────┐
│ RAG Engine          │ ← Query → Retrieve → Augment
└─────────────────────┘
         ↓
┌─────────────────────┐
│ Claude 3.5 Sonnet   │ ← Generates answers with citations
│ (Bedrock)           │    Uses retrieved context
└─────────────────────┘
```

### **What is AWS RAG Wrapper?**

**File**: `aws_rag_engine.py`

**Purpose**: Wrapper that integrates multiple AWS services for RAG:

1. **BedrockEmbeddings Class** (`amazon.titan-embed-text-v2:0`)
   - Converts text → 768-dimensional vectors
   - Used for both document indexing and query embedding

2. **OpenSearchVectorStore Class**
   - Connects to OpenSearch Serverless
   - Stores document chunks with embeddings
   - Performs k-NN vector similarity search
   - Filters by metadata (regulator, agent_type, etc.)

3. **AWSRAGEngine Class**
   - Main orchestrator
   - Methods: `index_documents()`, `search()`, `query()`
   - Manages document chunking and retrieval
   - Returns results with confidence scores and sources

---

## 🔍 **k-NN vs ANN - Which One?**

### **Current Implementation: k-NN (k-Nearest Neighbors)**

**Pros:**
- ✅ **100% accurate** - finds exact nearest neighbors
- ✅ **Simple** - easy to implement and debug
- ✅ **No training** - works immediately

**Cons:**
- ❌ **Slower** - searches all vectors
- ❌ **Doesn't scale well** - performance degrades with millions of docs

### **Recommended: ANN (Approximate Nearest Neighbors)**

**Pros:**
- ✅ **Much faster** - 10-100x speed improvement
- ✅ **Scalable** - handles millions/billions of vectors
- ✅ **Widely used** - FAISS, HNSW, ScaNN

**Cons:**
- ⚠️ **Approximate** - might miss 1-2% of exact matches
- ⚠️ **Trade-off** - speed vs accuracy

### **For Your Use Case (42 documents):**

**Use k-NN** ✅
- Small dataset (42 docs = ~hundreds of chunks)
- k-NN is fast enough
- 100% accuracy is important for regulatory compliance
- No need for ANN complexity yet

**When to Switch to ANN:**
- Growing beyond 10,000 documents
- Need sub-100ms query latency
- Accuracy trade-off acceptable

**OpenSearch Serverless supports both** - easy to switch later!

---

## 🚀 **Deploy RAG System to AWS**

### **Prerequisites:**

**1. Request Bedrock Model Access** (if not done):
- Console: https://console.aws.amazon.com/bedrock/
- Models needed:
  - ✅ `anthropic.claude-3-5-sonnet-20240620-v1:0` (already have)
  - ⏳ `amazon.titan-embed-text-v2:0` (for embeddings)

**2. AWS Services Needed:**
- Amazon OpenSearch Serverless (vector database)
- AWS Bedrock (Titan Embeddings + Claude)
- IAM permissions for OpenSearch + Bedrock

---

## 📋 **Deployment Steps:**

Will create deployment script next...

---

**Location**: `bank-of-anthos/src/agents/RAG/documents/`  
**Storage**: Local JSON files (42 files)  
**Next**: Deploy to OpenSearch Serverless


