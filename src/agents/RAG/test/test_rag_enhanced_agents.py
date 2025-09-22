#!/usr/bin/env python3
"""
Tests for RAG-Enhanced Agents
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag_enhanced_agents import (
    RAGEnhancedAgent, RAGEnhancedTransactionRiskAgent, RAGEnhancedComplianceAgent,
    RAGEnhancedResilienceAgent, RAGEnhancedCustomerSentimentAgent,
    RAGEnhancedDataPrivacyAgent, RAGEnhancedKnowledgeAgent,
    RAGEnhancedBankingAssistantAgent, create_rag_enhanced_agent
)

class TestRAGEnhancedAgent:
    """Test cases for base RAG Enhanced Agent"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        # Mock the RAG engine to avoid actual initialization
        self.agent = RAGEnhancedAgent("test_agent")
        self.agent.rag_engine = None  # Disable RAG for basic tests
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        assert self.agent is not None
        assert self.agent.agent_name == "test_agent"
        assert self.agent.model == "gemini-2.5-flash"
    
    def test_get_regulatory_guidance_no_rag(self):
        """Test getting regulatory guidance without RAG"""
        guidance = self.agent.get_regulatory_guidance("test query")
        assert guidance == "RAG system not available"

class TestRAGEnhancedTransactionRiskAgent:
    """Test cases for Transaction Risk Agent"""
    
    def setup_method(self):
        """Set up test environment"""
        self.agent = RAGEnhancedTransactionRiskAgent()
        self.agent.rag_engine = None  # Disable RAG for testing
    
    def test_analyze_transaction_with_rag(self):
        """Test transaction analysis"""
        transaction_data = {
            "transaction_id": "TXN001",
            "amount": 25000
        }
        
        result = self.agent.analyze_transaction_with_rag(transaction_data)
        
        assert result["transaction_id"] == "TXN001"
        assert result["score"] == 0.95  # High risk for large amount
        assert result["suspicious"] is True
        assert "Large amount" in result["reason"]
        assert "regulatory_guidance" in result
    
    def test_analyze_small_transaction(self):
        """Test analysis of small transaction"""
        transaction_data = {
            "transaction_id": "TXN002",
            "amount": 500
        }
        
        result = self.agent.analyze_transaction_with_rag(transaction_data)
        
        assert result["transaction_id"] == "TXN002"
        assert result["score"] == 0.1  # Low risk for small amount
        assert result["suspicious"] is False
        assert "Normal amount" in result["reason"]

class TestRAGEnhancedComplianceAgent:
    """Test cases for Compliance Agent"""
    
    def setup_method(self):
        """Set up test environment"""
        self.agent = RAGEnhancedComplianceAgent()
        self.agent.rag_engine = None  # Disable RAG for testing
    
    def test_check_compliance_high_risk(self):
        """Test compliance check for high risk"""
        risk_data = {
            "transaction_id": "TXN001",
            "score": 0.95
        }
        
        result = self.agent.check_compliance_with_rag(risk_data)
        
        assert result["transaction_id"] == "TXN001"
        assert result["action"] == "hold_and_report"
        assert result["reason"] == "AUSTRAC_threshold_exceeded"
        assert result["compliance_status"] == "requires_review"
    
    def test_check_compliance_low_risk(self):
        """Test compliance check for low risk"""
        risk_data = {
            "transaction_id": "TXN002",
            "score": 0.3
        }
        
        result = self.agent.check_compliance_with_rag(risk_data)
        
        assert result["transaction_id"] == "TXN002"
        assert result["action"] == "monitor"
        assert result["reason"] == "within_normal_parameters"
        assert result["compliance_status"] == "compliant"

class TestRAGEnhancedResilienceAgent:
    """Test cases for Resilience Agent"""
    
    def setup_method(self):
        """Set up test environment"""
        self.agent = RAGEnhancedResilienceAgent()
        self.agent.rag_engine = None  # Disable RAG for testing
    
    def test_take_action_hold_and_report(self):
        """Test taking action for hold and report"""
        compliance_data = {
            "transaction_id": "TXN001",
            "action": "hold_and_report"
        }
        
        result = self.agent.take_action_with_rag(compliance_data)
        
        assert result["transaction_id"] == "TXN001"
        assert "block_transaction" in result["actions_taken"]
        assert "freeze_account_temporarily" in result["actions_taken"]
        assert result["status"] == "investigating"
        assert result["investigation_id"] == "INV_TXN001"
    
    def test_take_action_monitor(self):
        """Test taking action for monitor"""
        compliance_data = {
            "transaction_id": "TXN002",
            "action": "monitor"
        }
        
        result = self.agent.take_action_with_rag(compliance_data)
        
        assert result["transaction_id"] == "TXN002"
        assert result["actions_taken"] == ["monitor"]
        assert result["status"] == "normal"

class TestRAGEnhancedCustomerSentimentAgent:
    """Test cases for Customer Sentiment Agent"""
    
    def setup_method(self):
        """Set up test environment"""
        self.agent = RAGEnhancedCustomerSentimentAgent()
        self.agent.rag_engine = None  # Disable RAG for testing
    
    def test_analyze_negative_sentiment(self):
        """Test analyzing negative sentiment"""
        message = "Why was my transaction blocked? This is ridiculous!"
        
        result = self.agent.analyze_sentiment_with_rag(message)
        
        assert result["sentiment"] == "negative"
        assert result["sentiment_score"] < 0.3
        assert result["urgency"] == "high"
        assert result["action"] == "escalate_to_customer_service"
        assert "ridiculous" in result["keywords"]
    
    def test_analyze_neutral_sentiment(self):
        """Test analyzing neutral sentiment"""
        message = "I would like to know about my account balance"
        
        result = self.agent.analyze_sentiment_with_rag(message)
        
        assert result["sentiment"] == "neutral"
        assert result["urgency"] == "normal"
        assert result["action"] == "monitor"

