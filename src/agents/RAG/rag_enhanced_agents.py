#!/usr/bin/env python3
"""
RAG-Enhanced AI Agents
Integrates RAG capabilities with all 7 NFRGuard AI agents
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag_engine import AustralianBankingRAG, RAGResult
from google.adk.agents import Agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGEnhancedAgent:
    """Base class for RAG-enhanced agents"""
    
    def __init__(self, agent_name: str, model: str = "gemini-2.5-flash"):
        self.agent_name = agent_name
        self.model = model
        self.rag_engine = None
        self.initialize_rag()
    
    def initialize_rag(self):
        """Initialize RAG engine"""
        try:
            self.rag_engine = AustralianBankingRAG()
            if not self.rag_engine.initialize():
                logger.warning(f"RAG initialization failed for {self.agent_name}")
                self.rag_engine = None
            else:
                logger.info(f"RAG initialized successfully for {self.agent_name}")
        except Exception as e:
            logger.error(f"Failed to initialize RAG for {self.agent_name}: {e}")
            self.rag_engine = None
    
    def get_regulatory_guidance(self, query: str, context: Dict[str, Any] = None) -> str:
        """Get regulatory guidance using RAG"""
        if not self.rag_engine:
            return "RAG system not available"
        
        try:
            result = self.rag_engine.query(query, self.agent_name, context or {})
            return result.context
        except Exception as e:
            logger.error(f"RAG query failed for {self.agent_name}: {e}")
            return "Unable to retrieve regulatory guidance"

class RAGEnhancedTransactionRiskAgent(RAGEnhancedAgent):
    """RAG-enhanced Transaction Risk Agent"""
    
    def __init__(self):
        super().__init__("transaction_risk", "gemini-2.5-flash")
    
    def analyze_transaction_with_rag(self, transaction_data: Dict) -> Dict:
        """Analyze transaction with RAG-enhanced context"""
        # Get regulatory guidance
        query = f"suspicious transaction monitoring AUSTRAC AML/CTF amount {transaction_data.get('amount', 0)}"
        context = {
            "transaction_amount": transaction_data.get("amount", 0),
            "risk_level": "high" if transaction_data.get("amount", 0) > 10000 else "normal"
        }
        
        regulatory_guidance = self.get_regulatory_guidance(query, context)
        
        # Perform risk analysis
        amount = transaction_data.get('amount', 0)
        
        # Enhanced risk calculation with regulatory context
        risk_score = 0.1  # Base risk
        if amount > 10000:
            risk_score = 0.95  # High risk for large transactions
        elif amount > 1000:
            risk_score = 0.6   # Medium risk
        
        # Check if regulatory guidance indicates additional risk factors
        if "suspicious" in regulatory_guidance.lower() or "high risk" in regulatory_guidance.lower():
            risk_score = min(risk_score + 0.1, 1.0)
        
        suspicious = risk_score > 0.8
        
        result = {
            "transaction_id": transaction_data.get("transaction_id"),
            "score": risk_score,
            "suspicious": suspicious,
            "regulatory_guidance": regulatory_guidance,
            "reason": f"Large amount (${amount:,.2f})" if amount > 10000 else f"Normal amount (${amount:,.2f})"
        }
        
        logger.info(f"RAG-enhanced risk analysis: {result}")
        return result

class RAGEnhancedComplianceAgent(RAGEnhancedAgent):
    """RAG-enhanced Compliance Agent"""
    
    def __init__(self):
        super().__init__("compliance", "gemini-2.5-flash")
    
    def check_compliance_with_rag(self, risk_data: Dict) -> Dict:
        """Check compliance with RAG-enhanced context"""
        # Get compliance guidance
        query = f"compliance requirements APRA CPS 230 operational risk management"
        context = {
            "risk_level": "high" if risk_data.get("score", 0) > 0.8 else "normal",
            "regulation_type": "APRA"
        }
        
        regulatory_guidance = self.get_regulatory_guidance(query, context)
        
        # Determine compliance action
        if risk_data.get("score", 0) > 0.8:
            action = "hold_and_report"
            reason = "AUSTRAC_threshold_exceeded"
        else:
            action = "monitor"
            reason = "within_normal_parameters"
        
        result = {
            "transaction_id": risk_data.get("transaction_id"),
            "action": action,
            "reason": reason,
            "regulatory_guidance": regulatory_guidance,
            "compliance_status": "compliant" if action == "monitor" else "requires_review"
        }
        
        logger.info(f"RAG-enhanced compliance check: {result}")
        return result

class RAGEnhancedResilienceAgent(RAGEnhancedAgent):
    """RAG-enhanced Resilience Agent"""
    
    def __init__(self):
        super().__init__("resilience", "gemini-2.5-flash")
    
    def take_action_with_rag(self, compliance_data: Dict) -> Dict:
        """Take action with RAG-enhanced context"""
        # Get resilience guidance
        query = "incident management APRA CPG 230 operational risk resilience"
        context = {
            "threat_type": "transaction_risk",
            "action_required": compliance_data.get("action", "monitor")
        }
        
        regulatory_guidance = self.get_regulatory_guidance(query, context)
        
        # Determine actions based on compliance data
        if compliance_data.get("action") == "hold_and_report":
            actions_taken = [
                "block_transaction",
                "freeze_account_temporarily",
                "notify_customer",
                "initiate_investigation"
            ]
            status = "investigating"
        else:
            actions_taken = ["monitor"]
            status = "normal"
        
        result = {
            "transaction_id": compliance_data.get("transaction_id"),
            "actions_taken": actions_taken,
            "status": status,
            "regulatory_guidance": regulatory_guidance,
            "investigation_id": f"INV_{compliance_data.get('transaction_id', 'UNKNOWN')}"
        }
        
        logger.info(f"RAG-enhanced resilience action: {result}")
        return result

class RAGEnhancedCustomerSentimentAgent(RAGEnhancedAgent):
    """RAG-enhanced Customer Sentiment Agent"""
    
    def __init__(self):
        super().__init__("customer_sentiment", "gemini-2.5-flash")
    
    def analyze_sentiment_with_rag(self, customer_message: str, context: Dict = None) -> Dict:
        """Analyze customer sentiment with RAG-enhanced context"""
        # Get customer service guidance
        query = "customer complaint handling AFCA guidelines customer communication"
        rag_context = {
            "complaint_type": "transaction_blocked" if "blocked" in customer_message.lower() else "general",
            "sentiment": "negative" if any(word in customer_message.lower() for word in ["angry", "frustrated", "terrible", "ridiculous"]) else "neutral"
        }
        
        regulatory_guidance = self.get_regulatory_guidance(query, rag_context)
        
        # Analyze sentiment
        negative_words = ["angry", "frustrated", "terrible", "ridiculous", "blocked", "slow"]
        sentiment_score = 0.5  # Neutral base
        
        for word in negative_words:
            if word in customer_message.lower():
                sentiment_score -= 0.2
        
        sentiment_score = max(sentiment_score, 0.1)
        
        sentiment = "negative" if sentiment_score < 0.3 else "positive" if sentiment_score > 0.7 else "neutral"
        
        result = {
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "urgency": "high" if sentiment == "negative" else "normal",
            "action": "escalate_to_customer_service" if sentiment == "negative" else "monitor",
            "regulatory_guidance": regulatory_guidance,
            "keywords": [word for word in negative_words if word in customer_message.lower()]
        }
        
        logger.info(f"RAG-enhanced sentiment analysis: {result}")
        return result

class RAGEnhancedDataPrivacyAgent(RAGEnhancedAgent):
    """RAG-enhanced Data Privacy Agent"""
    
    def __init__(self):
        super().__init__("data_privacy", "gemini-2.5-flash")
    
    def scan_logs_with_rag(self, log_entry: str) -> Dict:
        """Scan logs with RAG-enhanced context"""
        # Get privacy guidance
        query = "data privacy obligations AUSTRAC record keeping customer data protection"
        context = {
            "data_type": "transaction_log" if "transaction" in log_entry.lower() else "general_log"
        }
        
        regulatory_guidance = self.get_regulatory_guidance(query, context)
        
        # Check for PII patterns
        pii_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'  # Credit card
        ]
        
        import re
        violations = []
        for pattern in pii_patterns:
            if re.search(pattern, log_entry):
                violations.append(pattern)
        
        violation_detected = len(violations) > 0
        
        result = {
            "violation": violation_detected,
            "violations": violations,
            "sanitized_log": self._sanitize_pii(log_entry, violations) if violation_detected else log_entry,
            "regulatory_guidance": regulatory_guidance,
            "severity": "medium" if violation_detected else "none",
            "action_required": "sanitize_and_alert" if violation_detected else "none"
        }
        
        logger.info(f"RAG-enhanced privacy scan: {result}")
        return result
    
    def _sanitize_pii(self, log_entry: str, violations: List[str]) -> str:
        """Sanitize PII from log entry"""
        sanitized = log_entry
        
        # Replace email addresses
        import re
        sanitized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', sanitized)
        
        # Replace SSNs
        sanitized = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]', sanitized)
        
        # Replace credit cards
        sanitized = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD_REDACTED]', sanitized)
        
        return sanitized

class RAGEnhancedKnowledgeAgent(RAGEnhancedAgent):
    """RAG-enhanced Knowledge Agent"""
    
    def __init__(self):
        super().__init__("knowledge", "gemini-2.5-flash")
    
    def generate_report_with_rag(self, all_events: List[Dict]) -> Dict:
        """Generate report with RAG-enhanced context"""
        # Get knowledge guidance
        query = "regulatory guidance summary compliance requirements explanation"
        context = {
            "requirement_type": "incident_reporting",
            "regulation_area": "operational_risk"
        }
        
        regulatory_guidance = self.get_regulatory_guidance(query, context)
        
        # Extract information from events
        transaction_info = self._extract_transaction_info(all_events)
        risk_analysis = self._extract_risk_info(all_events)
        customer_impact = self._extract_sentiment_info(all_events)
        privacy_issues = self._extract_privacy_info(all_events)
        
        # Generate report
        report = f"""
        NFRGuard AI Security Incident Report
        
        Transaction Details:
        - Amount: ${transaction_info.get('amount', 0):,.2f}
        - Transaction ID: {transaction_info.get('transaction_id', 'N/A')}
        
        Risk Analysis:
        - Risk Level: {risk_analysis.get('level', 'UNKNOWN')}
        - Risk Score: {risk_analysis.get('score', 0):.2f}
        - Actions Taken: {', '.join(risk_analysis.get('actions', []))}
        
        Customer Impact:
        - Sentiment: {customer_impact.get('sentiment', 'UNKNOWN')}
        - Urgency: {customer_impact.get('urgency', 'NORMAL')}
        
        Privacy Issues:
        - Violations Detected: {privacy_issues.get('count', 0)}
        - Severity: {privacy_issues.get('severity', 'NONE')}
        
        Regulatory Guidance:
        {regulatory_guidance[:500]}...
        
        Recommendations:
        - Monitor customer satisfaction
        - Review transaction patterns
        - Update risk models if needed
        - Ensure compliance with regulatory requirements
        """
        
        severity = "high" if risk_analysis.get('level') == "HIGH" else "medium"
        
        result = {
            "report": report,
            "severity": severity,
            "regulatory_guidance": regulatory_guidance,
            "summary": {
                "transaction": transaction_info,
                "risk": risk_analysis,
                "customer": customer_impact,
                "privacy": privacy_issues
            }
        }
        
        logger.info(f"RAG-enhanced knowledge report: {result}")
        return result
    
    def _extract_transaction_info(self, events: List[Dict]) -> Dict:
        """Extract transaction information from events"""
        for event in events:
            if "transaction_id" in event:
                return {
                    "transaction_id": event.get("transaction_id"),
                    "amount": event.get("amount", 0)
                }
        return {}
    
    def _extract_risk_info(self, events: List[Dict]) -> Dict:
        """Extract risk information from events"""
        for event in events:
            if "score" in event:
                return {
                    "level": "HIGH" if event.get("score", 0) > 0.8 else "NORMAL",
                    "score": event.get("score", 0),
                    "actions": event.get("actions_taken", [])
                }
        return {}
    
    def _extract_sentiment_info(self, events: List[Dict]) -> Dict:
        """Extract sentiment information from events"""
        for event in events:
            if "sentiment" in event:
                return {
                    "sentiment": event.get("sentiment"),
                    "urgency": event.get("urgency", "NORMAL")
                }
        return {}
    
    def _extract_privacy_info(self, events: List[Dict]) -> Dict:
        """Extract privacy information from events"""
        for event in events:
            if "violation" in event:
                return {
                    "count": len(event.get("violations", [])),
                    "severity": event.get("severity", "NONE")
                }
        return {}

class RAGEnhancedBankingAssistantAgent(RAGEnhancedAgent):
    """RAG-enhanced Banking Assistant Agent"""
    
    def __init__(self):
        super().__init__("banking_assistant", "gemini-2.5-flash")
    
    def handle_customer_query_with_rag(self, customer_message: str, context: Dict = None) -> Dict:
        """Handle customer query with RAG-enhanced context"""
        # Get customer service guidance
        query = "customer service guidelines AFCA banking assistance procedures"
        rag_context = {
            "service_type": "transaction_support" if "transaction" in customer_message.lower() else "general_support",
            "assistance_type": "complaint_resolution" if any(word in customer_message.lower() for word in ["problem", "issue", "complaint"]) else "information_request"
        }
        
        regulatory_guidance = self.get_regulatory_guidance(query, rag_context)
        
        # Determine intent
        if "blocked" in customer_message.lower():
            intent = "transaction_blocked"
            response = "Your transaction was temporarily blocked for security review. This is part of our fraud prevention measures as required by Australian banking regulations."
            alternatives = [
                "Contact our customer service team for assistance",
                "Verify your account details and try again",
                "Use our mobile app for smaller transactions"
            ]
            escalation = "automatic"
        elif "slow" in customer_message.lower():
            intent = "performance_issue"
            response = "We apologize for any delays. Our systems are designed to process transactions securely and efficiently."
            alternatives = [
                "Try our mobile app for faster processing",
                "Contact customer service for priority assistance"
            ]
            escalation = "none"
        else:
            intent = "general_inquiry"
            response = "How can I help you today? I'm here to assist with your banking needs."
            alternatives = []
            escalation = "none"
        
        result = {
            "intent": intent,
            "response": response,
            "alternatives": alternatives,
            "escalation": escalation,
            "regulatory_guidance": regulatory_guidance,
            "confidence": 0.8 if intent != "general_inquiry" else 0.5
        }
        
        logger.info(f"RAG-enhanced banking assistant response: {result}")
        return result

# Factory function to create RAG-enhanced agents
def create_rag_enhanced_agent(agent_type: str) -> RAGEnhancedAgent:
    """Create a RAG-enhanced agent of the specified type"""
    agent_classes = {
        "transaction_risk": RAGEnhancedTransactionRiskAgent,
        "compliance": RAGEnhancedComplianceAgent,
        "resilience": RAGEnhancedResilienceAgent,
        "customer_sentiment": RAGEnhancedCustomerSentimentAgent,
        "data_privacy": RAGEnhancedDataPrivacyAgent,
        "knowledge": RAGEnhancedKnowledgeAgent,
        "banking_assistant": RAGEnhancedBankingAssistantAgent
    }
    
    if agent_type not in agent_classes:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return agent_classes[agent_type]()

def main():
    """Test RAG-enhanced agents"""
    print("Testing RAG-enhanced agents...")
    
    # Test transaction risk agent
    risk_agent = RAGEnhancedTransactionRiskAgent()
    transaction_data = {"transaction_id": "TXN001", "amount": 25000}
    risk_result = risk_agent.analyze_transaction_with_rag(transaction_data)
    print(f"Risk Analysis: {risk_result}")
    
    # Test compliance agent
    compliance_agent = RAGEnhancedComplianceAgent()
    compliance_result = compliance_agent.check_compliance_with_rag(risk_result)
    print(f"Compliance Check: {compliance_result}")
    
    # Test customer sentiment agent
    sentiment_agent = RAGEnhancedCustomerSentimentAgent()
    sentiment_result = sentiment_agent.analyze_sentiment_with_rag("Why was my transaction blocked? This is ridiculous!")
    print(f"Sentiment Analysis: {sentiment_result}")

if __name__ == "__main__":
    main()
