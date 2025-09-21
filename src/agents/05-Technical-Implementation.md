# 🔧 Technical Implementation Guide

## How the AI Agents Actually Work

This guide explains the technical details of how NFRGuard AI agents are implemented, how they communicate, and how you can extend or modify them.

## 🛠️ **Development Environment Setup**

### **Installing Google Agent Development Kit (ADK)**

```bash
# Navigate to the right directory
cd D:\Joy_of_AI\Google_Bank_of_Anthos

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
.venv\Scripts\activate.ps1

# Install ADK - Follow https://google.github.io/adk-docs/get-started/
pip install google-adk

# Verify your installation
pip show google-adk
```

**Note:** The ADK is required for building and deploying AI agents. Make sure to follow the official documentation for the latest installation instructions.

## Architecture Overview

### Event-Driven Design
The agents use an **event-driven architecture** where they communicate through messages rather than direct calls:

```
Transaction Created → Risk Analysis → Compliance Check → Action Taken → Report Generated
```

### Communication Flow
1. **Banking Assistant** receives transaction request
2. **Publishes event** to message bus
3. **Other agents subscribe** to relevant events
4. **Agents process** and publish their own events
5. **Knowledge Agent** collects all events and creates reports

## Agent Implementation Details

### 1. Transaction Risk Agent

#### How It Works
```python
class TransactionRiskAgent:
    def analyze_transaction(self, transaction_data):
        # Extract key risk factors
        amount = transaction_data['amount']
        time = transaction_data['timestamp']
        destination = transaction_data['destination']
        
        # Calculate risk score
        risk_score = self.calculate_risk_score(amount, time, destination)
        
        # Determine if suspicious
        if risk_score > 0.8:
            self.publish_risk_alert(transaction_data, risk_score)
        
        return {"risk_score": risk_score, "suspicious": risk_score > 0.8}
```

#### Risk Factors Analyzed
- **Amount:** Large transactions (>$10,000) are higher risk
- **Timing:** Transactions at unusual hours (2 AM) are suspicious
- **Destination:** Foreign accounts or new recipients increase risk
- **Pattern:** Unusual spending patterns for the customer
- **Velocity:** Multiple large transactions in short time

### 2. Compliance Agent

#### How It Works
```python
class ComplianceAgent:
    def check_compliance(self, risk_data):
        # Check AUSTRAC requirements
        if risk_data['amount'] > 10000:
            return {
                "action": "hold_and_report",
                "reason": "AUSTRAC_threshold_exceeded",
                "report_required": True
            }
        
        # Check other regulations
        if self.is_high_risk_country(risk_data['destination']):
            return {
                "action": "additional_verification",
                "reason": "high_risk_country"
            }
        
        return {"action": "approve", "reason": "compliant"}
```

#### Compliance Rules
- **AUSTRAC:** Transactions >$10,000 require reporting
- **Sanctions:** Block transactions to sanctioned countries
- **KYC:** Verify customer identity for high-risk transactions
- **AML:** Monitor for money laundering patterns

### 3. Resilience Agent

#### How It Works
```python
class ResilienceAgent:
    def take_action(self, compliance_data):
        if compliance_data['action'] == 'hold_and_report':
            # Block the transaction
            self.block_transaction(compliance_data['transaction_id'])
            
            # Freeze account temporarily
            self.freeze_account(compliance_data['account_id'])
            
            # Notify customer
            self.notify_customer(compliance_data['account_id'])
            
            # Initiate investigation
            self.create_investigation_case(compliance_data)
        
        return {"action_taken": "blocked", "status": "investigating"}
```

#### Actions Available
- **Block Transaction:** Prevent completion
- **Freeze Account:** Temporarily restrict account access
- **Notify Customer:** Send automated message
- **Create Investigation:** Start manual review process
- **Escalate:** Alert human security team

### 4. Customer Sentiment Agent

#### How It Works
```python
class SentimentAgent:
    def analyze_sentiment(self, customer_message):
        # Analyze message for sentiment
        sentiment_score = self.nlp_model.analyze(customer_message)
        
        # Extract key indicators
        negative_words = self.extract_negative_words(customer_message)
        urgency_level = self.detect_urgency(customer_message)
        
        # Determine action needed
        if sentiment_score < 0.3:  # Negative sentiment
            return {
                "sentiment": "negative",
                "urgency": urgency_level,
                "action": "escalate_to_customer_service",
                "keywords": negative_words
            }
        
        return {"sentiment": "positive", "action": "monitor"}
```

