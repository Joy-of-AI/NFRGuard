# 🔄 Agent-to-Agent Communication System

**How 7 AI agents work together as a coordinated team**

---

## 🏗️ **Communication Architecture**

### **Approach**: Event-Driven Architecture (AWS EventBridge)

```
┌─────────────────────────────────────────────────────────┐
│          Agent Communication Flow                        │
└─────────────────────────────────────────────────────────┘

Transaction Risk Agent
         │
         │ Detects fraud
         ↓
    [PUT EVENT]
         │
    "risk.detected"
         ↓
┌────────────────────┐
│  AWS EventBridge   │ ← Serverless event bus
│  (Event Router)    │    (Replaces Google Pub/Sub)
└────────────────────┘
         │
         ├─────────────────┐
         ↓                 ↓
    [EVENT RULE]      [EVENT RULE]
         │                 │
Compliance Agent    Resilience Agent
         │                 │
         ↓                 ↓
  Checks rules      Takes action
         │                 │
    [PUT EVENT]           │
         │                 │
  "compliance.action"     │
         │                 │
         └────────▶────────┘
                   │
                   ↓
            Resilience Agent
            Applies hold/release
```

---

## 🛠️ **AWS Services Used**

### **1. AWS EventBridge (Primary)** ⭐

**What**: Serverless event bus for application integration

**Purpose**: Routes events between agents

**How it works:**
```python
# Agent 1 publishes
publish("risk.detected", {
    "transaction_id": "TX123",
    "risk_score": 0.95,
    "action": "hold"
})

# EventBridge routes to subscribers

# Agent 2 receives
subscribe("risk.detected", handle_risk_event)
```

**Features:**
- ✅ Event-driven messaging (publish/subscribe pattern)
- ✅ Event filtering (by type, source, content)
- ✅ Automatic retry with exponential backoff
- ✅ Dead letter queues for failed events
- ✅ Event replay and archive
- ✅ Event rules and patterns

**Cost**: $1/million events (very cheap!)

**AWS Terminology:**
- **Publish** = `PutEvents` (send events to EventBridge)
- **Subscribe** = Create EventBridge Rule (route events to targets)
- **Topic** = Event Bus (default or custom)
- **Message** = Event (JSON payload)

---

### **2. AWS SNS (Fallback)**

**What**: Simple Notification Service

**Purpose**: Backup if EventBridge fails

**How it works:**
```python
if eventbridge_fails:
    sns.publish(
        TopicArn='arn:aws:sns:...',
        Message=json.dumps(event_data)
    )
```

**Use case**: Reliability fallback

---

### **3. Local Queue (In-Process)**

**What**: Python `Queue` for same-pod communication

**Purpose**: Fast local message passing

**How it works:**
```python
# Thread-safe queue
local_queue.put(event)

# Background thread processes
while running:
    event = local_queue.get()
    for handler in subscribers:
        handler(event)
```

**Benefit**: Near-instant delivery for local events

---

## 📊 **Complete Communication Stack**

| Layer | Technology | Purpose | Latency |
|-------|-----------|---------|---------|
| **Primary** | AWS EventBridge | Inter-agent events (publish/subscribe) | ~100ms |
| **Fallback** | AWS SNS | Backup messaging (topics) | ~50ms |
| **Local** | Python Queue | In-process events | <1ms |
| **Protocol** | JSON | Event payload format | - |

**Note**: AWS EventBridge provides publish/subscribe functionality (replaces Google Pub/Sub)

---

## 🔄 **Event Flow Example**

### **Scenario**: Suspicious transaction detected

**Step 1: Transaction Risk Agent**
```python
# Detects fraud
risk_score = analyze_transaction(tx)

if risk_score > 0.8:
    # Publish risk event
    publish("risk.detected", {
        "event_type": "risk.detected",
        "transaction_id": tx_id,
        "risk_score": 0.95,
        "indicators": ["overseas", "new_account", "large_amount"],
        "timestamp": datetime.now()
    })
```

**Step 2: EventBridge Routes Event**
```
AWS EventBridge:
  Event: risk.detected
  Routes to: compliance-agent (subscribed)
```

**Step 3: Compliance Agent Receives**
```python
# Subscribed to risk.detected
def handle_risk_event(event):
    # Check compliance
    compliance_result = check_regulations(event)
    
    if requires_action(compliance_result):
        # Publish compliance action
        publish("compliance.action", {
            "event_type": "compliance.action",
            "transaction_id": event["transaction_id"],
            "action": "hold_and_report",
            "regulation": "AUSTRAC_AML_CTF",
            "reason": "High risk overseas transfer"
        })
```

