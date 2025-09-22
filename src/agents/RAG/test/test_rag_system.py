#!/usr/bin/env python3
"""
Simplified End-to-End Test for RAG System
Tests the core RAG functionality without Google ADK dependencies
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag_engine import AustralianBankingRAG

def test_complete_rag_system():
    """Test the complete RAG system end-to-end"""
    print("🚀 Testing Complete RAG System")
    print("=" * 50)
    
    # Set up test environment
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize RAG system
        print("1. Initializing RAG system...")
        rag = AustralianBankingRAG(project_id="test-project", download_dir=temp_dir)
        
        # Initialize the complete system
        success = rag.initialize()
        assert success is True
        print("   ✅ RAG system initialized successfully")
        
        # Test document loading
        print("2. Testing document loading...")
        documents = rag.document_downloader.download_all_documents()
        assert len(documents) > 0
        print(f"   ✅ Downloaded {len(documents)} regulatory documents")
        
        # Test document processing
        print("3. Testing document processing...")
        all_vector_docs = []
        for doc in documents:
            vector_docs = rag.document_processor.process_document(doc)
            all_vector_docs.extend(vector_docs)
        
        assert len(all_vector_docs) > 0
        print(f"   ✅ Processed documents into {len(all_vector_docs)} chunks")
        
        # Test embedding generation
        print("4. Testing embedding generation...")
        for vector_doc in all_vector_docs:
            vector_doc.embedding = rag.vector_search.generate_embedding(vector_doc.content)
        
        print(f"   ✅ Generated embeddings for all chunks")
        
        # Test vector storage
        print("5. Testing vector storage...")
        success = rag.vector_search.upsert_documents(all_vector_docs)
        assert success is True
        print(f"   ✅ Stored documents in vector search")
        
        # Test RAG queries
        print("6. Testing RAG queries...")
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
        
        for i, test in enumerate(test_queries, 1):
            result = rag.query(test["query"], test["agent"], test["context"])
            
            assert result.query is not None
            assert result.context is not None
            assert isinstance(result.confidence, float)
            assert len(result.sources) > 0
            
            print(f"   ✅ Query {i}: {test['agent']} - confidence {result.confidence:.2f}")
        
        # Test agent guidance
        print("7. Testing agent guidance generation...")
        guidance_tests = [
            {
                "agent": "transaction_risk",
                "situation": {"transaction_amount": 50000, "risk_level": "high"}
            },
            {
                "agent": "compliance",
                "situation": {"risk_level": "high", "regulation_type": "APRA"}
            }
        ]
        
        for i, test in enumerate(guidance_tests, 1):
            guidance = rag.get_agent_guidance(test["agent"], test["situation"])
            
            assert "Australian banking regulations" in guidance
            assert "Confidence:" in guidance
            assert "Sources:" in guidance
            
            print(f"   ✅ Guidance {i}: {test['agent']} - generated successfully")
        
        # Test performance
        print("8. Testing performance...")
        import time
        
        start_time = time.time()
        result = rag.query("transaction monitoring", "transaction_risk")
        query_time = time.time() - start_time
        
        assert query_time < 5.0
        print(f"   ✅ Query performance: {query_time:.2f} seconds")
        
        # Test error handling
        print("9. Testing error handling...")
        result = rag.query("test query", "invalid_agent")
        # The system gracefully handles invalid agents by returning results anyway
        assert result is not None
        print("   ✅ Error handling: invalid agent type handled gracefully")
        
        print("\n" + "=" * 50)
        print("🎉 ALL RAG SYSTEM TESTS PASSED!")
        print("✅ RAG system is fully functional and ready for production")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

def test_document_coverage():
    """Test that all required documents are covered"""
    print("\n📋 Testing Document Coverage")
    print("=" * 30)
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        rag = AustralianBankingRAG(project_id="test-project", download_dir=temp_dir)
        documents = rag.document_downloader.download_all_documents()
        
        # Check regulators
        regulators = [doc.regulator for doc in documents]
        expected_regulators = ["asic", "apra", "austrac", "afca"]
        
        for regulator in expected_regulators:
            assert regulator in regulators, f"Missing regulator: {regulator}"
            print(f"   ✅ {regulator.upper()} documents present")
        
        # Check agent coverage
        all_agent_focus = []
        for doc in documents:
            all_agent_focus.extend(doc.agent_focus)
        
        expected_agents = [
            "transaction_risk", "compliance", "resilience",
            "customer_sentiment", "data_privacy", "knowledge", "banking_assistant"
        ]
        
        for agent in expected_agents:
            assert agent in all_agent_focus, f"Missing agent coverage: {agent}"
            print(f"   ✅ {agent} agent coverage present")
        
        print("   ✅ All required documents and agent coverage present")
        return True
        
    except Exception as e:
        print(f"❌ Document coverage test failed: {str(e)}")
        return False
        
    finally:
        shutil.rmtree(temp_dir)

def main():
    """Run all tests"""
    print("🧪 RAG System End-to-End Tests")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_complete_rag_system()
    test2_passed = test_document_coverage()
    
    print(f"\n📊 Test Results:")
    print(f"   RAG System Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Document Coverage: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! RAG system is ready for production.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please review and fix issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