#### Sentiment Analysis Features
- **Emotion Detection:** Anger, frustration, satisfaction
- **Urgency Detection:** Immediate vs routine issues
- **Keyword Extraction:** "blocked", "slow", "terrible"
- **Trend Analysis:** Comparing to historical sentiment

### 5. Data Privacy Agent

#### How It Works
```python
class PrivacyAgent:
    def scan_logs(self, log_entry):
        # Check for PII patterns
        pii_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'  # Credit card
        ]
        
        violations = []
        for pattern in pii_patterns:
            if re.search(pattern, log_entry):
                violations.append(pattern)
        
        if violations:
            # Sanitize the log
            sanitized_log = self.sanitize_pii(log_entry, violations)
            
            # Generate alert
            self.create_privacy_alert(violations, log_entry)
            
            return {"violation": True, "sanitized": sanitized_log}
        
        return {"violation": False}
```

#### Privacy Protection Features
- **PII Detection:** Email, SSN, credit card numbers
- **Log Sanitization:** Remove or mask sensitive data
- **Alert Generation:** Notify compliance team
- **Audit Trail:** Track all privacy violations

### 6. Knowledge Agent

#### How It Works
```python
class KnowledgeAgent:
    def generate_report(self, all_events):
        # Collect information from all events
        transaction_info = self.extract_transaction_info(all_events)
        risk_analysis = self.extract_risk_info(all_events)
        customer_impact = self.extract_sentiment_info(all_events)
        privacy_issues = self.extract_privacy_info(all_events)
        
        # Generate human-readable report
        report = f"""
        Security Incident Report
        
        Transaction: ${transaction_info['amount']}
        Risk Level: {risk_analysis['level']}
        Actions Taken: {risk_analysis['actions']}
        Customer Impact: {customer_impact['sentiment']}
        Privacy Issues: {privacy_issues['count']} violations detected
        
        Recommendations:
        - Monitor customer satisfaction
        - Review transaction patterns
        - Update risk models if needed
        """
        
        return {"report": report, "severity": "high" if risk_analysis['level'] == "HIGH" else "medium"}
```

#### Report Generation Features
- **Event Aggregation:** Combines data from all agents
- **Natural Language:** Human-readable explanations
- **Actionable Insights:** Specific recommendations
- **Severity Classification:** High/Medium/Low priority

### 7. Banking Assistant

#### How It Works
```python
class BankingAssistant:
    def handle_customer_query(self, customer_message):
        # Understand customer intent
        intent = self.nlp_model.classify_intent(customer_message)
        
        if intent == "transaction_blocked":
            # Provide explanation
            explanation = self.generate_blocking_explanation(customer_message)
            alternatives = self.suggest_alternatives(customer_message)
            
            return {
                "response": explanation,
                "alternatives": alternatives,
                "escalation": "automatic" if customer_message.contains_anger() else "none"
            }
        
        return {"response": "How can I help you today?"}
```

#### Customer Service Features
- **Intent Recognition:** Understand what customer wants
- **Automated Responses:** Common questions answered instantly
- **Escalation Logic:** When to involve humans
- **Alternative Suggestions:** Helpful options for blocked transactions

## Message Flow Implementation

### Event Types
```python
# Transaction events
TRANSACTION_CREATED = "transaction.created"
TRANSACTION_UPDATED = "transaction.updated"
TRANSACTION_COMPLETED = "transaction.completed"

# Risk events
RISK_ANALYZED = "risk.analyzed"
RISK_FLAGGED = "risk.flagged"
RISK_CLEARED = "risk.cleared"

# Compliance events
COMPLIANCE_CHECKED = "compliance.checked"
COMPLIANCE_VIOLATION = "compliance.violation"
COMPLIANCE_ACTION = "compliance.action"

# Customer events
CUSTOMER_MESSAGE = "customer.message"
SENTIMENT_ANALYZED = "sentiment.analyzed"
CUSTOMER_SATISFIED = "customer.satisfied"

# Privacy events
PRIVACY_SCAN = "privacy.scan"
PRIVACY_VIOLATION = "privacy.violation"
PRIVACY_SANITIZED = "privacy.sanitized"
```

### Event Publishing
```python
class EventPublisher:
    def publish(self, event_type, data):
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "source": self.agent_name
        }
        
        # Send to message bus
        self.message_bus.publish(event)
        
        # Log for debugging
        self.logger.info(f"Published {event_type}: {data}")
```

