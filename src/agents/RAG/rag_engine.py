#!/usr/bin/env python3
"""
RAG Engine for Australian Banking Regulatory Documents
Combines document processing, vector search, and retrieval-augmented generation
"""

import os
import json
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

from document_downloader import AustralianBankingDocumentDownloader, RegulatoryDocument
from vertex_ai_vector_search import VertexAIVectorSearch, VectorDocument, SearchResult

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RAGQuery:
    """Represents a RAG query"""
    query_text: str
    agent_type: str
    context: Dict[str, Any]
    filters: Dict[str, Any]

@dataclass
class RAGResult:
    """Represents a RAG result"""
    query: str
    relevant_documents: List[SearchResult]
    context: str
    confidence: float
    sources: List[str]

class DocumentProcessor:
    """Processes and chunks documents for vector storage"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def process_document(self, document: RegulatoryDocument) -> List[VectorDocument]:
        """Process a regulatory document into chunks for vector storage"""
        chunks = self._chunk_text(document.content)
        
        vector_documents = []
        for i, chunk in enumerate(chunks):
            # Create unique ID for chunk
            chunk_id = self._generate_chunk_id(document, i)
            
            # Create metadata
            metadata = {
                "title": document.title,
                "regulator": document.regulator,
                "document_type": document.document_type,
                "sections": document.sections,
                "agent_focus": document.agent_focus,
                "relevance": document.relevance,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "url": document.url,
                "content": chunk  # Store content in metadata for easy retrieval
            }
            
            # Create vector document
            vector_doc = VectorDocument(
                id=chunk_id,
                content=chunk,
                embedding=[],  # Will be generated later
                metadata=metadata
            )
            
            vector_documents.append(vector_doc)
            
        return vector_documents
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 200 characters
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + self.chunk_size - 200:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
        return chunks
    
    def _generate_chunk_id(self, document: RegulatoryDocument, chunk_index: int) -> str:
        """Generate unique ID for document chunk"""
        content_hash = hashlib.md5(document.content.encode()).hexdigest()[:8]
        return f"{document.regulator}_{document.document_type}_{content_hash}_{chunk_index}"

class AustralianBankingRAG:
    """Main RAG engine for Australian banking regulations"""
    
    def __init__(self, project_id: str = None, download_dir: str = "documents"):
        self.project_id = project_id
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.document_downloader = AustralianBankingDocumentDownloader(str(self.download_dir))
        self.vector_search = VertexAIVectorSearch(project_id)
        self.document_processor = DocumentProcessor()
        
        # RAG configuration
        self.index_id = None
        self.index_endpoint_id = None
        self.deployed_index_id = None
        
        # Agent-specific query templates
        self.agent_query_templates = {
            "transaction_risk": {
                "templates": [
                    "suspicious transaction monitoring AUSTRAC AML/CTF {amount}",
                    "transaction risk assessment {risk_level} amount {amount}",
                    "AML/CTF compliance requirements transaction {amount}"
                ],
                "filters": {"agent_focus": ["risk", "compliance"]}
            },
            "compliance": {
                "templates": [
                    "compliance requirements APRA CPS 230 operational risk {risk_level}",
                    "regulatory compliance obligations {regulation_type}",
                    "operational risk management APRA CPS 230"
                ],
                "filters": {"agent_focus": ["compliance"]}
            },
            "resilience": {
                "templates": [
                    "incident management APRA CPG 230 operational risk",
                    "business continuity management resilience {threat_type}",
                    "operational risk incident handling procedures"
                ],
                "filters": {"agent_focus": ["resilience"]}
            },
            "customer_sentiment": {
                "templates": [
                    "customer complaint handling AFCA guidelines {complaint_type}",
                    "customer communication standards AFCA {sentiment}",
                    "dispute resolution AFCA customer service"
                ],
                "filters": {"agent_focus": ["banking_assistant"]}
            },
            "data_privacy": {
                "templates": [
                    "data privacy obligations AUSTRAC record keeping",
                    "customer data protection requirements {data_type}",
                    "privacy compliance AML/CTF data handling"
                ],
                "filters": {"agent_focus": ["compliance"]}
            },
            "knowledge": {
                "templates": [
                    "regulatory guidance summary {regulator} {topic}",
                    "compliance requirements explanation {requirement_type}",
                    "banking regulations overview {regulation_area}"
                ],
                "filters": {"agent_focus": ["knowledge"]}
            },
            "banking_assistant": {
                "templates": [
                    "customer service guidelines AFCA {service_type}",
                    "banking assistance procedures {assistance_type}",
                    "customer communication AFCA standards"
                ],
                "filters": {"agent_focus": ["banking_assistant"]}
            }
        }
    
    def setup_vector_search(self) -> bool:
        """Set up vector search infrastructure"""
        try:
            # Create vector index
            self.index_id = self.vector_search.create_vector_index()
            
            # Create index endpoint
            self.index_endpoint_id = self.vector_search.create_index_endpoint()
            
            # Deploy index
            self.deployed_index_id = self.vector_search.deploy_index(
                self.index_id, 
                self.index_endpoint_id
            )
            
            logger.info("Vector search infrastructure set up successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set up vector search: {e}")
            return False
    
    def load_documents(self) -> bool:
        """Load and process all regulatory documents"""
        try:
            # Download documents
            logger.info("Downloading regulatory documents...")
            documents = self.document_downloader.download_all_documents()
            
            if not documents:
                logger.error("No documents downloaded")
                return False
            
            # Process documents into chunks
            logger.info("Processing documents into chunks...")
            all_vector_docs = []
            
            for doc in documents:
                vector_docs = self.document_processor.process_document(doc)
                all_vector_docs.extend(vector_docs)
            
            logger.info(f"Processed {len(documents)} documents into {len(all_vector_docs)} chunks")
            
            # Generate embeddings
            logger.info("Generating embeddings...")
            for vector_doc in all_vector_docs:
                vector_doc.embedding = self.vector_search.generate_embedding(vector_doc.content)
            
            # Upsert to vector search
            logger.info("Storing documents in vector search...")
            success = self.vector_search.upsert_documents(all_vector_docs)
            
            if success:
                logger.info(f"Successfully loaded {len(all_vector_docs)} document chunks")
                return True
            else:
                logger.error("Failed to store documents in vector search")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load documents: {e}")
            return False
    
    def query(self, query_text: str, agent_type: str, context: Dict[str, Any] = None) -> RAGResult:
        """Perform RAG query for specific agent"""
        try:
            # Build enhanced query
            enhanced_query = self._build_enhanced_query(query_text, agent_type, context or {})
            
            # Perform vector search
            filters = self.agent_query_templates.get(agent_type, {}).get("filters", {})
            search_results = self.vector_search.similarity_search(
                query=enhanced_query,
                top_k=5,
                filter_dict=filters
            )
            
            # Build context from search results
            context_text = self._build_context(search_results)
            
            # Calculate confidence
            confidence = self._calculate_confidence(search_results)
            
            # Extract sources
            sources = [result.metadata.get("regulator", "unknown") for result in search_results]
            
            result = RAGResult(
                query=enhanced_query,
                relevant_documents=search_results,
                context=context_text,
                confidence=confidence,
                sources=list(set(sources))
            )
            
            logger.info(f"RAG query completed for {agent_type} with confidence {confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return RAGResult(
                query=query_text,
                relevant_documents=[],
                context="No relevant documents found",
                confidence=0.0,
                sources=[]
            )
    
    def _build_enhanced_query(self, query_text: str, agent_type: str, context: Dict[str, Any]) -> str:
        """Build enhanced query using templates and context"""
        templates = self.agent_query_templates.get(agent_type, {}).get("templates", [])
        
        if not templates:
            return query_text
        
        # Use the first template and fill in context variables
        template = templates[0]
        
        # Replace placeholders with context values
        enhanced_query = template
        for key, value in context.items():
            enhanced_query = enhanced_query.replace(f"{{{key}}}", str(value))
        
        # Combine with original query
        if enhanced_query != query_text:
            enhanced_query = f"{enhanced_query} {query_text}"
        
        return enhanced_query
    
    def _build_context(self, search_results: List[SearchResult]) -> str:
        """Build context string from search results"""
        if not search_results:
            return "No relevant regulatory guidance found"
        
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            regulator = result.metadata.get("regulator", "unknown").upper()
            title = result.metadata.get("title", "Unknown document")
            content = result.content[:500]  # Limit content length
            
            context_part = f"[{i}] {regulator} - {title}:\n{content}..."
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    def _calculate_confidence(self, search_results: List[SearchResult]) -> float:
        """Calculate confidence score based on search results"""
        if not search_results:
            return 0.0
        
        # Average the similarity scores
        total_score = sum(result.score for result in search_results)
        avg_score = total_score / len(search_results)
        
        # Normalize to 0-1 range (assuming scores are already in reasonable range)
        confidence = min(avg_score, 1.0)
        
        return confidence
    
    def get_agent_guidance(self, agent_type: str, situation: Dict[str, Any]) -> str:
        """Get specific guidance for an agent in a given situation"""
        # Build query based on situation
        query_parts = []
        
        if "transaction_amount" in situation:
            query_parts.append(f"transaction amount {situation['transaction_amount']}")
        
        if "risk_level" in situation:
            query_parts.append(f"risk level {situation['risk_level']}")
        
        if "customer_sentiment" in situation:
            query_parts.append(f"customer sentiment {situation['customer_sentiment']}")
        
        query_text = " ".join(query_parts) if query_parts else "general guidance"
        
        # Perform RAG query
        result = self.query(query_text, agent_type, situation)
        
        # Format guidance
        guidance = f"Based on Australian banking regulations:\n\n{result.context}\n\nConfidence: {result.confidence:.2f}\nSources: {', '.join(result.sources)}"
        
        return guidance
    
    def initialize(self) -> bool:
        """Initialize the complete RAG system"""
        logger.info("Initializing Australian Banking RAG system...")
        
        # Set up vector search
        if not self.setup_vector_search():
            logger.error("Failed to set up vector search")
            return False
        
        # Load documents
        if not self.load_documents():
            logger.error("Failed to load documents")
            return False
        
        logger.info("RAG system initialized successfully")
        return True

def main():
    """Test the RAG engine"""
    # Initialize RAG system
    rag = AustralianBankingRAG()
    
    # Initialize the system
    if not rag.initialize():
        print("Failed to initialize RAG system")
        return
    
    # Test queries for different agents
    test_queries = [
        {
            "agent": "transaction_risk",
            "query": "large transaction monitoring",
            "context": {"transaction_amount": 50000, "risk_level": "high"}
        },
        {
            "agent": "compliance",
            "query": "operational risk management",
            "context": {"regulation_type": "APRA"}
        },
        {
            "agent": "customer_sentiment",
            "query": "customer complaint handling",
            "context": {"complaint_type": "transaction_blocked"}
        }
    ]
    
    print("Testing RAG queries:")
    print("=" * 50)
    
    for test in test_queries:
        print(f"\nAgent: {test['agent']}")
        print(f"Query: {test['query']}")
        print("-" * 30)
        
        result = rag.query(test["query"], test["agent"], test["context"])
        
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Sources: {', '.join(result.sources)}")
        print(f"Context: {result.context[:200]}...")
        print()

if __name__ == "__main__":
    main()
