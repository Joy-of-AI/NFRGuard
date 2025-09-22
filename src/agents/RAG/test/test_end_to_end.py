#!/usr/bin/env python3
"""
End-to-End Tests for RAG System
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag_engine import AustralianBankingRAG
from rag_enhanced_agents import (
    create_rag_enhanced_agent, RAGEnhancedTransactionRiskAgent,
    RAGEnhancedComplianceAgent, RAGEnhancedResilienceAgent
)

class TestEndToEndRAG:
    """End-to-end tests for the complete RAG system"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.rag = AustralianBankingRAG(project_id="test-project", download_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_rag_initialization(self):
        """Test complete RAG system initialization"""
        print("\n=== Testing Complete RAG System Initialization ===")
        
        # Initialize the complete system
        success = self.rag.initialize()
        
        assert success is True
        assert self.rag.index_id is not None
        assert self.rag.index_endpoint_id is not None
        assert self.rag.deployed_index_id is not None
        
        print(f"✓ RAG system initialized successfully")
        print(f"  - Index ID: {self.rag.index_id}")
        print(f"  - Endpoint ID: {self.rag.index_endpoint_id}")
        print(f"  - Deployed Index ID: {self.rag.deployed_index_id}")
    
    def test_document_loading_and_processing(self):
        """Test document loading and processing"""
        print("\n=== Testing Document Loading and Processing ===")
        
        # Download documents
        documents = self.rag.document_downloader.download_all_documents()
        assert len(documents) > 0
        print(f"✓ Downloaded {len(documents)} regulatory documents")
        
        # Process documents
        all_vector_docs = []
        for doc in documents:
            vector_docs = self.rag.document_processor.process_document(doc)
            all_vector_docs.extend(vector_docs)
        
        assert len(all_vector_docs) > 0
        print(f"✓ Processed documents into {len(all_vector_docs)} chunks")
        
        # Generate embeddings
        for vector_doc in all_vector_docs:
            vector_doc.embedding = self.rag.vector_search.generate_embedding(vector_doc.content)
        
        print(f"✓ Generated embeddings for all chunks")
        
        # Store in vector search
        success = self.rag.vector_search.upsert_documents(all_vector_docs)
        assert success is True
        print(f"✓ Stored documents in vector search")
    
    def test_rag_query_functionality(self):
        """Test RAG query functionality"""
        print("\n=== Testing RAG Query Functionality ===")
        
        # Initialize system
        self.rag.initialize()
        
        # Test different types of queries
        test_queries = [
            {
                "query": "transaction risk monitoring AUSTRAC",
                "agent": "transaction_risk",
                "context": {"transaction_amount": 25000}
            },
            {
                "query": "compliance requirements APRA CPS 230",
                "agent": "compliance",
                "context": {"regulation_type": "APRA"}
            },
            {
                "query": "customer complaint handling AFCA",
                "agent": "customer_sentiment",
                "context": {"complaint_type": "transaction_blocked"}
            }
        ]
        
        for test in test_queries:
            result = self.rag.query(test["query"], test["agent"], test["context"])
            
            assert result.query is not None
            assert result.context is not None
            assert isinstance(result.confidence, float)
            assert len(result.sources) > 0
            
            print(f"✓ Query '{test['query']}' for {test['agent']}: confidence {result.confidence:.2f}")
    
    def test_agent_guidance_generation(self):
        """Test agent guidance generation"""
        print("\n=== Testing Agent Guidance Generation ===")
        
        # Initialize system
        self.rag.initialize()
        
        # Test guidance for different agents
        guidance_tests = [
            {
                "agent": "transaction_risk",
                "situation": {"transaction_amount": 50000, "risk_level": "high"}
            },
            {
                "agent": "compliance",
                "situation": {"risk_level": "high", "regulation_type": "APRA"}
            },
            {
                "agent": "customer_sentiment",
                "situation": {"complaint_type": "transaction_blocked", "sentiment": "negative"}
            }
        ]
        
        for test in guidance_tests:
            guidance = self.rag.get_agent_guidance(test["agent"], test["situation"])
            
            assert "Australian banking regulations" in guidance
            assert "Confidence:" in guidance
            assert "Sources:" in guidance
            
            print(f"✓ Generated guidance for {test['agent']}")
    
    def test_rag_enhanced_agent_workflow(self):
        """Test complete workflow with RAG-enhanced agents"""
        print("\n=== Testing RAG-Enhanced Agent Workflow ===")
        
        # Initialize RAG system
        self.rag.initialize()
        
        # Create RAG-enhanced agents
        risk_agent = RAGEnhancedTransactionRiskAgent()
        compliance_agent = RAGEnhancedComplianceAgent()
        resilience_agent = RAGEnhancedResilienceAgent()
        
        # Set the RAG engine for agents
        risk_agent.rag_engine = self.rag
        compliance_agent.rag_engine = self.rag
        resilience_agent.rag_engine = self.rag
        
        # Test complete workflow
        transaction_data = {
            "transaction_id": "E2E_TEST_001",
            "amount": 75000
        }
        
        print(f"Testing transaction: {transaction_data}")
        
        # Step 1: Risk analysis
        risk_result = risk_agent.analyze_transaction_with_rag(transaction_data)
        assert risk_result["transaction_id"] == "E2E_TEST_001"
        assert risk_result["suspicious"] is True
        assert risk_result["score"] == 0.95
        print(f"✓ Risk analysis: {risk_result['reason']}")
        
        # Step 2: Compliance check
        compliance_result = compliance_agent.check_compliance_with_rag(risk_result)
        assert compliance_result["transaction_id"] == "E2E_TEST_001"
        assert compliance_result["action"] == "hold_and_report"
        print(f"✓ Compliance check: {compliance_result['action']}")
        
        # Step 3: Resilience action
        resilience_result = resilience_agent.take_action_with_rag(compliance_result)
        assert resilience_result["transaction_id"] == "E2E_TEST_001"
        assert "block_transaction" in resilience_result["actions_taken"]
        print(f"✓ Resilience action: {resilience_result['status']}")
        
        print("✓ Complete workflow executed successfully")
    
    def test_agent_factory_functionality(self):
        """Test agent factory functionality"""
        print("\n=== Testing Agent Factory Functionality ===")
        
        # Test creating all agent types
        agent_types = [
            "transaction_risk", "compliance", "resilience",
            "customer_sentiment", "data_privacy", "knowledge", "banking_assistant"
        ]
        
        for agent_type in agent_types:
            agent = create_rag_enhanced_agent(agent_type)
            assert agent is not None
            assert agent.agent_name == agent_type
            print(f"✓ Created {agent_type} agent")
        
        # Test error handling
        try:
            create_rag_enhanced_agent("unknown_agent")
            assert False, "Should have raised ValueError"
        except ValueError:
            print("✓ Correctly handled unknown agent type")
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        print("\n=== Testing Performance Benchmarks ===")
        
        # Initialize system
        self.rag.initialize()
        
        import time
        
        # Test query performance
        start_time = time.time()
        result = self.rag.query("transaction monitoring", "transaction_risk")
        query_time = time.time() - start_time
        
        assert query_time < 5.0  # Should complete within 5 seconds
        print(f"✓ Query performance: {query_time:.2f} seconds")
        
        # Test embedding generation performance
        start_time = time.time()
        embedding = self.rag.vector_search.generate_embedding("Test document for performance")
        embedding_time = time.time() - start_time
        
        assert embedding_time < 2.0  # Should complete within 2 seconds
        print(f"✓ Embedding generation: {embedding_time:.2f} seconds")
    
    def test_error_handling(self):
        """Test error handling"""
        print("\n=== Testing Error Handling ===")
        
        # Test with invalid agent type
        result = self.rag.query("test query", "invalid_agent")
        assert result.confidence == 0.0
        print("✓ Handled invalid agent type gracefully")
        
        # Test with empty query
        result = self.rag.query("", "transaction_risk")
        assert result is not None
        print("✓ Handled empty query gracefully")
        
        # Test with None context
        result = self.rag.query("test query", "transaction_risk", None)
        assert result is not None
        print("✓ Handled None context gracefully")

def main():
    """Run all end-to-end tests"""
    print("🚀 Starting End-to-End RAG System Tests")
    print("=" * 60)
    
    # Run tests
    test_instance = TestEndToEndRAG()
    test_instance.setup_method()
    
    try:
        # Run all test methods
        test_methods = [
            "test_complete_rag_initialization",
            "test_document_loading_and_processing", 
            "test_rag_query_functionality",
            "test_agent_guidance_generation",
            "test_rag_enhanced_agent_workflow",
            "test_agent_factory_functionality",
            "test_performance_benchmarks",
            "test_error_handling"
        ]
        
        for method_name in test_methods:
            method = getattr(test_instance, method_name)
            try:
                method()
                print(f"✅ {method_name} PASSED")
            except Exception as e:
                print(f"❌ {method_name} FAILED: {str(e)}")
                raise
        
        print("\n" + "=" * 60)
        print("🎉 ALL END-TO-END TESTS PASSED!")
        print("✅ RAG system is fully functional")
        
    finally:
        test_instance.teardown_method()

if __name__ == "__main__":
    main()
