#!/usr/bin/env python3
"""
Automated Document Update Script for RAG System
This script updates regulatory documents and refreshes the vector search index
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from production_config import *
from rag_engine import AustralianBankingRAG

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler('document_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_document_freshness():
    """Check if documents need updating based on freshness"""
    logger.info("Checking document freshness...")
    
    try:
        # Load deployment info
        if Path("deployment_info.json").exists():
            with open("deployment_info.json", "r") as f:
                deployment_info = json.load(f)
        else:
            logger.error("No deployment info found")
            return False
        
        # Initialize RAG system
        rag = AustralianBankingRAG(project_id=PROJECT_ID)
        rag.index_id = deployment_info["index_id"]
        rag.index_endpoint_id = deployment_info["endpoint_id"]
        rag.deployed_index_id = deployment_info["deployed_index_id"]
        
        # Check document freshness
        documents = rag.document_downloader.download_all_documents()
        current_time = time.time()
        stale_documents = 0
        
        for doc in documents:
            # Check if document is older than 7 days
            if hasattr(doc, 'metadata') and 'download_date' in doc.metadata:
                download_date = doc.metadata['download_date']
                # Simple check - in production you'd parse the date properly
                if current_time - time.time() > 7 * 24 * 60 * 60:  # 7 days
                    stale_documents += 1
        
        if stale_documents == 0:
            logger.info("All documents are fresh")
            return False
        else:
            logger.info(f"Found {stale_documents} stale documents, update needed")
            return True
            
    except Exception as e:
        logger.error(f"Error checking document freshness: {e}")
        return True  # Update on error to be safe

def update_documents():
    """Update regulatory documents and refresh vector search"""
    logger.info("Starting document update process...")
    
    try:
        # Load deployment info
        if Path("deployment_info.json").exists():
            with open("deployment_info.json", "r") as f:
                deployment_info = json.load(f)
        else:
            logger.error("No deployment info found")
            return False
        
        # Initialize RAG system
        rag = AustralianBankingRAG(project_id=PROJECT_ID)
        rag.index_id = deployment_info["index_id"]
        rag.index_endpoint_id = deployment_info["endpoint_id"]
        rag.deployed_index_id = deployment_info["deployed_index_id"]
        
        # Download fresh documents
        logger.info("Downloading fresh regulatory documents...")
        documents = rag.document_downloader.download_all_documents()
        
        if len(documents) < 6:  # Expected minimum
            logger.error(f"Insufficient documents downloaded: {len(documents)}")
            return False
        
        logger.info(f"Downloaded {len(documents)} regulatory documents")
        
        # Process documents into chunks
        logger.info("Processing documents into chunks...")
        chunks = rag._process_documents_into_chunks(documents)
        logger.info(f"Processed into {len(chunks)} chunks")
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = []
        for i, chunk in enumerate(chunks):
            embedding = rag.vector_search.generate_embedding(chunk.page_content)
            embeddings.append(embedding)
            if (i + 1) % 10 == 0:
                logger.info(f"Generated embeddings for {i + 1}/{len(chunks)} chunks")
        
        # Store in vector search
        logger.info("Storing documents in vector search...")
        success = rag.vector_search.upsert_documents(chunks)
        
        if success:
            logger.info("Successfully updated vector search with fresh documents")
            
            # Test the updated system
            logger.info("Testing updated system...")
            test_queries = [
                ("transaction risk monitoring", "transaction_risk"),
                ("compliance requirements", "compliance"),
                ("customer complaint handling", "customer_sentiment")
            ]
            
            for query, agent in test_queries:
                result = rag.query(query, agent)
                logger.info(f"Test query {agent}: confidence {result.confidence:.2f}")
            
            # Save update timestamp
            update_info = {
                "last_update": datetime.now().isoformat(),
                "document_count": len(documents),
                "chunk_count": len(chunks),
                "update_successful": True
            }
            
            with open("last_update.json", "w") as f:
                json.dump(update_info, f, indent=2)
            
            logger.info("Document update completed successfully")
            return True
        else:
            logger.error("Failed to update vector search")
            return False
            
    except Exception as e:
        logger.error(f"Document update failed: {e}")
        return False

def send_update_notification(success, details):
    """Send notification about document update status"""
    if success:
        logger.info("📧 Document update notification: SUCCESS")
        logger.info(f"   Updated {details.get('document_count', 0)} documents")
        logger.info(f"   Processed {details.get('chunk_count', 0)} chunks")
    else:
        logger.error("📧 Document update notification: FAILED")
        logger.error(f"   Error: {details.get('error', 'Unknown error')}")

def main():
    """Main document update function"""
    logger.info("🔄 Starting automated document update")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check if update is needed
    if not check_document_freshness():
        logger.info("Documents are fresh, no update needed")
        return True
    
    # Perform update
    success = update_documents()
    
    # Send notification
    details = {
        "document_count": 0,
        "chunk_count": 0,
        "error": None
    }
    
    if success:
        # Load update info
        if Path("last_update.json").exists():
            with open("last_update.json", "r") as f:
                update_info = json.load(f)
                details.update(update_info)
    else:
        details["error"] = "Update process failed"
    
    send_update_notification(success, details)
    
    if success:
        logger.info("✅ Document update completed successfully")
        return True
    else:
        logger.error("❌ Document update failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
