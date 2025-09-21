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
🕵️ Risk Agent checks for fraud
         ↓
📋 Compliance Agent checks regulations
         ↓
🛡️ Resilience Agent takes action if needed
         ↓
📚 Knowledge Agent creates human report
```

## Real-World Example

**Scenario:** Customer tries to transfer $50,000 at 2 AM to a foreign account

1. **🕵️ Risk Agent:** "This looks suspicious - large amount, weird time, foreign account. Risk score: 0.95/1.0"

2. **📋 Compliance Agent:** "This exceeds AUSTRAC reporting threshold. We need to hold this transaction."

3. **🛡️ Resilience Agent:** "Transaction blocked. Account temporarily frozen. Customer notified."

4. **😊 Sentiment Agent:** Customer sends angry message: "Why was my transaction blocked? This is ridiculous!" → "Negative sentiment detected. Escalate to customer service."

5. **🔒 Privacy Agent:** Finds customer email in system logs → "PII violation detected. Logs sanitized."

6. **📚 Knowledge Agent:** Creates report: "Blocked $50K transfer at 2 AM to foreign account. Customer frustrated - recommend proactive outreach."

7. **🏦 Banking Assistant:** Sends automated response: "Your transaction is under security review. Please contact support for assistance."

**Result:** Fraud prevented, regulations followed, customer helped, privacy protected - all in under 3 seconds!

## Why This Matters

### For the Bank:
- **Prevents fraud** - Stops millions in potential losses
- **Stays compliant** - Avoids regulatory fines
- **Protects reputation** - Maintains customer trust
- **Saves money** - Fewer human security staff needed

### For Customers:
- **Faster responses** - AI works instantly, 24/7
- **Better protection** - Accounts are safer
- **Clearer explanations** - Know why things happen
- **Proactive help** - Problems caught early

## Technical Architecture

The agents use an **event-driven architecture** - they communicate through messages rather than talking directly to each other. This makes the system:
- **Scalable** - Easy to add more agents
- **Reliable** - If one agent fails, others keep working  
- **Flexible** - Can change individual agents without affecting others

## What Makes This Special

Unlike simple fraud detection systems, NFRGuard:
- **Thinks like a team** - Agents collaborate and share information
- **Learns continuously** - Gets smarter with every transaction
- **Covers everything** - Fraud, compliance, privacy, customer service
- **Explains itself** - Humans understand what's happening
- **Never sleeps** - Works 24/7 without breaks

This is the future of banking security - AI agents that work together like a superhuman security team! 🛡️