**Step 4: Resilience Agent Receives**
```python
# Subscribed to compliance.action
def handle_compliance_action(event):
    if event["action"] == "hold_and_report":
        # Apply transaction hold
        apply_hold(event["transaction_id"])
        
        # Notify knowledge agent
        publish("ops.alert", {
            "event_type": "ops.alert",
            "transaction_id": event["transaction_id"],
            "action_taken": "hold_applied"
        })
```

**Step 5: Knowledge Agent Receives**
```python
# Subscribed to ops.alert
def handle_ops_alert(event):
    # Generate human-readable alert
    alert = create_alert(event)
    send_to_dashboard(alert)
```

**Total Time**: ~500ms from detection to action!

---

## 📝 **Event Types & Subscribers**

| Event Type | Publisher | Subscribers | Purpose |
|------------|-----------|-------------|---------|
| `risk.detected` | Transaction Risk | Compliance, Knowledge | Fraud alert |
| `compliance.action` | Compliance | Resilience | Required action |
| `ops.alert` | Resilience | Knowledge, Banking Assistant | Operational alert |
| `privacy.violation` | Data Privacy | Compliance, Knowledge | PII leak |
| `sentiment.negative` | Customer Sentiment | Banking Assistant, Knowledge | Customer issue |

---

## 💡 **Why Event-Driven?**

### **vs Direct API Calls:**

| Approach | Event-Driven (Current) | Direct API Calls |
|----------|----------------------|------------------|
| **Coupling** | ✅ Loose (agents independent) | ❌ Tight (agents depend on each other) |
| **Scaling** | ✅ Easy (add agents anytime) | ❌ Hard (update all callers) |
| **Reliability** | ✅ High (retry, fallback) | ❌ Lower (single point of failure) |
| **Async** | ✅ Yes (non-blocking) | ❌ Synchronous |
| **Complexity** | ⚠️ Higher (event routing) | ✅ Simple |

**Best for**: Multi-agent systems with complex interactions (your case!)

---

## 🔧 **Implementation Details**

### **File**: `shared/aws_messaging.py`

**Key Methods:**

**1. `publish(event_type, data)`**
```python
# Publishes to 3 destinations:
1. AWS EventBridge (global event bus)
2. Local Queue (same pod)
3. SNS Topic (fallback)

# Returns True if successful
```

**2. `subscribe(event_type, handler)`**
```python
# Registers handler for event type
# Creates EventBridge rule
# Adds to local subscribers

subscribe("risk.detected", my_handler)
```

**3. Background Processing**
```python
# Separate thread processes local events
while running:
    event = queue.get()
    for handler in subscribers[event_type]:
        handler(event)  # Call registered handlers
```

---

## 📊 **Communication Patterns**

### **Pattern 1: Fan-Out (1 → Many)**

```
Transaction Risk Agent
         │
         ↓ (publishes risk.detected)
    EventBridge
         │
         ├──────────┬──────────┐
         ↓          ↓          ↓
   Compliance  Knowledge  Resilience
```

**Use**: Broadcasting alerts to multiple agents

---

### **Pattern 2: Chain (1 → 2 → 3)**

```
Risk Agent → Compliance Agent → Resilience Agent

risk.detected → compliance.action → ops.alert
```

**Use**: Sequential processing workflow

---

### **Pattern 3: Request-Response**

```
Banking Assistant → Transaction Risk → Banking Assistant

(asks for risk score) → (analyzes) → (returns score)
```

**Use**: Synchronous queries between agents

---

## 🚀 **Advantages of This Approach**

### **1. Scalability**
- Add new agents without modifying existing ones
- Agents can scale independently
- EventBridge handles routing automatically

### **2. Reliability**
- Messages persist if agent is down
- Automatic retries
- Dead letter queues for failed events
- Fallback to SNS

### **3. Flexibility**
- One event can trigger multiple agents
- Easy to add new subscribers
- Change workflows without code changes

### **4. Observability**
- All events logged in CloudWatch
- Event history for debugging
- Trace complete message flows

---

## 💰 **Cost**

| Service | Cost | Your Usage | Total |
|---------|------|------------|-------|
| **EventBridge** | $1/million events | ~1000/day | ~$0.001/day |
| **SNS** | $0.50/million | Fallback only | ~$0 |

**Total**: Negligible (~$0.03/month)

---

