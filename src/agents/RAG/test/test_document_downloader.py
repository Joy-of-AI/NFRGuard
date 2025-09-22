#!/usr/bin/env python3
"""
Tests for Document Downloader
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from document_downloader import AustralianBankingDocumentDownloader, RegulatoryDocument

class TestDocumentDownloader:
    """Test cases for document downloader"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = AustralianBankingDocumentDownloader(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_downloader_initialization(self):
        """Test document downloader initialization"""
        assert self.downloader is not None
        assert Path(self.temp_dir).exists()
        assert len(self.downloader.document_sources) == 4
        assert "asic" in self.downloader.document_sources
        assert "apra" in self.downloader.document_sources
        assert "austrac" in self.downloader.document_sources
        assert "afca" in self.downloader.document_sources
    
    def test_download_all_documents(self):
        """Test downloading all documents"""
        documents = self.downloader.download_all_documents()
        
        assert len(documents) > 0
        assert len(documents) <= 6  # Maximum expected documents
        
        # Check document types
        regulators = [doc.regulator for doc in documents]
        assert "asic" in regulators
        assert "apra" in regulators
        assert "austrac" in regulators
        assert "afca" in regulators
    
    def test_document_structure(self):
        """Test document structure"""
        documents = self.downloader.download_all_documents()
        
        for doc in documents:
            assert isinstance(doc, RegulatoryDocument)
            assert doc.title
            assert doc.regulator
            assert doc.content
            assert doc.sections
            assert doc.agent_focus
            assert doc.relevance
            assert doc.document_type
            assert doc.metadata
    
    def test_asic_document_content(self):
        """Test ASIC document content"""
        documents = self.downloader.download_all_documents()
        asic_docs = [doc for doc in documents if doc.regulator == "asic"]
        
        assert len(asic_docs) > 0
        asic_doc = asic_docs[0]
        
        assert "risk appetite" in asic_doc.content.lower()
        assert "governance" in asic_doc.content.lower()
        assert "fraud management" in asic_doc.content.lower()
        assert "compliance" in asic_doc.agent_focus
    
    def test_apra_document_content(self):
        """Test APRA document content"""
        documents = self.downloader.download_all_documents()
        apra_docs = [doc for doc in documents if doc.regulator == "apra"]
        
        assert len(apra_docs) > 0
        
        # Check CPS 230 content
        cps_docs = [doc for doc in apra_docs if "CPS 230" in doc.title]
        assert len(cps_docs) > 0
        cps_doc = cps_docs[0]
        assert "operational risk" in cps_doc.content.lower()
        assert "transaction_risk" in cps_doc.agent_focus
        
        # Check CPG 230 content
        cpg_docs = [doc for doc in apra_docs if "CPG 230" in doc.title]
        assert len(cpg_docs) > 0
        cpg_doc = cpg_docs[0]
        assert "incident handling" in cpg_doc.content.lower()
        assert "resilience" in cpg_doc.agent_focus
    
    def test_austrac_document_content(self):
        """Test AUSTRAC document content"""
        documents = self.downloader.download_all_documents()
        austrac_docs = [doc for doc in documents if doc.regulator == "austrac"]
        
        assert len(austrac_docs) > 0
        austrac_doc = austrac_docs[0]
        
        assert "aml/ctf" in austrac_doc.content.lower()
        assert "suspicious" in austrac_doc.content.lower()
        assert "transaction_risk" in austrac_doc.agent_focus
        assert "compliance" in austrac_doc.agent_focus
    
    def test_afca_document_content(self):
        """Test AFCA document content"""
        documents = self.downloader.download_all_documents()
        afca_docs = [doc for doc in documents if doc.regulator == "afca"]
        
        assert len(afca_docs) > 0
        
        # Check rules document
        rules_docs = [doc for doc in afca_docs if "rules" in doc.title.lower()]
        assert len(rules_docs) > 0
        rules_doc = rules_docs[0]
        assert "complaint" in rules_doc.content.lower()
        assert "customer" in rules_doc.content.lower()
        assert "banking_assistant" in rules_doc.agent_focus
    
    def test_document_saving(self):
        """Test that documents are saved to files"""
        documents = self.downloader.download_all_documents()
        
        # Check that files were created
        saved_files = list(Path(self.temp_dir).glob("*.json"))
        assert len(saved_files) == len(documents)
        
        # Check file content
        for file_path in saved_files:
            import json
            with open(file_path, 'r') as f:
                doc_data = json.load(f)
            
            assert "title" in doc_data
            assert "regulator" in doc_data
            assert "content" in doc_data
            assert "metadata" in doc_data
    
    def test_agent_focus_coverage(self):
        """Test that all agent types are covered"""
        documents = self.downloader.download_all_documents()
        
        all_agent_focus = []
        for doc in documents:
            all_agent_focus.extend(doc.agent_focus)
        
        expected_agents = [
            "transaction_risk", "compliance", "resilience",
            "customer_sentiment", "data_privacy", "knowledge", "banking_assistant"
        ]
        
        for agent in expected_agents:
            assert agent in all_agent_focus, f"Agent {agent} not covered in any document"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