### Event Subscription
```python
class EventSubscriber:
    def subscribe(self, event_type, handler):
        self.message_bus.subscribe(event_type, handler)
    
    def handle_transaction_created(self, event):
        # Process the event
        result = self.process_transaction(event.data)
        
        # Publish response event
        self.publisher.publish("risk.analyzed", result)
```

## Database Integration

### Transaction Monitoring
```python
class DatabaseMonitor:
    def get_latest_transactions(self):
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="ledger-db",
            database="postgresdb",
            user="admin",
            password="password"
        )
        
        # Query latest transactions
        cursor = conn.cursor()
        cursor.execute("""
            SELECT transaction_id, amount, timestamp, from_acct, to_acct
            FROM transactions
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        
        return cursor.fetchall()
```

### Real-time Monitoring
```python
class RealTimeMonitor:
    def monitor_database(self):
        last_transaction_id = None
        
        while True:
            # Get latest transaction
            latest = self.get_latest_transaction()
            
            if latest['transaction_id'] != last_transaction_id:
                # New transaction detected
                self.process_new_transaction(latest)
                last_transaction_id = latest['transaction_id']
            
            time.sleep(2)  # Check every 2 seconds
```

## Extending the System

### Adding New Agents
1. **Create agent class** with required methods
2. **Subscribe to relevant events** in the message bus
3. **Publish response events** when processing is complete
4. **Add to deployment configuration** for Kubernetes

### Adding New Risk Factors
1. **Modify risk calculation** in Transaction Risk Agent
2. **Add new data sources** if needed
3. **Update risk scoring algorithm**
4. **Test with various scenarios**

### Adding New Compliance Rules
1. **Update compliance rules** in Compliance Agent
2. **Add new regulatory checks**
3. **Modify action recommendations**
4. **Update documentation**

## Performance Optimization

### Caching
```python
class CachedRiskAgent:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def calculate_risk(self, transaction_data):
        cache_key = self.generate_cache_key(transaction_data)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Calculate risk (expensive operation)
        risk_score = self.expensive_calculation(transaction_data)
        
        # Cache result
        self.cache[cache_key] = risk_score
        
        return risk_score
```

### Async Processing
```python
import asyncio

class AsyncAgent:
    async def process_transaction(self, transaction_data):
        # Process multiple aspects in parallel
        risk_task = asyncio.create_task(self.analyze_risk(transaction_data))
        compliance_task = asyncio.create_task(self.check_compliance(transaction_data))
        sentiment_task = asyncio.create_task(self.analyze_sentiment(transaction_data))
        
        # Wait for all to complete
        results = await asyncio.gather(risk_task, compliance_task, sentiment_task)
        
        return self.combine_results(results)
```

## Testing

### Unit Tests
```python
import unittest

class TestRiskAgent(unittest.TestCase):
    def test_high_risk_transaction(self):
        agent = TransactionRiskAgent()
        
        transaction = {
            "amount": 50000,
            "timestamp": "2025-01-14T02:00:00Z",
            "destination": "foreign_account"
        }
        
        result = agent.analyze_transaction(transaction)
        
        self.assertTrue(result["suspicious"])
        self.assertGreater(result["risk_score"], 0.8)
```

### Integration Tests
```python
class TestAgentIntegration(unittest.TestCase):
    def test_full_workflow(self):
        # Create test transaction
        transaction = self.create_test_transaction()
        
        # Publish event
        self.event_bus.publish("transaction.created", transaction)
        
        # Wait for processing
        time.sleep(1)
        
        # Check results
        events = self.event_bus.get_events()
        self.assertIn("risk.analyzed", events)
        self.assertIn("compliance.checked", events)
```

## Monitoring and Debugging

### Logging
```python
import logging

class AgentLogger:
    def __init__(self, agent_name):
        self.logger = logging.getLogger(agent_name)
        
    def log_decision(self, decision, reasoning):
        self.logger.info(f"Decision: {decision}, Reasoning: {reasoning}")
    
    def log_error(self, error, context):
        self.logger.error(f"Error: {error}, Context: {context}")
```

### Metrics
```python
class AgentMetrics:
    def track_processing_time(self, start_time, end_time):
        duration = end_time - start_time
        self.metrics.histogram("agent.processing.time", duration)
    
    def track_decision_accuracy(self, predicted, actual):
        accuracy = 1 if predicted == actual else 0
        self.metrics.counter("agent.decision.accuracy", accuracy)
```

This technical guide gives you everything you need to understand, modify, and extend the NFRGuard AI agent system! 🔧