## 🔧 **Configuration**

**Environment Variables:**
```bash
AWS_REGION=us-east-1
EVENT_BUS_NAME=nfrguard-event-bus
```

**EventBridge Setup:**
```bash
# Event bus created automatically by agents
# Rules created when agents subscribe
# No manual configuration needed!
```

---

## ⚠️ **Current Issue (Low Priority)**

You saw this error:
```
ERROR: User not authorized to perform: events:DescribeRule
```

**Impact**: ⚠️ Warning only
- Agents still communicate via local queue
- EventBridge works but can't verify rules
- Fix: Add EventBridge policy to node role (optional)

**Fix (if needed):**
```bash
NODE_ROLE=$(aws iam list-roles --query "Roles[?contains(RoleName, 'fintech-ai-aws-cluster-node')].RoleName" --output text)

aws iam attach-role-policy \
  --role-name $NODE_ROLE \
  --policy-arn arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess
```

---

## 📝 **Summary**

**Your agent communication uses:**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Primary Bus** | AWS EventBridge | Global event routing |
| **Fallback** | AWS SNS | Backup messaging |
| **Local** | Python Queue + Threading | In-process events |
| **Pattern** | Event-driven (EventBridge Rules) | Loose coupling |
| **Protocol** | JSON | Event format |
| **Cost** | ~$0.03/month | Very cheap! |

---

# 🔢 What are 768-Dimensional Vectors?

## 🎯 **Simple Explanation**

**Vector**: A list of numbers representing meaning

**768-dimensional**: A list of 768 numbers

### **Example:**

**Text**: "Bank account balance"

**768-dim Vector** (simplified):
```python
[0.234, -0.891, 0.456, 0.123, ..., -0.334]
        ↑       ↑       ↑              ↑
     768 numbers total
```

Each number captures a different aspect of meaning!

---

## 🧠 **How It Works**

### **Step 1: Text → Vector (Embedding)**

**Bedrock Titan Embeddings converts text to numbers:**

```python
text = "APRA CPS 230 operational resilience"

embedding = titan.get_embedding(text)

# Result: [0.234, -0.891, 0.456, ..., -0.334]
# 768 numbers that "mean" this text
```

### **Step 2: Similar Meaning = Similar Numbers**

**Similar texts have similar vectors:**

```python
"APRA CPS 230 requirements"
→ [0.234, -0.891, 0.456, ...]

"CPS 230 operational standards"
→ [0.241, -0.887, 0.461, ...]  # Very similar!

"Cat sat on mat"
→ [-0.789, 0.234, -0.123, ...]  # Very different!
```

### **Step 3: Find Similar Documents**

**Using cosine similarity:**

```python
query_vector = [0.234, -0.891, 0.456, ...]

# Compare with all document vectors
doc1_similarity = 0.95  # Very similar! ✅
doc2_similarity = 0.12  # Not similar
doc3_similarity = 0.89  # Pretty similar ✅

# Return top matches (0.95, 0.89)
```

---

## 📐 **Why 768 Dimensions?**

### **More Dimensions = More Detail**

**50 dimensions**: Basic meaning  
**384 dimensions**: Good meaning  
**768 dimensions**: Rich, detailed meaning ⭐  
**1536 dimensions**: Very detailed (overkill for most)

**Titan Embeddings V2** uses 768 because it's the sweet spot:
- ✅ Captures nuanced meaning
- ✅ Fast to compute
- ✅ Good storage size
- ✅ Industry standard

---

## 🎨 **Visualization (Simplified)**

Imagine each dimension as a feature:

```
Dimension 1: "Banking-ness"      → 0.89
Dimension 2: "Regulatory-ness"   → 0.92
Dimension 3: "Risk-ness"         → 0.45
Dimension 4: "Customer-ness"     → 0.12
...
Dimension 768: "Legal-ness"      → 0.78
```

Together, these 768 numbers capture the complete meaning!

---

## 🔍 **Real Example**

### **Query**: "What are CPS 230 requirements?"

**Step 1: Convert to vector**
```python
query_vector = titan.embed("What are CPS 230 requirements?")
# [0.234, -0.891, 0.456, ..., -0.334]  (768 numbers)
```

**Step 2: Compare with documents**
```python
# Document 1: APRA CPS 230 Standard
doc1_vector = [0.241, -0.887, 0.461, ...]
similarity = cosine_similarity(query_vector, doc1_vector)
# = 0.95 (95% match!) ✅

# Document 2: AFCA Complaint Rules
doc2_vector = [-0.123, 0.567, -0.234, ...]
similarity = cosine_similarity(query_vector, doc2_vector)
# = 0.15 (15% match - not relevant)
```

