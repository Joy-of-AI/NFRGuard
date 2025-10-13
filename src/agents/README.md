# 🛡️ NFRGuard AI Agents - Banking Security System

**7 AI agents powered by AWS Bedrock that protect banking operations with real-time fraud detection, compliance monitoring, and regulatory guidance.**

---

## 📂 **Project Structure**

```
src/agents/
├── README.md                    # This file - project overview
├── agents/                      # 7 AI agent implementations
│   ├── banking_assistant_agent/
│   ├── compliance_agent/
│   ├── transaction_risk_agent/
│   ├── customer_sentiment_agent/
│   ├── data_privacy_agent/
│   ├── knowledge_agent/
│   └── resilience_agent/
├── docs/                        # All documentation
│   ├── architecture/            # System design & communication
│   ├── deployment/              # Setup & deployment guides
│   ├── technical/               # Implementation details
│   └── reference/               # Quick references & guides
├── RAG/                         # Regulatory document system (42 docs)
├── shared/                      # Shared libraries (Bedrock, EventBridge)
├── scripts/                     # Automation scripts
├── k8s/                         # Kubernetes manifests
├── tests/                       # Integration tests
└── eksctl/                      # Bundled EKS CLI tool
```

---

## 🚀 **Quick Start**

### **First Time - Complete Setup (~30 minutes)**

```bash
cd src/agents

# Automated setup
python scripts/01-complete-setup.py
```

### **Daily Use - Resume Cluster (2 minutes)**

```bash
cd src/agents

# Resume paused cluster
bash scripts/06-resume-cluster.sh

# Or Windows
.\resume_cluster.bat
```

### **When Done - Pause to Save Money**

```bash
# Pause cluster
bash scripts/05-pause-cluster.sh

# Or Windows
.\pause_cluster.bat
```

---

## 📚 **Documentation Guide**

### **🎯 Getting Started** (Start Here!)

| Document | Purpose | Location |
|----------|---------|----------|
| **GETTING_STARTED.txt** | Quick reference card | `docs/reference/` |
| **QUICK_RESUME_GUIDE.md** | Resume after pause (2 min) | `docs/deployment/` |
| **RESTART_GUIDE.md** | Complete deployment guide | `docs/deployment/` |

### **🏗️ Architecture** (Read in Order)

| # | Document | Purpose |
|---|----------|---------|
| 01 | **01-Architecture-Overview.md** | System design & agents |
| 02 | **02-Agent-Communication.md** | EventBridge & vectors |

### **🚀 Deployment** (Read in Order)

| # | Document | Purpose |
|---|----------|---------|
| 03 | **03-Quick-Resume-Guide.md** | Resume paused cluster (2 min) |
| 04 | **04-Deployment-Operations.md** | Operations guide |
| 05 | **05-Complete-Deployment-Guide.md** | Full setup from scratch |

### **🔧 Technical** (Read in Order)

| # | Document | Purpose |
|---|----------|---------|
| 06 | **06-Monitoring-Observability.md** | Monitoring guide |
| 07 | **07-Technical-Implementation.md** | Code details |
| 08 | **08-RAG-System-Guide.md** | RAG architecture (42 docs) |

### **📖 Reference** (Quick Guides)

| # | Document | Purpose |
|---|----------|---------|
| 09 | **09-Getting-Started.txt** | Quick start reference |
| 10 | **10-Quick-Reference.txt** | Commands cheat sheet |
| - | **COMPLETE_ANSWERS.md** | Technical Q&A |
| - | **DEPLOYMENT_STATUS.md** | Current status |
| - | **Demo-Presentation.md** | Demo scripts |

---

## 🤖 **7 AI Agents**

| Agent | Purpose | Features |
|-------|---------|----------|
| **Transaction Risk** | Fraud detection | Real-time risk scoring, pattern detection |
| **Compliance** | Regulatory compliance | AUSTRAC, APRA, ASIC rule checking |
| **Resilience** | Operational actions | Transaction holds, automated response |
| **Customer Sentiment** | Sentiment analysis | Detects negative feedback, escalates |
| **Data Privacy** | PII protection | Scans for privacy violations |
| **Knowledge** | Alert generation | Human-readable summaries |
| **Banking Assistant** | Customer service | Account operations, chat interface |

**Location**: `agents/*/agent.py`  
**Technology**: AWS Bedrock Claude 3.5 Sonnet

---

## 🧠 **RAG System (Regulatory Documents)**

**42 Australian Banking Regulatory Documents:**
- **ASIC**: 7 documents (consumer protection)
- **APRA**: 14 documents (prudential standards + guides)
- **AUSTRAC**: 7 documents (AML/CTF)
- **AFCA**: 14 documents (dispute resolution)

**Features:**
- Document retrieval with citations
- Regulatory compliance verification
- Fact-based answers
- Source attribution

**Options:**
- Mock RAG: $0/month (keyword search)
- Full RAG: ~$700/month (OpenSearch Serverless + vector embeddings)

