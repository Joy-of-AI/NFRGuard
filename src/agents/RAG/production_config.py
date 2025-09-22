#!/usr/bin/env python3
"""
Production Configuration for RAG System
"""

import os

# Google Cloud Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = "australia-southeast1"  # or your preferred region
SERVICE_ACCOUNT_KEY = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Vector Search Configuration
VECTOR_INDEX_NAME = "nfrguard-banking-regulations-prod"
VECTOR_ENDPOINT_NAME = "nfrguard-vector-endpoint-prod"
MACHINE_TYPE = "e2-standard-16"  # Production machine type
MIN_REPLICAS = 2
MAX_REPLICAS = 10

# Document Storage Configuration
BUCKET_NAME = f"{PROJECT_ID}-nfrguard-documents"
DOCUMENT_UPDATE_INTERVAL = 24 * 60 * 60  # 24 hours in seconds

# Monitoring Configuration
METRICS_NAMESPACE = "nfrguard/rag"
ALERT_THRESHOLD_CONFIDENCE = 0.3
ALERT_THRESHOLD_RESPONSE_TIME = 1.0  # seconds

# RAG System Configuration
RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"
VECTOR_INDEX_ID = os.getenv("VECTOR_INDEX_ID", "")
VECTOR_ENDPOINT_ID = os.getenv("VECTOR_ENDPOINT_ID", "")
DEPLOYED_INDEX_ID = "nfrguard-deployed-index"

# Agent Configuration
AGENT_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
CACHE_TTL = 300  # 5 minutes

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Performance Configuration
MAX_CONCURRENT_QUERIES = 100
QUERY_BATCH_SIZE = 10
EMBEDDING_BATCH_SIZE = 50

# Security Configuration
ENABLE_ACCESS_LOGGING = True
ENABLE_AUDIT_LOGGING = True
DATA_RETENTION_DAYS = 90

# Health Check Configuration
HEALTH_CHECK_INTERVAL = 60  # seconds
HEALTH_CHECK_TIMEOUT = 10  # seconds
HEALTH_CHECK_RETRIES = 3

# Alerting Configuration
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "")
ALERT_SLACK_WEBHOOK = os.getenv("ALERT_SLACK_WEBHOOK", "")

# Feature Flags
ENABLE_DOCUMENT_AUTO_UPDATE = True
ENABLE_QUERY_CACHING = True
ENABLE_METRICS_COLLECTION = True
ENABLE_PERFORMANCE_MONITORING = True

# Regulatory Document Sources
REGULATORY_SOURCES = {
    "asic": {
        "name": "Australian Securities and Investments Commission",
        "update_frequency": "weekly",
        "priority": "high"
    },
    "apra": {
        "name": "Australian Prudential Regulation Authority", 
        "update_frequency": "weekly",
        "priority": "high"
    },
    "austrac": {
        "name": "Australian Transaction Reports and Analysis Centre",
        "update_frequency": "daily",
        "priority": "critical"
    },
    "afca": {
        "name": "Australian Financial Complaints Authority",
        "update_frequency": "weekly", 
        "priority": "medium"
    }
}

# Agent-Specific Configuration
AGENT_CONFIGS = {
    "transaction_risk": {
        "enabled": True,
        "priority": "critical",
        "timeout": 5,
        "max_retries": 3
    },
    "compliance": {
        "enabled": True,
        "priority": "critical",
        "timeout": 10,
        "max_retries": 3
    },
    "resilience": {
        "enabled": True,
        "priority": "critical",
        "timeout": 5,
        "max_retries": 3
    },
    "customer_sentiment": {
        "enabled": True,
        "priority": "high",
        "timeout": 15,
        "max_retries": 2
    },
    "data_privacy": {
        "enabled": True,
        "priority": "high",
        "timeout": 10,
        "max_retries": 3
    },
    "knowledge": {
        "enabled": True,
        "priority": "medium",
        "timeout": 20,
        "max_retries": 2
    },
    "banking_assistant": {
        "enabled": True,
        "priority": "high",
        "timeout": 30,
        "max_retries": 2
    }
}

def validate_config():
    """Validate production configuration"""
    errors = []
    
    if not PROJECT_ID or PROJECT_ID == "your-project-id":
        errors.append("PROJECT_ID must be set")
    
    if not SERVICE_ACCOUNT_KEY:
        errors.append("GOOGLE_APPLICATION_CREDENTIALS must be set")
    
    if MIN_REPLICAS < 1:
        errors.append("MIN_REPLICAS must be at least 1")
    
    if MAX_REPLICAS < MIN_REPLICAS:
        errors.append("MAX_REPLICAS must be >= MIN_REPLICAS")
    
    if ALERT_THRESHOLD_CONFIDENCE < 0 or ALERT_THRESHOLD_CONFIDENCE > 1:
        errors.append("ALERT_THRESHOLD_CONFIDENCE must be between 0 and 1")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
    
    return True

def get_agent_config(agent_name):
    """Get configuration for specific agent"""
    return AGENT_CONFIGS.get(agent_name, {
        "enabled": True,
        "priority": "medium",
        "timeout": 10,
        "max_retries": 3
    })

def is_agent_enabled(agent_name):
    """Check if agent is enabled"""
    config = get_agent_config(agent_name)
    return config.get("enabled", True) and RAG_ENABLED

def get_timeout_for_agent(agent_name):
    """Get timeout for specific agent"""
    config = get_agent_config(agent_name)
    return config.get("timeout", AGENT_TIMEOUT)

def get_retries_for_agent(agent_name):
    """Get max retries for specific agent"""
    config = get_agent_config(agent_name)
    return config.get("max_retries", MAX_RETRIES)

if __name__ == "__main__":
    try:
        validate_config()
        print("✅ Production configuration is valid")
        print(f"Project ID: {PROJECT_ID}")
        print(f"Location: {LOCATION}")
        print(f"RAG Enabled: {RAG_ENABLED}")
        print(f"Vector Index: {VECTOR_INDEX_NAME}")
        print(f"Vector Endpoint: {VECTOR_ENDPOINT_NAME}")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        exit(1)