**Step 3: Return best matches**
```
Top Results:
1. APRA CPS 230 (95% match) ✅
2. APRA CPG 230 (89% match) ✅
3. APRA CPS 232 (67% match)
```

---

## 💡 **Why Vectors are Powerful**

### **Traditional Keyword Search:**
```
Query: "operational resilience requirements"
Matches: Documents containing exact words
        "operational" AND "resilience" AND "requirements"

Misses:
- "business continuity standards"  (same meaning!)
- "system recovery procedures"     (related!)
```

### **Vector Search (Semantic):**
```
Query: "operational resilience requirements"
Vector: [0.234, -0.891, ...]

Finds:
✅ "operational resilience requirements" (exact)
✅ "business continuity standards"        (similar meaning!)
✅ "system recovery procedures"           (related!)
✅ "critical service availability"        (conceptually similar!)
```

**Understands meaning, not just words!**

---

## 📏 **Vector Math**

### **Cosine Similarity (How we compare)**

**Formula**:
```
similarity = (A · B) / (||A|| × ||B||)

Where:
A = Query vector (768 numbers)
B = Document vector (768 numbers)
· = Dot product
||A|| = Vector length
```

**Result**: Number from -1 to 1
- **1.0** = Identical meaning
- **0.8-1.0** = Very similar ✅
- **0.5-0.8** = Somewhat similar
- **< 0.5** = Different

---

## 🎯 **In Your RAG System**

### **Each Document Chunk:**

```json
{
  "id": "apra_cps_230_chunk_5",
  "content": "APRA requires banks to maintain operational resilience...",
  "embedding": [0.234, -0.891, 0.456, ..., -0.334],
                 ↑_____________________________↑
                       768 numbers
  "metadata": {
    "regulator": "APRA",
    "document": "CPS 230"
  }
}
```

### **When You Query:**

```python
# Your query
query = "What are resilience requirements?"

# Convert to vector (768 numbers)
query_vector = titan.embed(query)

# OpenSearch finds most similar vectors
results = opensearch.knn_search(
    query_vector=query_vector,
    k=5  # Top 5 matches
)

# Returns chunks with highest similarity scores
```

---

## 🔢 **Why 768 Specifically?**

**Historical reason**: BERT model (2018) used 768  
**Technical reason**: Optimal for:
- Capture complex relationships
- Fast computation
- Reasonable storage (768 × 4 bytes = 3KB per vector)

**Alternatives**:
- OpenAI: 1536 dimensions (more detailed, slower)
- Sentence Transformers: 384 dimensions (faster, less detail)
- Titan V2: **768 dimensions** ← Your choice! ⭐

---

## 📊 **Storage Requirements**

**For 42 documents:**

```
42 documents
× ~20 chunks/document
= ~840 chunks

Each chunk:
- Vector: 768 × 4 bytes = 3KB
- Content: ~1KB
- Metadata: ~0.5KB
= ~4.5KB per chunk

Total: 840 × 4.5KB = ~3.8 MB
```

**Very small!** Fits easily in OpenSearch.

---

## 🎯 **Summary**

### **Agent Communication:**
- **Technology**: AWS EventBridge (primary) + SNS (fallback) + Local Queue
- **Pattern**: Event-driven architecture with EventBridge Rules
- **Latency**: ~100ms inter-agent
- **Cost**: ~$0.03/month
- **Why**: Loose coupling, scalable, reliable
- **Replaces**: Google Cloud Pub/Sub → AWS EventBridge

### **768-Dimensional Vectors:**
- **What**: List of 768 numbers representing text meaning
- **How**: Bedrock Titan converts text → numbers
- **Why**: Captures semantic similarity
- **Use**: Find similar documents by meaning, not keywords
- **Size**: 768 is sweet spot (detail + speed)

---

## 🚀 **Next Steps**

**Tomorrow**:
1. Test Mock RAG (uses keyword search, not vectors yet)
2. See document retrieval with citations
3. Later: Deploy full OpenSearch for vector search

**The difference**:
- **Mock RAG**: Keyword matching (good, $0)
- **Full RAG**: Vector similarity (better, $700/mo)

Both give you citations from 42 regulatory documents!

---

**🎊 Communication is event-driven! Vectors capture meaning!** ✨

**Any more questions?** 🚀

