#!/usr/bin/env python3
"""
AWS RAG Engine
Replaces Vertex AI Vector Search with Amazon OpenSearch Serverless + Bedrock Titan Embeddings
"""

import os
import json
import logging
import boto3
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Represents a document chunk for vector storage"""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    source: str
    chunk_index: int

@dataclass
class SearchResult:
    """Represents a search result from OpenSearch"""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    source: str

@dataclass
class RAGQuery:
    """Represents a RAG query"""
    query_text: str
    agent_type: str
    context: Dict[str, Any]
    filters: Dict[str, Any]
    max_results: int = 5

@dataclass
class RAGResult:
    """Represents a RAG result"""
    query: str
    relevant_documents: List[SearchResult]
    context: str
    confidence: float
    sources: List[str]

class BedrockEmbeddings:
    """Bedrock Titan Embeddings wrapper"""
    
    def __init__(self, region: str = None):
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.model_id = os.getenv("BEDROCK_EMBEDDING_MODEL", "amazon.titan-embed-text-v2:0")
        
        try:
            self.bedrock_runtime = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.region
            )
            logger.info(f"Bedrock embeddings client initialized in {self.region}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock embeddings client: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using Bedrock Titan"""
        try:
            body = json.dumps({"inputText": text})
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=body
            )
            response_body = json.loads(response['body'].read())
            return response_body['embedding']
            
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embeddings.append(self.get_embedding(text))
        return embeddings

