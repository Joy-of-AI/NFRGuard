#!/usr/bin/env python3
"""
Tests for Vertex AI Vector Search
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from vertex_ai_vector_search import VertexAIVectorSearch, VectorDocument, SearchResult

class TestVertexAIVectorSearch:
    """Test cases for Vertex AI Vector Search"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.vector_search = VertexAIVectorSearch(project_id="test-project")
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_vector_search_initialization(self):
        """Test vector search initialization"""
        assert self.vector_search is not None
        assert self.vector_search.project_id == "test-project"
        assert self.vector_search.location == "australia-southeast1"
    
    def test_create_vector_index(self):
        """Test creating vector index"""
        index_id = self.vector_search.create_vector_index("test-index")
        
        assert index_id is not None
        assert "mock_index" in index_id or "index" in index_id
        assert self.vector_search.index_id == index_id
    
    def test_create_index_endpoint(self):
        """Test creating index endpoint"""
        endpoint_id = self.vector_search.create_index_endpoint("test-endpoint")
        
        assert endpoint_id is not None
        assert "mock_endpoint" in endpoint_id or "endpoint" in endpoint_id
        assert self.vector_search.index_endpoint_id == endpoint_id
    
    def test_deploy_index(self):
        """Test deploying index"""
        index_id = "test-index-123"
        endpoint_id = "test-endpoint-456"
        deployed_id = self.vector_search.deploy_index(index_id, endpoint_id, "deployed-test")
        
        assert deployed_id is not None
        assert deployed_id == "deployed-test"
    
    def test_generate_embedding(self):
        """Test generating embeddings"""
        text = "This is a test document about banking regulations"
        embedding = self.vector_search.generate_embedding(text)
        
        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) == 768  # Standard embedding size
        assert all(isinstance(x, float) for x in embedding)
        
        # Test that same text produces same embedding
        embedding2 = self.vector_search.generate_embedding(text)
        assert embedding == embedding2
    
    def test_upsert_documents(self):
        """Test upserting documents"""
        # Create test documents
        documents = [
            VectorDocument(
                id="doc1",
                content="Banking regulation document 1",
                embedding=[0.1] * 768,
                metadata={"regulator": "asic", "type": "guidance"}
            ),
            VectorDocument(
                id="doc2",
                content="Banking regulation document 2",
                embedding=[0.2] * 768,
                metadata={"regulator": "apra", "type": "standard"}
            )
        ]
        
        success = self.vector_search.upsert_documents(documents)
        
        assert success is True
        
        # Check that mock file was created
        mock_file = Path("mock_vector_documents.json")
        if mock_file.exists():
            import json
            with open(mock_file, 'r') as f:
                stored_docs = json.load(f)
            
            assert len(stored_docs) == 2
            assert stored_docs[0]["id"] == "doc1"
            assert stored_docs[1]["id"] == "doc2"
    
    def test_similarity_search(self):
        """Test similarity search"""
        # First upsert some documents
        documents = [
            VectorDocument(
                id="risk_doc",
                content="Transaction risk monitoring AUSTRAC AML/CTF requirements",
                embedding=[0.1, 0.2, 0.3] + [0.0] * 765,
                metadata={"regulator": "austrac", "agent_focus": "transaction_risk"}
            ),
            VectorDocument(
                id="compliance_doc",
                content="APRA CPS 230 operational risk management compliance",
                embedding=[0.4, 0.5, 0.6] + [0.0] * 765,
                metadata={"regulator": "apra", "agent_focus": "compliance"}
            )
        ]
        
        self.vector_search.upsert_documents(documents)
        
        # Test search without filter
        results = self.vector_search.similarity_search("transaction risk monitoring", top_k=2)
        
        assert len(results) > 0
        assert len(results) <= 2
        
        for result in results:
            assert isinstance(result, SearchResult)
            assert result.document_id
            assert result.content
            assert isinstance(result.score, float)
            assert result.metadata
    
    def test_similarity_search_with_filter(self):
        """Test similarity search with filter"""
        # First upsert some documents
        documents = [
            VectorDocument(
                id="risk_doc",
                content="Transaction risk monitoring AUSTRAC AML/CTF requirements",
                embedding=[0.1, 0.2, 0.3] + [0.0] * 765,
                metadata={"regulator": "austrac", "agent_focus": "transaction_risk"}
            ),
            VectorDocument(
                id="compliance_doc",
                content="APRA CPS 230 operational risk management compliance",
                embedding=[0.4, 0.5, 0.6] + [0.0] * 765,
                metadata={"regulator": "apra", "agent_focus": "compliance"}
            )
        ]
        
        self.vector_search.upsert_documents(documents)
        
        # Test search with filter
        filter_dict = {"agent_focus": "transaction_risk"}
        results = self.vector_search.similarity_search(
            "transaction risk monitoring",
            top_k=2,
            filter_dict=filter_dict
        )
        
        assert len(results) > 0
        
        # Check that all results match the filter
        for result in results:
            assert "transaction_risk" in result.metadata.get("agent_focus", [])
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        vec3 = [0.0, 1.0, 0.0]
        
        # Same vectors should have similarity of 1
        similarity1 = self.vector_search._cosine_similarity(vec1, vec2)
        assert abs(similarity1 - 1.0) < 0.001
        
        # Orthogonal vectors should have similarity of 0
        similarity2 = self.vector_search._cosine_similarity(vec1, vec3)
        assert abs(similarity2 - 0.0) < 0.001
    
    def test_filter_matching(self):
        """Test filter matching"""
        metadata = {
            "regulator": "asic",
            "agent_focus": ["compliance", "risk"],
            "type": "guidance"
        }
        
        # Test exact match
        filter1 = {"regulator": "asic"}
        assert self.vector_search._matches_filter(metadata, filter1) is True
        
        # Test list match
        filter2 = {"agent_focus": ["compliance"]}
        assert self.vector_search._matches_filter(metadata, filter2) is True
        
        # Test non-match
        filter3 = {"regulator": "apra"}
        assert self.vector_search._matches_filter(metadata, filter3) is False
        
        # Test multiple conditions
        filter4 = {"regulator": "asic", "type": "guidance"}
        assert self.vector_search._matches_filter(metadata, filter4) is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
