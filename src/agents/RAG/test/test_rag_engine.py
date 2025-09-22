#!/usr/bin/env python3
"""
Tests for RAG Engine
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag_engine import AustralianBankingRAG, DocumentProcessor, RAGQuery, RAGResult

class TestDocumentProcessor:
    """Test cases for Document Processor"""
    
    def setup_method(self):
        """Set up test environment"""
        self.processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
    
    def test_processor_initialization(self):
        """Test processor initialization"""
        assert self.processor is not None
        assert self.processor.chunk_size == 500
        assert self.processor.chunk_overlap == 100
    
    def test_chunk_text(self):
        """Test text chunking"""
        # Short text should not be chunked
        short_text = "This is a short text."
        chunks = self.processor._chunk_text(short_text)
        assert len(chunks) == 1
        assert chunks[0] == short_text
        
        # Long text should be chunked
        long_text = "This is a long text. " * 100  # Much longer than 500 chars
        chunks = self.processor._chunk_text(long_text)
        assert len(chunks) > 1
        
        # Check that chunks don't exceed size limit
        for chunk in chunks:
            assert len(chunk) <= 500 + 50  # Allow some margin
    
    def test_generate_chunk_id(self):
        """Test chunk ID generation"""
        from document_downloader import RegulatoryDocument
        
        doc = RegulatoryDocument(
            title="Test Document",
            regulator="test",
            url="http://test.com",
            content="Test content",
            sections=["test"],
            agent_focus=["test"],
            relevance="high",
            document_type="test",
            metadata={}
        )
        
        chunk_id = self.processor._generate_chunk_id(doc, 0)
        
        assert chunk_id is not None
        assert "test_test_" in chunk_id
        assert "_0" in chunk_id

class TestRAGEngine:
    """Test cases for RAG Engine"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.rag = AustralianBankingRAG(project_id="test-project", download_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_rag_initialization(self):
        """Test RAG initialization"""
        assert self.rag is not None
        assert self.rag.project_id == "test-project"
        assert Path(self.temp_dir).exists()
        assert self.rag.document_downloader is not None
        assert self.rag.vector_search is not None
        assert self.rag.document_processor is not None
    
    def test_agent_query_templates(self):
        """Test agent query templates"""
        assert len(self.rag.agent_query_templates) == 7
        
        expected_agents = [
            "transaction_risk", "compliance", "resilience",
            "customer_sentiment", "data_privacy", "knowledge", "banking_assistant"
        ]
        
        for agent in expected_agents:
            assert agent in self.rag.agent_query_templates
            template = self.rag.agent_query_templates[agent]
            assert "templates" in template
            assert "filters" in template
            assert len(template["templates"]) > 0
    
    def test_setup_vector_search(self):
        """Test vector search setup"""
        success = self.rag.setup_vector_search()
        
        assert success is True
        assert self.rag.index_id is not None
        assert self.rag.index_endpoint_id is not None
        assert self.rag.deployed_index_id is not None
    
    def test_load_documents(self):
        """Test document loading"""
        # First set up vector search
        self.rag.setup_vector_search()
        
        # Load documents
        success = self.rag.load_documents()
        
        assert success is True
    
    def test_build_enhanced_query(self):
        """Test enhanced query building"""
        # Test with context
        context = {
            "transaction_amount": 25000,
            "risk_level": "high"
        }
        
        enhanced_query = self.rag._build_enhanced_query(
            "transaction monitoring",
            "transaction_risk",
            context
        )
        
        assert "25000" in enhanced_query
        assert "high" in enhanced_query
        assert "transaction monitoring" in enhanced_query
    
    def test_build_context(self):
        """Test context building"""
        from vertex_ai_vector_search import SearchResult
        
        # Create mock search results
        results = [
            SearchResult(
                document_id="doc1",
                content="This is document 1 content about banking regulations",
                score=0.9,
                metadata={"regulator": "asic", "title": "ASIC Guidance"}
            ),
            SearchResult(
                document_id="doc2",
                content="This is document 2 content about compliance requirements",
                score=0.8,
                metadata={"regulator": "apra", "title": "APRA Standard"}
            )
        ]
        
        context = self.rag._build_context(results)
        
        assert "ASIC" in context
        assert "APRA" in context
        assert "banking regulations" in context
        assert "compliance requirements" in context
    
    def test_calculate_confidence(self):
        """Test confidence calculation"""
        from vertex_ai_vector_search import SearchResult
        
        # High confidence results
        high_results = [
            SearchResult("doc1", "content1", 0.9, {}),
            SearchResult("doc2", "content2", 0.8, {})
        ]
        
        confidence = self.rag._calculate_confidence(high_results)
        assert confidence > 0.8
        
        # Low confidence results
        low_results = [
            SearchResult("doc1", "content1", 0.3, {}),
            SearchResult("doc2", "content2", 0.2, {})
        ]
        
        confidence = self.rag._calculate_confidence(low_results)
        assert confidence < 0.3
        
        # Empty results
        confidence = self.rag._calculate_confidence([])
        assert confidence == 0.0
    
    def test_query(self):
        """Test RAG query"""
        # Set up vector search and load documents
        self.rag.setup_vector_search()
        self.rag.load_documents()
        
        # Test query
        result = self.rag.query(
            "transaction risk monitoring",
            "transaction_risk",
            {"transaction_amount": 15000}
        )
        
        assert isinstance(result, RAGResult)
        assert result.query is not None
        assert result.context is not None
        assert isinstance(result.confidence, float)
        assert isinstance(result.sources, list)
    
    def test_get_agent_guidance(self):
        """Test getting agent guidance"""
        # Set up vector search and load documents
        self.rag.setup_vector_search()
        self.rag.load_documents()
        
        # Test guidance for transaction risk agent
        guidance = self.rag.get_agent_guidance(
            "transaction_risk",
            {
                "transaction_amount": 50000,
                "risk_level": "high"
            }
        )
        
        assert "Australian banking regulations" in guidance
        assert "Confidence:" in guidance
        assert "Sources:" in guidance
    
    def test_initialize(self):
        """Test complete initialization"""
        success = self.rag.initialize()
        
        assert success is True
        assert self.rag.index_id is not None
        assert self.rag.index_endpoint_id is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
