# 🏗️ NFRGuard AI Agents - Architecture Overview

## What is NFRGuard?

NFRGuard is your AI-powered security team that protects Bank of Anthos 24/7. Think of it as having 7 expert security professionals working around the clock, but faster, more consistent, and never getting tired.

## The 7 AI Agents

### 🕵️ **Transaction Risk Agent**
**What it does:** Spots suspicious transactions before they cause damage
- Analyzes every transaction in real-time
- Flags unusual patterns (large amounts, weird timing, foreign transfers)
- Gives risk scores from 0.0 (safe) to 1.0 (very dangerous)

### 📋 **Compliance Agent** 
**What it does:** Makes sure we follow banking rules and regulations
- Checks AUSTRAC compliance (Australian anti-money laundering rules)
- Ensures we report suspicious transactions properly
- Blocks transactions that break regulations

### 🛡️ **Resilience Agent**
**What it does:** Takes immediate action when threats are detected
- Freezes accounts when fraud is suspected
- Blocks transactions that are too risky
- Sends alerts to security teams

### 😊 **Customer Sentiment Agent**
**What it does:** Understands how customers are feeling
- Reads customer messages and support tickets
- Spots when customers are frustrated or angry
- Alerts customer service teams to help before problems get worse

### 🔒 **Data Privacy Agent**
**What it does:** Protects customer personal information
- Scans logs and systems for accidentally leaked personal data
- Removes sensitive information from logs
- Ensures we follow privacy laws

### 📚 **Knowledge Agent**
**What it does:** Creates easy-to-understand reports for humans
- Takes complex technical alerts and explains them in plain English
- Creates incident reports for security teams
- Helps humans understand what the AI agents are doing

### 🏦 **Banking Assistant**
**What it does:** Helps customers with banking questions and problems
- Answers customer questions about blocked transactions
- Provides explanations when things go wrong
- Escalates complex issues to human staff

## How They Work Together

```
Customer makes transaction
         ↓
🏦 Banking Assistant processes it
         ↓
🕵️ Risk Agent checks for fraud (with AUSTRAC guidance)
         ↓
📋 Compliance Agent checks regulations (using APRA standards)
         ↓
🛡️ Resilience Agent takes action if needed (based on CPG 230)
         ↓
📚 Knowledge Agent creates human report (with regulatory context)
```

### 🧠 **RAG Enhancement**

Each agent now has access to **real Australian banking regulations** through our RAG system:
- **ASIC**: Corporate governance and risk management guidance
- **APRA**: Operational risk standards (CPS 230) and practice guides (CPG 230)
- **AUSTRAC**: AML/CTF compliance requirements and transaction monitoring
- **AFCA**: Customer complaint handling and dispute resolution procedures

This means agents make decisions based on **actual regulatory requirements**, not just programmed rules.

## Real-World Example

**Scenario:** Customer tries to transfer $50,000 at 2 AM to a foreign account

1. **🕵️ Risk Agent:** "This looks suspicious - large amount, weird time, foreign account. Risk score: 0.95/1.0. Based on AUSTRAC guidance, this exceeds monitoring thresholds."

2. **📋 Compliance Agent:** "This exceeds AUSTRAC reporting threshold. According to APRA CPS 230, we need to hold this transaction for investigation."

3. **🛡️ Resilience Agent:** "Transaction blocked. Account temporarily frozen. Customer notified. Following CPG 230 incident management procedures."

4. **😊 Sentiment Agent:** Customer sends angry message: "Why was my transaction blocked? This is ridiculous!" → "Negative sentiment detected. Following AFCA complaint handling guidelines, escalate to customer service."

5. **🔒 Privacy Agent:** Finds customer email in system logs → "PII violation detected. Logs sanitized per AUSTRAC record keeping requirements."

6. **📚 Knowledge Agent:** Creates report: "Blocked $50K transfer at 2 AM to foreign account. Customer frustrated - recommend proactive outreach. Based on regulatory requirements, this action was compliant with AUSTRAC and APRA standards."

7. **🏦 Banking Assistant:** Sends automated response: "Your transaction is under security review per Australian banking regulations. Please contact support for assistance."

**Result:** Fraud prevented, regulations followed, customer helped, privacy protected - all in under 3 seconds!

## Why This Matters

### For the Bank:
- **Prevents fraud** - Stops millions in potential losses
- **Stays compliant** - Avoids regulatory fines with RAG-enhanced decisions
- **Protects reputation** - Maintains customer trust
- **Saves money** - Fewer human security staff needed
- **Regulatory confidence** - Decisions backed by actual Australian banking regulations

### For Customers:
- **Faster responses** - AI works instantly, 24/7
- **Better protection** - Accounts are safer
- **Clearer explanations** - Know why things happen with regulatory context
- **Proactive help** - Problems caught early
- **Transparent decisions** - Every action explained with regulatory basis

## Technical Architecture

The agents use an **event-driven architecture** enhanced with **RAG (Retrieval-Augmented Generation)** - they communicate through messages and have access to real regulatory documents. This makes the system:
- **Scalable** - Easy to add more agents
- **Reliable** - If one agent fails, others keep working  
- **Flexible** - Can change individual agents without affecting others
- **Regulatory-compliant** - Decisions based on actual Australian banking regulations
- **Transparent** - Every decision backed by regulatory guidance
- **Audit-ready** - Complete regulatory context for compliance reporting

## What Makes This Special

Unlike simple fraud detection systems, NFRGuard:
- **Thinks like a team** - Agents collaborate and share information
- **Learns continuously** - Gets smarter with every transaction
- **Covers everything** - Fraud, compliance, privacy, customer service
- **Explains itself** - Humans understand what's happening with regulatory context
- **Never sleeps** - Works 24/7 without breaks
- **Regulatory-aware** - Makes decisions based on actual Australian banking regulations
- **Transparent** - Every action backed by regulatory guidance and source attribution

This is the future of banking security - AI agents that work together like a superhuman security team! 🛡️
