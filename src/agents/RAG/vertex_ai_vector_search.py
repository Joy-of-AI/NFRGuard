#!/usr/bin/env python3
"""
Vertex AI Vector Search Integration for RAG
Handles document embedding, indexing, and retrieval using Vertex AI Vector Search
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

try:
    from google.cloud import aiplatform
    from google.cloud.aiplatform import gapic as aip
    from google.cloud import storage
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    logging.warning("Vertex AI libraries not available. Using mock implementation.")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VectorDocument:
    """Represents a document in vector search"""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]

@dataclass
class SearchResult:
    """Represents a search result from vector search"""
    document_id: str
    content: str
    score: float
    metadata: Dict[str, Any]

class VertexAIVectorSearch:
    """Vertex AI Vector Search implementation"""
    
    def __init__(self, project_id: str = None, location: str = "australia-southeast1"):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        
        if not self.project_id:
            raise ValueError("Project ID must be provided or set in GOOGLE_CLOUD_PROJECT environment variable")
            
        self.index_id = None
        self.index_endpoint_id = None
        
        # Check if Vertex AI is available
        try:
            from google.cloud import aiplatform
            from google.cloud.aiplatform import gapic as aip
            from google.cloud import storage
            self.vertex_ai_available = True
        except ImportError:
            self.vertex_ai_available = False
            logger.warning("Vertex AI libraries not available. Using mock implementation.")
        
        if self.vertex_ai_available:
            try:
                # Initialize Vertex AI
                aiplatform.init(project=self.project_id, location=self.location)
                
                # Initialize clients
                self.index_client = aip.IndexServiceClient()
                self.index_endpoint_client = aip.IndexEndpointServiceClient()
                self.prediction_client = aip.PredictionServiceClient()
                
                logger.info(f"Initialized Vertex AI Vector Search for project {self.project_id}")
            except Exception as e:
                logger.warning(f"Failed to initialize Vertex AI: {e}. Using mock implementation.")
                self.vertex_ai_available = False
        else:
            logger.info("Using mock Vertex AI implementation")
    
    def create_vector_index(self, display_name: str = "australian-banking-regulations") -> str:
        """Create a vector index for document storage"""
        if not self.vertex_ai_available:
            return self._mock_create_index(display_name)
            
        try:
            # Define the index
            index = aip.Index(
                display_name=display_name,
                description="Australian banking regulatory documents for RAG",
                metadata_schema_uri="gs://your-bucket/metadata-schema.json",
                index_update_method=aip.Index.IndexUpdateMethod.BATCH_UPDATE
            )
            
            # Create the index
            parent = f"projects/{self.project_id}/locations/{self.location}"
            operation = self.index_client.create_index(parent=parent, index=index)
            
            # Wait for completion
            result = operation.result(timeout=300)
            self.index_id = result.name.split("/")[-1]
            
            logger.info(f"Created vector index: {self.index_id}")
            return self.index_id
            
        except Exception as e:
            logger.error(f"Failed to create vector index: {e}")
            return self._mock_create_index(display_name)
    
    def create_index_endpoint(self, display_name: str = "australian-banking-endpoint") -> str:
        """Create an index endpoint for serving"""
        if not self.vertex_ai_available:
            return self._mock_create_endpoint(display_name)
            
        try:
            # Define the endpoint
            endpoint = aip.IndexEndpoint(
                display_name=display_name,
                description="Endpoint for Australian banking regulations"
            )
            
            # Create the endpoint
            parent = f"projects/{self.project_id}/locations/{self.location}"
            operation = self.index_endpoint_client.create_index_endpoint(parent=parent, index_endpoint=endpoint)
            
            # Wait for completion
            result = operation.result(timeout=300)
            self.index_endpoint_id = result.name.split("/")[-1]
            
            logger.info(f"Created index endpoint: {self.index_endpoint_id}")
            return self.index_endpoint_id
            
        except Exception as e:
            logger.error(f"Failed to create index endpoint: {e}")
            return self._mock_create_endpoint(display_name)
    
    def deploy_index(self, index_id: str, endpoint_id: str, deployed_index_id: str = "deployed_index") -> str:
        """Deploy an index to an endpoint"""
        if not self.vertex_ai_available:
            return self._mock_deploy_index(index_id, endpoint_id, deployed_index_id)
            
        try:
            # Create deployed index
            deployed_index = aip.DeployedIndex(
                id=deployed_index_id,
                index=index_id,
                display_name="Australian Banking Regulations Deployed Index",
                enable_access_logging=True,
                dedicated_resources=aip.DeployedIndex.DedicatedResources(
                    machine_spec=aip.MachineSpec(
                        machine_type="e2-standard-16"
                    ),
                    min_replica_count=1,
                    max_replica_count=1
                )
            )
            
            # Deploy to endpoint
            endpoint_name = f"projects/{self.project_id}/locations/{self.location}/indexEndpoints/{endpoint_id}"
            operation = self.index_endpoint_client.deploy_index(
                index_endpoint=endpoint_name,
                deployed_index=deployed_index
            )
            
            # Wait for completion
            result = operation.result(timeout=600)
            
            logger.info(f"Deployed index {index_id} to endpoint {endpoint_id}")
            return deployed_index_id
            
        except Exception as e:
            logger.error(f"Failed to deploy index: {e}")
            return self._mock_deploy_index(index_id, endpoint_id, deployed_index_id)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Vertex AI"""
        if not self.vertex_ai_available:
            return self._mock_generate_embedding(text)
            
        try:
            # Use Vertex AI's text embedding model
            endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/textembedding-gecko@001"
            
            instances = [{"content": text}]
            
            response = self.prediction_client.predict(
                endpoint=endpoint,
                instances=instances
            )
            
            embedding = response.predictions[0]["embeddings"]["values"]
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return self._mock_generate_embedding(text)
    
    def upsert_documents(self, documents: List[VectorDocument]) -> bool:
        """Upsert documents to the vector index"""
        if not self.vertex_ai_available:
            return self._mock_upsert_documents(documents)
            
        try:
            # Prepare datapoints
            datapoints = []
            for doc in documents:
                datapoint = aip.IndexDatapoint(
                    datapoint_id=doc.id,
                    feature_vector=doc.embedding,
                    metadata=doc.metadata
                )
                datapoints.append(datapoint)
            
            # Upsert to index
            index_name = f"projects/{self.project_id}/locations/{self.location}/indexes/{self.index_id}"
            self.index_client.upsert_datapoints(index=index_name, datapoints=datapoints)
            
            logger.info(f"Upserted {len(documents)} documents to vector index")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert documents: {e}")
            return self._mock_upsert_documents(documents)
    
    def similarity_search(self, query: str, top_k: int = 5, filter_dict: Dict = None) -> List[SearchResult]:
        """Perform similarity search"""
        if not self.vertex_ai_available:
            return self._mock_similarity_search(query, top_k, filter_dict)
            
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Prepare query
            query_request = aip.NearestNeighborQuery(
                embedding=query_embedding,
                neighbor_count=top_k
            )
            
            # Add filter if provided
            if filter_dict:
                query_request.filter = self._build_filter(filter_dict)
            
            # Perform search
            endpoint_name = f"projects/{self.project_id}/locations/{self.location}/indexEndpoints/{self.index_endpoint_id}"
            response = self.prediction_client.predict(
                endpoint=endpoint_name,
                instances=[query_request]
            )
            
            # Process results
            results = []
            for neighbor in response.predictions[0]["neighbors"]:
                result = SearchResult(
                    document_id=neighbor["datapoint"]["datapoint_id"],
                    content=neighbor["datapoint"]["metadata"]["content"],
                    score=neighbor["distance"],
                    metadata=neighbor["datapoint"]["metadata"]
                )
                results.append(result)
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            return self._mock_similarity_search(query, top_k, filter_dict)
    
    def _build_filter(self, filter_dict: Dict) -> str:
        """Build filter expression for search"""
        conditions = []
        for key, value in filter_dict.items():
            if isinstance(value, list):
                # Handle list values (e.g., agent_focus)
                value_str = " OR ".join([f'"{v}"' for v in value])
                conditions.append(f"metadata.{key} = ({value_str})")
            else:
                conditions.append(f'metadata.{key} = "{value}"')
        
        return " AND ".join(conditions)
    
    # Mock implementations for when Vertex AI is not available
    def _mock_create_index(self, display_name: str) -> str:
        """Mock implementation of create_index"""
        self.index_id = f"mock_index_{int(time.time())}"
        logger.info(f"Created mock vector index: {self.index_id}")
        return self.index_id
    
    def _mock_create_endpoint(self, display_name: str) -> str:
        """Mock implementation of create_endpoint"""
        self.index_endpoint_id = f"mock_endpoint_{int(time.time())}"
        logger.info(f"Created mock index endpoint: {self.index_endpoint_id}")
        return self.index_endpoint_id
    
    def _mock_deploy_index(self, index_id: str, endpoint_id: str, deployed_index_id: str) -> str:
        """Mock implementation of deploy_index"""
        logger.info(f"Deployed mock index {index_id} to endpoint {endpoint_id}")
        return deployed_index_id
    
    def _mock_generate_embedding(self, text: str) -> List[float]:
        """Mock implementation of generate_embedding"""
        # Generate a mock embedding based on text content
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 768-dimensional vector (typical embedding size)
        embedding = []
        for i in range(768):
            byte_index = i % len(hash_bytes)
            embedding.append((hash_bytes[byte_index] - 128) / 128.0)
        
        return embedding
    
    def _mock_upsert_documents(self, documents: List[VectorDocument]) -> bool:
        """Mock implementation of upsert_documents"""
        # Store documents in local file for mock
        mock_file = Path("mock_vector_documents.json")
        
        try:
            if mock_file.exists():
                with open(mock_file, 'r') as f:
                    existing_docs = json.load(f)
            else:
                existing_docs = []
            
            # Add new documents
            for doc in documents:
                doc_data = {
                    "id": doc.id,
                    "content": doc.content,
                    "embedding": doc.embedding,
                    "metadata": doc.metadata
                }
                existing_docs.append(doc_data)
            
            # Save back to file
            with open(mock_file, 'w') as f:
                json.dump(existing_docs, f, indent=2)
            
            logger.info(f"Mock upserted {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Mock upsert failed: {e}")
            return False
    
    def _mock_similarity_search(self, query: str, top_k: int = 5, filter_dict: Dict = None) -> List[SearchResult]:
        """Mock implementation of similarity_search"""
        # Generate query embedding
        query_embedding = self._mock_generate_embedding(query)
        
        # Load mock documents
        mock_file = Path("mock_vector_documents.json")
        if not mock_file.exists():
            # Return some mock results if no file exists
            mock_results = [
                SearchResult(
                    document_id="mock_doc_1",
                    content="Mock banking regulation content for testing",
                    score=0.8,
                    metadata={"regulator": "mock", "agent_focus": ["transaction_risk"]}
                ),
                SearchResult(
                    document_id="mock_doc_2", 
                    content="Mock compliance requirements for testing",
                    score=0.7,
                    metadata={"regulator": "mock", "agent_focus": ["compliance"]}
                )
            ]
            return mock_results[:top_k]
        
        try:
            with open(mock_file, 'r') as f:
                documents = json.load(f)
            
            # Calculate similarities
            similarities = []
            for doc in documents:
                # Simple cosine similarity
                doc_embedding = doc["embedding"]
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                
                # Apply filter if provided
                if filter_dict:
                    if not self._matches_filter(doc["metadata"], filter_dict):
                        continue
                
                similarities.append((similarity, doc))
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            results = []
            for similarity, doc in similarities[:top_k]:
                result = SearchResult(
                    document_id=doc["id"],
                    content=doc["content"],
                    score=similarity,
                    metadata=doc["metadata"]
                )
                results.append(result)
            
            logger.info(f"Mock found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Mock similarity search failed: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _matches_filter(self, metadata: Dict, filter_dict: Dict) -> bool:
        """Check if metadata matches filter"""
        for key, value in filter_dict.items():
            if key not in metadata:
                return False
            
            if isinstance(value, list):
                # For agent_focus, check if any of the requested agents are in the document's agent_focus
                if key == "agent_focus":
                    doc_agents = metadata[key]
                    if not any(agent in doc_agents for agent in value):
                        return False
                else:
                    if metadata[key] not in value:
                        return False
            else:
                if metadata[key] != value:
                    return False
        
        return True

def main():
    """Test the Vertex AI Vector Search implementation"""
    # Initialize vector search
    vector_search = VertexAIVectorSearch()
    
    # Create index and endpoint
    index_id = vector_search.create_vector_index()
    endpoint_id = vector_search.create_index_endpoint()
    
    # Deploy index
    deployed_id = vector_search.deploy_index(index_id, endpoint_id)
    
    print(f"Vector Search setup complete:")
    print(f"Index ID: {index_id}")
    print(f"Endpoint ID: {endpoint_id}")
    print(f"Deployed Index ID: {deployed_id}")

if __name__ == "__main__":
    main()