**See**: `docs/technical/RAG_SYSTEM_GUIDE.md`

---

## 🔄 **Agent Communication**

**Technology**: AWS EventBridge (event-driven architecture)

**How it works:**
1. Agents publish events (e.g., "risk.detected")
2. EventBridge routes to subscribers
3. Multiple agents can react to same event
4. Fallback to AWS SNS if needed

**Features:**
- Loose coupling (agents independent)
- Automatic retry and error handling
- Event history for audit
- Cost: ~$0.03/month

**See**: `docs/architecture/AGENT_COMMUNICATION.md`

---

## 🛠️ **Automation Scripts**

| # | Script | Purpose | Platform |
|---|--------|---------|----------|
| 01 | `01-complete-setup.py` | Full automated deployment | All |
| 02 | `02-setup-aws-infrastructure.sh` | Setup EKS, ECR, S3, DynamoDB | Bash |
| 03 | `03-build-and-push-images.sh` | Build Docker images | Bash |
| 04 | `04-deploy-to-eks.sh` | Deploy to Kubernetes | Bash |
| 05 | `05-pause-cluster.sh` | Pause to save money | Bash |
| 06 | `06-resume-cluster.sh` | Resume quickly | Bash |
| 07 | `07-cleanup-aws-resources.sh` | Delete everything | Bash |
| - | `pause_cluster.bat` | Pause cluster | Windows |
| - | `resume_cluster.bat` | Resume cluster | Windows |
| - | `setup-opensearch.sh` | Setup RAG vector DB | Bash |
| - | `create-secure-env.sh` | Create .env file | Bash |
| - | `fix-agents.py` | Fix agent code | Python |
| - | `run-tests.sh` | Run test suite | Bash |

**Location**: `scripts/`

---

## 💰 **Cost Management**

| Status | Cost/Day | Use Case |
|--------|----------|----------|
| **Running** | ~$2.40 | Active development/testing |
| **Paused** | ~$2.40 | Overnight (pods at 0) |
| **Deleted** | $0 | Not using for weeks |
| **+ Mock RAG** | +$0 | Regulatory citations |
| **+ Full RAG** | +~$23/day | Production semantic search |

---

## ✅ **Current Status**

- ✅ Deployed on AWS EKS (`fintech-ai-aws-cluster`, ap-southeast-2)
- ✅ 13 agent pods (7 agents × replicas)
- ✅ Bank of Anthos integrated
- ✅ All bugs fixed and tested
- ✅ Bedrock Claude 3.5 Sonnet working
- ✅ IAM permissions configured
- ✅ 42 regulatory documents ready
- ✅ Mock RAG tested and working
- ✅ **100% AWS** (all GCP references removed)
- ✅ **Professional structure** - Ready for presentation

---

## 🎯 **Technology Stack**

**AI & ML:**
- AWS Bedrock Claude 3.5 Sonnet (LLM)
- AWS Bedrock Titan Embeddings V2 (768-dim vectors)
- Amazon OpenSearch Serverless (optional, for RAG)

**Infrastructure:**
- Amazon EKS (Kubernetes)
- Amazon ECR (Docker registry)
- Amazon EC2 (t3.large spot instances)

**Integration:**
- AWS EventBridge (agent communication)
- AWS SNS (fallback messaging)
- AWS IAM (permissions)

---

## 📖 **Next Steps**

**For Development:**
1. Read: `docs/reference/GETTING_STARTED.txt`
2. Resume cluster: `bash scripts/resume_cluster.sh`
3. Test agents: `kubectl port-forward -n nfrguard-agents svc/banking-assistant-agent 8080:8080`

**For Understanding:**
1. Architecture: `docs/architecture/01-Architecture-Overview.md`
2. Communication: `docs/architecture/AGENT_COMMUNICATION.md`
3. Technical: `docs/technical/05-Technical-Implementation.md`

**For Deployment:**
1. Complete guide: `docs/deployment/RESTART_GUIDE.md`
2. Quick resume: `docs/deployment/QUICK_RESUME_GUIDE.md`

---

## 📞 **Support & References**

**Key Files:**
- Troubleshooting: `docs/deployment/RESTART_GUIDE.md` (11 common issues)
- Q&A: `docs/reference/COMPLETE_ANSWERS.md`
- Changelog: `docs/reference/CHANGELOG.txt`

**External Resources:**
- AWS Bedrock: https://docs.aws.amazon.com/bedrock/
- AWS EventBridge: https://docs.aws.amazon.com/eventbridge/
- Amazon OpenSearch: https://docs.aws.amazon.com/opensearch-service/

---

## 🎊 **Production Ready**

This system is ready for:
- ✅ Professional demonstrations
- ✅ Client presentations
- ✅ Production deployment
- ✅ Team collaboration
- ✅ Stakeholder review

**Clean, organized, and fully documented!** ✨

---

**For complete documentation, see `docs/` folder**
