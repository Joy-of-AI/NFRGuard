#!/usr/bin/env python3
"""
Debug test for RAG system
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag_engine import AustralianBankingRAG

def debug_rag_system():
    """Debug the RAG system"""
    print("🔍 Debugging RAG System")
    print("=" * 30)
    
    # Initialize RAG system
    rag = AustralianBankingRAG(project_id="test-project")
    rag.initialize()
    
    # Test a simple query
    print("Testing simple query...")
    result = rag.query("transaction risk", "transaction_risk")
    
    print(f"Query: {result.query}")
    print(f"Confidence: {result.confidence}")
    print(f"Sources: {result.sources}")
    print(f"Context length: {len(result.context)}")
    print(f"Relevant documents: {len(result.relevant_documents)}")
    
    # Check if mock file exists and has content
    mock_file = Path("mock_vector_documents.json")
    if mock_file.exists():
        import json
        with open(mock_file, 'r') as f:
            docs = json.load(f)
        print(f"Mock file has {len(docs)} documents")
        
        # Check first document structure
        if docs:
            first_doc = docs[0]
            print(f"First doc keys: {list(first_doc.keys())}")
            print(f"First doc metadata: {first_doc.get('metadata', {})}")
    else:
        print("Mock file does not exist")

if __name__ == "__main__":
    debug_rag_system()