class OpenSearchVectorStore:
    """OpenSearch Serverless vector store wrapper"""
    
    def __init__(self, region: str = None, collection_endpoint: str = None):
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.collection_endpoint = collection_endpoint or os.getenv("OPENSEARCH_ENDPOINT")
        self.index_name = os.getenv("OPENSEARCH_INDEX", "banking-regulations")
        
        if not self.collection_endpoint:
            raise ValueError("OPENSEARCH_ENDPOINT environment variable is required")
        
        # Set up AWS authentication for OpenSearch
        from opensearchpy import OpenSearch, RequestsHttpConnection
        from requests_aws4auth import AWS4Auth
        
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            self.region,
            'aoss',  # Amazon OpenSearch Serverless
            session_token=credentials.token
        )
        
        # Create OpenSearch client
        self.client = OpenSearch(
            hosts=[{'host': self.collection_endpoint, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
        
        logger.info(f"OpenSearch client initialized for {self.collection_endpoint}")
    
    def create_index(self, dimension: int = 1536) -> bool:
        """Create vector index in OpenSearch"""
        try:
            index_mapping = {
                "settings": {
                    "index": {
                        "knn": True,
                        "knn.algo_param.ef_search": 100
                    }
                },
                "mappings": {
                    "properties": {
                        "content": {
                            "type": "text"
                        },
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": dimension,
                            "method": {
                                "name": "hnsw",
                                "space_type": "l2",
                                "engine": "faiss",
                                "parameters": {
                                    "ef_construction": 128,
                                    "m": 24
                                }
                            }
                        },
                        "metadata": {
                            "type": "object"
                        },
                        "source": {
                            "type": "keyword"
                        },
                        "chunk_index": {
                            "type": "integer"
                        }
                    }
                }
            }
            
            if self.client.indices.exists(index=self.index_name):
                logger.info(f"Index {self.index_name} already exists")
                return True
            
            self.client.indices.create(index=self.index_name, body=index_mapping)
            logger.info(f"Created OpenSearch index: {self.index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating OpenSearch index: {e}")
            return False
    
    def add_documents(self, documents: List[DocumentChunk]) -> bool:
        """Add documents to the vector store"""
        try:
            for doc in documents:
                doc_data = {
                    "content": doc.content,
                    "embedding": doc.embedding,
                    "metadata": doc.metadata,
                    "source": doc.source,
                    "chunk_index": doc.chunk_index
                }
                
                self.client.index(
                    index=self.index_name,
                    id=doc.id,
                    body=doc_data
                )
            
            logger.info(f"Added {len(documents)} documents to OpenSearch")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to OpenSearch: {e}")
            return False
    
    def search(self, query_embedding: List[float], k: int = 5, filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Search for similar documents"""
        try:
            search_body = {
                "size": k,
                "query": {
                    "knn": {
                        "embedding": {
                            "vector": query_embedding,
                            "k": k
                        }
                    }
                }
            }
            
            # Add filters if provided
            if filters:
                search_body["query"] = {
                    "bool": {
                        "must": [
                            {
                                "knn": {
                                    "embedding": {
                                        "vector": query_embedding,
                                        "k": k
                                    }
                                }
                            }
                        ],
                        "filter": []
                    }
                }
                
                for key, value in filters.items():
                    search_body["query"]["bool"]["filter"].append({
                        "term": {f"metadata.{key}": value}
                    })
            
            response = self.client.search(index=self.index_name, body=search_body)
            
            results = []
            for hit in response['hits']['hits']:
                result = SearchResult(
                    id=hit['_id'],
                    content=hit['_source']['content'],
                    score=hit['_score'],
                    metadata=hit['_source']['metadata'],
                    source=hit['_source']['source']
                )
                results.append(result)
            
            logger.info(f"Found {len(results)} search results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching OpenSearch: {e}")
            return []
    
    def delete_index(self) -> bool:
        """Delete the index"""
        try:
            if self.client.indices.exists(index=self.index_name):
                self.client.indices.delete(index=self.index_name)
                logger.info(f"Deleted OpenSearch index: {self.index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting OpenSearch index: {e}")
            return False

class AWSRAGEngine:
    """AWS RAG Engine combining OpenSearch + Bedrock Embeddings"""
    
    def __init__(self, region: str = None):
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        
        # Initialize components
        self.embeddings = BedrockEmbeddings(region)
        self.vector_store = OpenSearchVectorStore(region)
        
        # Create index if it doesn't exist
        self.vector_store.create_index(dimension=1536)  # Titan V2 dimension
        
        logger.info("AWS RAG Engine initialized")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the RAG system"""
        try:
            chunks = []
            for i, doc in enumerate(documents):
                # Split document into chunks (simple implementation)
                content = doc.get('content', '')
                chunks_text = self._split_text(content, chunk_size=1000, overlap=200)
                
                for j, chunk_text in enumerate(chunks_text):
                    # Get embedding for chunk
                    embedding = self.embeddings.get_embedding(chunk_text)
                    
                    # Create document chunk
                    chunk = DocumentChunk(
                        id=f"{doc.get('id', i)}_{j}",
                        content=chunk_text,
                        embedding=embedding,
                        metadata=doc.get('metadata', {}),
                        source=doc.get('source', 'unknown'),
                        chunk_index=j
                    )
                    chunks.append(chunk)
            
            return self.vector_store.add_documents(chunks)
            
        except Exception as e:
            logger.error(f"Error adding documents to RAG: {e}")
            return False
    
    def query(self, query_text: str, agent_type: str = "general", context: Dict[str, Any] = None, max_results: int = 5) -> RAGResult:
        """Query the RAG system"""
        try:
            # Get query embedding
            query_embedding = self.embeddings.get_embedding(query_text)
            
            # Build filters based on agent type
            filters = self._build_agent_filters(agent_type, context or {})
            
            # Search vector store
            search_results = self.vector_store.search(query_embedding, max_results, filters)
            
            # Build context from results
            context_text = self._build_context_from_results(search_results, query_text)
            
            # Calculate confidence based on scores
            confidence = self._calculate_confidence(search_results)
            
            # Extract sources
            sources = [result.source for result in search_results]
            
            return RAGResult(
                query=query_text,
                relevant_documents=search_results,
                context=context_text,
                confidence=confidence,
                sources=sources
            )
            
        except Exception as e:
            logger.error(f"Error querying RAG: {e}")
            return RAGResult(
                query=query_text,
                relevant_documents=[],
                context="Error retrieving relevant information",
                confidence=0.0,
                sources=[]
            )
    
    def _split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks with overlap"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size - 200:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def _build_agent_filters(self, agent_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build filters based on agent type"""
        filters = {}
        
        # Agent-specific filtering
        if agent_type == "transaction_risk":
            filters["agent_focus"] = ["risk", "transaction", "fraud"]
        elif agent_type == "compliance":
            filters["agent_focus"] = ["compliance", "regulation", "legal"]
        elif agent_type == "data_privacy":
            filters["agent_focus"] = ["privacy", "pii", "data_protection"]
        elif agent_type == "customer_sentiment":
            filters["agent_focus"] = ["customer", "sentiment", "feedback"]
        elif agent_type == "resilience":
            filters["agent_focus"] = ["resilience", "chaos", "testing"]
        elif agent_type == "knowledge":
            filters["agent_focus"] = ["knowledge", "documentation", "guidance"]
        elif agent_type == "banking_assistant":
            filters["agent_focus"] = ["banking", "general", "assistance"]
        
        # Add context-based filters
        if "regulator" in context:
            filters["regulator"] = context["regulator"]
        if "document_type" in context:
            filters["document_type"] = context["document_type"]
        
        return filters
    
    def _build_context_from_results(self, results: List[SearchResult], query: str) -> str:
        """Build context string from search results"""
        if not results:
            return "No relevant information found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"Source {i} (Score: {result.score:.2f}):\n{result.content}\n")
        
        return "\n".join(context_parts)
    
    def _calculate_confidence(self, results: List[SearchResult]) -> float:
        """Calculate confidence based on search results"""
        if not results:
            return 0.0
        
        # Simple confidence calculation based on top score
        top_score = results[0].score
        return min(top_score / 10.0, 1.0)  # Normalize to 0-1 range

# Global RAG engine instance
_rag_engine = None

def get_rag_engine() -> AWSRAGEngine:
    """Get global RAG engine instance"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = AWSRAGEngine()
    return _rag_engine

# Backward compatibility
class AustralianBankingRAG(AWSRAGEngine):
    """Backward compatibility alias"""
    def __init__(self):
        super().__init__()
    
    def initialize(self) -> bool:
        """Initialize the RAG system (backward compatibility)"""
        try:
            # Index is created in constructor
            logger.info("Australian Banking RAG initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Australian Banking RAG: {e}")
            return False

# Example usage and testing
if __name__ == "__main__":
    # Test RAG engine
    try:
        rag = AWSRAGEngine()
        
        # Test adding documents
        test_docs = [
            {
                "id": "test_doc_1",
                "content": "This is a test document about banking regulations and compliance requirements.",
                "metadata": {"regulator": "APRA", "document_type": "guideline"},
                "source": "test_source"
            }
        ]
        
        success = rag.add_documents(test_docs)
        print(f"Add documents test: {'Success' if success else 'Failed'}")
        
        # Test querying
        result = rag.query("What are the banking compliance requirements?", "compliance")
        print(f"Query test: Found {len(result.relevant_documents)} results")
        print(f"Context: {result.context[:100]}...")
        print(f"Confidence: {result.confidence:.2f}")
        
    except Exception as e:
        print(f"RAG engine test failed: {e}")
        print("Make sure AWS credentials are configured and OpenSearch endpoint is set")

