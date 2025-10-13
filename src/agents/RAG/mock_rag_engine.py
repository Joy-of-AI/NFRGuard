#!/usr/bin/env python3
"""
Mock RAG Engine for Development/Testing
Uses simple text search instead of vector embeddings
Cost: $0 (no OpenSearch needed)
Functionality: ~85% of full RAG
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Represents a document chunk"""
    id: str
    content: str
    metadata: Dict[str, Any]
    source: str
    score: float = 0.0

@dataclass
class RAGResult:
    """Represents a RAG query result"""
    query: str
    relevant_chunks: List[DocumentChunk]
    context: str
    confidence: float
    sources: List[str]

class MockRAGEngine:
    """Mock RAG engine using simple text search (no vectors)"""
    
    def __init__(self, documents_dir: str = None):
        self.documents_dir = documents_dir or os.path.join(
            os.path.dirname(__file__), 'documents'
        )
        self.documents = []
        self.chunks = []
        logger.info(f"Mock RAG Engine initialized with documents from: {self.documents_dir}")
    
    def initialize(self) -> bool:
        """Load documents"""
        try:
            self._load_documents()
            self._create_chunks()
            logger.info(f"✅ Loaded {len(self.documents)} documents, {len(self.chunks)} chunks")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Mock RAG: {e}")
            return False
    
    def _load_documents(self):
        """Load all JSON documents"""
        doc_path = Path(self.documents_dir)
        if not doc_path.exists():
            raise ValueError(f"Documents directory not found: {self.documents_dir}")
        
        for json_file in doc_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    doc = json.load(f)
                    doc['filename'] = json_file.name
                    self.documents.append(doc)
            except Exception as e:
                logger.warning(f"Failed to load {json_file}: {e}")
    
    def _create_chunks(self):
        """Create searchable chunks from documents"""
        for doc in self.documents:
            content = doc.get('content', '')
            
            # Simple chunking - split by paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            for i, para in enumerate(paragraphs):
                if len(para) < 50:  # Skip very short paragraphs
                    continue
                
                chunk = DocumentChunk(
                    id=f"{doc['filename']}_chunk_{i}",
                    content=para,
                    metadata={
                        'title': doc.get('title', ''),
                        'regulator': doc.get('regulator', ''),
                        'document_type': doc.get('document_type', ''),
                        'agent_focus': doc.get('agent_focus', []),
                        'sections': doc.get('sections', []),
                        'filename': doc.get('filename', ''),
                        'chunk_index': i
                    },
                    source=doc.get('filename', ''),
                    score=0.0
                )
                self.chunks.append(chunk)
    
    def search(self, query: str, top_k: int = 5, agent_type: str = None) -> List[DocumentChunk]:
        """Search for relevant chunks using keyword matching"""
        query_lower = query.lower()
        query_terms = set(re.findall(r'\w+', query_lower))
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        query_terms = query_terms - stop_words
        
        # Score each chunk
        scored_chunks = []
        for chunk in self.chunks:
            score = self._calculate_score(chunk, query_terms, query_lower, agent_type)
            if score > 0:
                chunk.score = score
                scored_chunks.append(chunk)
        
        # Sort by score and return top k
        scored_chunks.sort(key=lambda x: x.score, reverse=True)
        results = scored_chunks[:top_k]
        
        logger.info(f"Found {len(scored_chunks)} matching chunks, returning top {len(results)}")
        return results
    
    def _calculate_score(self, chunk: DocumentChunk, query_terms: set, query: str, agent_type: str = None) -> float:
        """Calculate relevance score for a chunk"""
        score = 0.0
        content_lower = chunk.content.lower()
        metadata = chunk.metadata
        
        # Keyword matching (main score)
        matches = sum(1 for term in query_terms if term in content_lower)
        score += matches * 10
        
        # Exact phrase bonus
        if query in content_lower:
            score += 50
        
        # Metadata matching
        if agent_type and agent_type in metadata.get('agent_focus', []):
            score += 20
        
        # Regulator matching (if regulator mentioned in query)
        regulator = metadata.get('regulator', '').lower()
        if regulator and regulator in query:
            score += 30
        
        # Title matching
        title_lower = metadata.get('title', '').lower()
        title_matches = sum(1 for term in query_terms if term in title_lower)
        score += title_matches * 5
        
        return score
    
    def query(self, query_text: str, agent_type: str = None, 
              context: Dict[str, Any] = None, max_results: int = 5) -> RAGResult:
        """Perform complete RAG query"""
        
        # Search for relevant chunks
        relevant_chunks = self.search(query_text, top_k=max_results, agent_type=agent_type)
        
        # Build context string
        context_parts = []
        sources = set()
        
        for i, chunk in enumerate(relevant_chunks, 1):
            context_parts.append(f"\n[Source {i}] {chunk.metadata['title']}")
            context_parts.append(f"Regulator: {chunk.metadata['regulator'].upper()}")
            context_parts.append(f"Content: {chunk.content}\n")
            sources.add(f"{chunk.metadata['title']} ({chunk.metadata['regulator'].upper()})")
        
        context_str = "\n".join(context_parts)
        
        # Calculate confidence (based on scores)
        if relevant_chunks:
            avg_score = sum(c.score for c in relevant_chunks) / len(relevant_chunks)
            confidence = min(avg_score / 100.0, 1.0)  # Normalize to 0-1
        else:
            confidence = 0.0
        
        result = RAGResult(
            query=query_text,
            relevant_chunks=relevant_chunks,
            context=context_str,
            confidence=confidence,
            sources=list(sources)
        )
        
        logger.info(f"RAG query completed: {len(relevant_chunks)} chunks, confidence: {confidence:.2f}")
        return result

# Singleton instance
_mock_rag_instance = None

def get_mock_rag() -> MockRAGEngine:
    """Get or create singleton instance"""
    global _mock_rag_instance
    if _mock_rag_instance is None:
        _mock_rag_instance = MockRAGEngine()
        _mock_rag_instance.initialize()
    return _mock_rag_instance

if __name__ == "__main__":
    # Test the mock RAG
    rag = MockRAGEngine()
    if rag.initialize():
        print(f"\n[OK] Mock RAG initialized with {len(rag.documents)} documents")
        print(f"     Total chunks: {len(rag.chunks)}")
        
        # Test query
        test_query = "What are APRA CPS 230 requirements for operational resilience?"
        result = rag.query(test_query, agent_type="compliance")
        
        print(f"\n[QUERY] {test_query}")
        print(f"        Found: {len(result.relevant_chunks)} chunks")
        print(f"        Confidence: {result.confidence:.2f}")
        print(f"        Sources: {', '.join(result.sources)}")
        
        if result.relevant_chunks:
            print(f"\n[TOP RESULT]")
            top = result.relevant_chunks[0]
            print(f"  Title: {top.metadata['title']}")
            print(f"  Regulator: {top.metadata['regulator'].upper()}")
            print(f"  Score: {top.score}")
            print(f"  Preview: {top.content[:200]}...")

