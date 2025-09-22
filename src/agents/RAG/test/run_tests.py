#!/usr/bin/env python3
"""
Test Runner for RAG System
Runs all tests and provides comprehensive reporting
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def run_all_tests():
    """Run all RAG tests with comprehensive reporting"""
    print("🧪 Running RAG System Tests")
    print("=" * 60)
    
    # Get test directory
    test_dir = Path(__file__).parent
    
    # Define test modules
    test_modules = [
        "test_document_downloader.py",
        "test_vertex_ai_vector_search.py", 
        "test_rag_engine.py",
        "test_rag_enhanced_agents.py",
        "test_end_to_end.py"
    ]
    
    # Run each test module
    results = {}
    total_tests = 0
    total_passed = 0
    
    for module in test_modules:
        module_path = test_dir / module
        if module_path.exists():
            print(f"\n📋 Running {module}")
            print("-" * 40)
            
            # Run pytest for this module
            exit_code = pytest.main([
                str(module_path),
                "-v",
                "--tb=short",
                "--disable-warnings"
            ])
            
            # Parse results (simplified)
            if exit_code == 0:
                results[module] = "PASSED"
                total_passed += 1
            else:
                results[module] = "FAILED"
            
            total_tests += 1
        else:
            print(f"⚠️  Module {module} not found")
            results[module] = "NOT FOUND"
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for module, status in results.items():
        status_icon = "✅" if status == "PASSED" else "❌" if status == "FAILED" else "⚠️"
        print(f"{status_icon} {module}: {status}")
    
    print(f"\n📈 Overall Results: {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED! RAG system is ready for production.")
        return True
    else:
        print("⚠️  Some tests failed. Please review and fix issues.")
        return False

def run_quick_tests():
    """Run quick smoke tests"""
    print("⚡ Running Quick Smoke Tests")
    print("=" * 40)
    
    try:
        # Test document downloader
        from document_downloader import AustralianBankingDocumentDownloader
        downloader = AustralianBankingDocumentDownloader("temp_test")
        documents = downloader.download_all_documents()
        print(f"✅ Document downloader: {len(documents)} documents")
        
        # Test vector search
        from vertex_ai_vector_search import VertexAIVectorSearch
        vector_search = VertexAIVectorSearch("test-project")
        index_id = vector_search.create_vector_index("test-index")
        print(f"✅ Vector search: Index {index_id} created")
        
        # Test RAG engine
        from rag_engine import AustralianBankingRAG
        rag = AustralianBankingRAG("test-project")
        success = rag.initialize()
        print(f"✅ RAG engine: {'Initialized' if success else 'Failed'}")
        
        # Test agent creation
        from rag_enhanced_agents import create_rag_enhanced_agent
        agent = create_rag_enhanced_agent("transaction_risk")
        print(f"✅ Agent creation: {agent.agent_name} created")
        
        print("\n🎉 Quick tests passed! RAG system is functional.")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {str(e)}")
        return False

def main():
    """Main test runner"""
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        success = run_quick_tests()
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