class TestRAGEnhancedDataPrivacyAgent:
    """Test cases for Data Privacy Agent"""
    
    def setup_method(self):
        """Set up test environment"""
        self.agent = RAGEnhancedDataPrivacyAgent()
        self.agent.rag_engine = None  # Disable RAG for testing
    
    def test_scan_logs_with_pii(self):
        """Test scanning logs with PII"""
        log_entry = "Transaction processed for customer@example.com with SSN 123-45-6789"
        
        result = self.agent.scan_logs_with_rag(log_entry)
        
        assert result["violation"] is True
        assert len(result["violations"]) > 0
        assert "[EMAIL_REDACTED]" in result["sanitized_log"]
        assert "[SSN_REDACTED]" in result["sanitized_log"]
        assert result["severity"] == "medium"
        assert result["action_required"] == "sanitize_and_alert"
    
    def test_scan_logs_without_pii(self):
        """Test scanning logs without PII"""
        log_entry = "Transaction processed successfully with amount $1000"
        
        result = self.agent.scan_logs_with_rag(log_entry)
        
        assert result["violation"] is False
        assert result["violations"] == []
        assert result["sanitized_log"] == log_entry
        assert result["severity"] == "none"
        assert result["action_required"] == "none"

class TestRAGEnhancedKnowledgeAgent:
    """Test cases for Knowledge Agent"""
    
    def setup_method(self):
        """Set up test environment"""
        self.agent = RAGEnhancedKnowledgeAgent()
        self.agent.rag_engine = None  # Disable RAG for testing
    
    def test_generate_report_with_events(self):
        """Test generating report with events"""
        events = [
            {
                "transaction_id": "TXN001",
                "amount": 25000,
                "score": 0.95,
                "actions_taken": ["block_transaction"],
                "sentiment": "negative",
                "urgency": "high",
                "violation": True,
                "violations": ["email_pattern"],
                "severity": "medium"
            }
        ]
        
        result = self.agent.generate_report_with_rag(events)
        
        assert "NFRGuard AI Security Incident Report" in result["report"]
        assert "TXN001" in result["report"]
        assert "$25,000.00" in result["report"]
        assert result["severity"] == "high"
        assert "transaction" in result["summary"]
        assert "risk" in result["summary"]
        assert "customer" in result["summary"]
        assert "privacy" in result["summary"]

class TestRAGEnhancedBankingAssistantAgent:
    """Test cases for Banking Assistant Agent"""
    
    def setup_method(self):
        """Set up test environment"""
        self.agent = RAGEnhancedBankingAssistantAgent()
        self.agent.rag_engine = None  # Disable RAG for testing
    
    def test_handle_transaction_blocked_query(self):
        """Test handling transaction blocked query"""
        message = "My transaction was blocked, what should I do?"
        
        result = self.agent.handle_customer_query_with_rag(message)
        
        assert result["intent"] == "transaction_blocked"
        assert "security review" in result["response"]
        assert "fraud prevention" in result["response"]
        assert len(result["alternatives"]) > 0
        assert result["escalation"] == "automatic"
        assert result["confidence"] > 0.5
    
    def test_handle_performance_query(self):
        """Test handling performance query"""
        message = "Why is the system so slow?"
        
        result = self.agent.handle_customer_query_with_rag(message)
        
        assert result["intent"] == "performance_issue"
        assert "apologize" in result["response"].lower()
        assert len(result["alternatives"]) > 0
        assert result["escalation"] == "none"
    
    def test_handle_general_query(self):
        """Test handling general query"""
        message = "Hello, how are you?"
        
        result = self.agent.handle_customer_query_with_rag(message)
        
        assert result["intent"] == "general_inquiry"
        assert "help" in result["response"].lower()
        assert result["alternatives"] == []
        assert result["escalation"] == "none"

class TestAgentFactory:
    """Test cases for agent factory"""
    
    def test_create_transaction_risk_agent(self):
        """Test creating transaction risk agent"""
        agent = create_rag_enhanced_agent("transaction_risk")
        assert isinstance(agent, RAGEnhancedTransactionRiskAgent)
    
    def test_create_compliance_agent(self):
        """Test creating compliance agent"""
        agent = create_rag_enhanced_agent("compliance")
        assert isinstance(agent, RAGEnhancedComplianceAgent)
    
    def test_create_resilience_agent(self):
        """Test creating resilience agent"""
        agent = create_rag_enhanced_agent("resilience")
        assert isinstance(agent, RAGEnhancedResilienceAgent)
    
    def test_create_customer_sentiment_agent(self):
        """Test creating customer sentiment agent"""
        agent = create_rag_enhanced_agent("customer_sentiment")
        assert isinstance(agent, RAGEnhancedCustomerSentimentAgent)
    
    def test_create_data_privacy_agent(self):
        """Test creating data privacy agent"""
        agent = create_rag_enhanced_agent("data_privacy")
        assert isinstance(agent, RAGEnhancedDataPrivacyAgent)
    
    def test_create_knowledge_agent(self):
        """Test creating knowledge agent"""
        agent = create_rag_enhanced_agent("knowledge")
        assert isinstance(agent, RAGEnhancedKnowledgeAgent)
    
    def test_create_banking_assistant_agent(self):
        """Test creating banking assistant agent"""
        agent = create_rag_enhanced_agent("banking_assistant")
        assert isinstance(agent, RAGEnhancedBankingAssistantAgent)
    
    def test_create_unknown_agent(self):
        """Test creating unknown agent type"""
        with pytest.raises(ValueError):
            create_rag_enhanced_agent("unknown_agent")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
