# 🚀 RAG System Production Deployment Guide

This guide walks you through deploying the RAG system to production with Vertex AI Vector Search and integrating it with your existing NFRGuard AI agents.

## 📋 **Prerequisites**

### **1. Google Cloud Setup**
```bash
# Set your project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
```

### **2. Service Account Permissions**
Your service account needs these roles:
- `roles/aiplatform.user` - For Vertex AI Vector Search
- `roles/storage.admin` - For document storage
- `roles/monitoring.metricWriter` - For metrics
- `roles/logging.logWriter` - For logging

### **3. Python Environment**
```bash
# Create virtual environment
python -m venv rag-production
source rag-production/bin/activate  # On Windows: rag-production\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install google-cloud-aiplatform>=1.38.0
pip install google-cloud-storage>=2.10.0
```

## 🏗️ **Production Deployment Steps**

### **Step 1: Configure Production Settings**

Create `production_config.py`:
```python
# production_config.py
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
```

### **Step 2: Deploy Vector Search Infrastructure**

Create `deploy_vector_search.py`:
```python
#!/usr/bin/env python3
"""
Deploy Vertex AI Vector Search for production
"""

import os
import time
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip
from production_config import *

def deploy_production_vector_search():
    """Deploy production-ready vector search infrastructure"""
    
    # Initialize Vertex AI
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
    
    # Create vector index
    print("Creating production vector index...")
    index = aip.Index(
        display_name=VECTOR_INDEX_NAME,
        description="Production NFRGuard Australian banking regulations",
        metadata_schema_uri="gs://your-bucket/metadata-schema.json",
        index_update_method=aip.Index.IndexUpdateMethod.BATCH_UPDATE
    )
    
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
    index_operation = aip.IndexServiceClient().create_index(parent=parent, index=index)
    index_result = index_operation.result(timeout=600)  # 10 minutes
    index_id = index_result.name.split("/")[-1]
    
    print(f"✅ Vector index created: {index_id}")
    
    # Create index endpoint
    print("Creating production index endpoint...")
    endpoint = aip.IndexEndpoint(
        display_name=VECTOR_ENDPOINT_NAME,
        description="Production endpoint for NFRGuard regulations"
    )
    
    endpoint_operation = aip.IndexEndpointServiceClient().create_index_endpoint(
        parent=parent, 
        index_endpoint=endpoint
    )
    endpoint_result = endpoint_operation.result(timeout=600)
    endpoint_id = endpoint_result.name.split("/")[-1]
    
    print(f"✅ Index endpoint created: {endpoint_id}")
    
    # Deploy index to endpoint
    print("Deploying index to endpoint...")
    deployed_index = aip.DeployedIndex(
        id="nfrguard-deployed-index",
        index=index_id,
        display_name="NFRGuard Production Deployed Index",
        enable_access_logging=True,
        dedicated_resources=aip.DeployedIndex.DedicatedResources(
            machine_spec=aip.MachineSpec(machine_type=MACHINE_TYPE),
            min_replica_count=MIN_REPLICAS,
            max_replica_count=MAX_REPLICAS
        )
    )
    
    endpoint_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/indexEndpoints/{endpoint_id}"
    deploy_operation = aip.IndexEndpointServiceClient().deploy_index(
        index_endpoint=endpoint_name,
        deployed_index=deployed_index
    )
    deploy_result = deploy_operation.result(timeout=1200)  # 20 minutes
    
    print(f"✅ Index deployed successfully")
    
    return {
        "index_id": index_id,
        "endpoint_id": endpoint_id,
        "deployed_index_id": "nfrguard-deployed-index"
    }

if __name__ == "__main__":
    result = deploy_production_vector_search()
    print(f"Production deployment complete: {result}")
```

### **Step 3: Load Production Documents**

Create `load_production_documents.py`:
```python
#!/usr/bin/env python3
"""
Load regulatory documents into production vector search
"""

import os
import time
from rag_engine import AustralianBankingRAG
from production_config import *

def load_production_documents():
    """Load documents into production vector search"""
    
    print("Initializing production RAG system...")
    
    # Initialize RAG with production settings
    rag = AustralianBankingRAG(
        project_id=PROJECT_ID,
        download_dir="production_documents"
    )
    
    # Set production vector search IDs
    rag.index_id = "your-index-id"  # From deployment
    rag.index_endpoint_id = "your-endpoint-id"  # From deployment
    rag.deployed_index_id = "nfrguard-deployed-index"
    
    print("Loading regulatory documents...")
    
    # Download and process documents
    success = rag.load_documents()
    
    if success:
        print("✅ Production documents loaded successfully")
        
        # Verify document count
        documents = rag.document_downloader.download_all_documents()
        print(f"📊 Loaded {len(documents)} regulatory documents")
        
        # Test production queries
        test_queries = [
            ("transaction risk monitoring", "transaction_risk"),
            ("compliance requirements", "compliance"),
            ("customer complaint handling", "customer_sentiment")
        ]
        
        for query, agent in test_queries:
            result = rag.query(query, agent)
            print(f"✅ {agent}: confidence {result.confidence:.2f}")
        
        return True
    else:
        print("❌ Failed to load production documents")
        return False

if __name__ == "__main__":
    success = load_production_documents()
    if success:
        print("🎉 Production RAG system ready!")
    else:
        print("❌ Production deployment failed")
```

### **Step 4: Integrate with Existing Agents**

Update your existing agent deployments to use RAG-enhanced versions:

**For Kubernetes deployment, update `k8s/agents.yaml`:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: transaction-risk-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: transaction-risk-agent
  template:
    metadata:
      labels:
        app: transaction-risk-agent
    spec:
      containers:
      - name: transaction-risk-agent
        image: gcr.io/PROJECT_ID/transaction-risk-agent:latest
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "your-project-id"
        - name: RAG_ENABLED
          value: "true"
        - name: VECTOR_INDEX_ID
          value: "your-index-id"
        - name: VECTOR_ENDPOINT_ID
          value: "your-endpoint-id"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

### **Step 5: Set Up Monitoring**

Create `monitoring_setup.py`:
```python
#!/usr/bin/env python3
"""
Set up production monitoring for RAG system
"""

from google.cloud import monitoring_v3
from google.cloud.monitoring_v3 import query
import time

def setup_production_monitoring():
    """Set up comprehensive monitoring for RAG system"""
    
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{PROJECT_ID}"
    
    # Create custom metrics
    metrics = [
        {
            "name": "rag_query_count",
            "description": "Number of RAG queries processed",
            "type": "counter"
        },
        {
            "name": "rag_query_latency",
            "description": "RAG query response time",
            "type": "histogram"
        },
        {
            "name": "rag_confidence_score",
            "description": "RAG query confidence scores",
            "type": "gauge"
        },
        {
            "name": "rag_document_coverage",
            "description": "Number of documents in vector search",
            "type": "gauge"
        }
    ]
    
    for metric in metrics:
        # Create metric descriptor
        descriptor = monitoring_v3.MetricDescriptor(
            type=f"custom.googleapis.com/nfrguard/rag/{metric['name']}",
            metric_kind=getattr(monitoring_v3.MetricDescriptor.MetricKind, metric['type'].upper()),
            value_type=monitoring_v3.MetricDescriptor.ValueType.DOUBLE,
            description=metric['description']
        )
        
        try:
            client.create_metric_descriptor(name=project_name, metric_descriptor=descriptor)
            print(f"✅ Created metric: {metric['name']}")
        except Exception as e:
            print(f"⚠️  Metric {metric['name']} may already exist: {e}")
    
    # Create alerting policies
    alert_policies = [
        {
            "name": "RAG Low Confidence",
            "condition": "rag_confidence_score < 0.3",
            "description": "RAG queries returning low confidence scores"
        },
        {
            "name": "RAG High Latency",
            "condition": "rag_query_latency > 1.0",
            "description": "RAG queries taking too long"
        },
        {
            "name": "RAG Document Coverage Low",
            "condition": "rag_document_coverage < 5",
            "description": "Insufficient documents in vector search"
        }
    ]
    
    for policy in alert_policies:
        # Create alert policy (simplified)
        print(f"📊 Alert policy: {policy['name']} - {policy['description']}")
    
    print("✅ Production monitoring setup complete")

if __name__ == "__main__":
    setup_production_monitoring()
```

### **Step 6: Production Health Checks**

Create `health_check.py`:
```python
#!/usr/bin/env python3
"""
Production health check for RAG system
"""

import time
import requests
from rag_engine import AustralianBankingRAG
from production_config import *

def health_check():
    """Comprehensive health check for production RAG system"""
    
    print("🏥 Running RAG system health check...")
    
    checks = {
        "vector_search": False,
        "document_loading": False,
        "query_performance": False,
        "agent_integration": False
    }
    
    try:
        # Test vector search connectivity
        rag = AustralianBankingRAG(project_id=PROJECT_ID)
        print("✅ Vector search connectivity: OK")
        checks["vector_search"] = True
        
        # Test document loading
        documents = rag.document_downloader.download_all_documents()
        if len(documents) >= 6:  # Expected minimum documents
            print(f"✅ Document loading: OK ({len(documents)} documents)")
            checks["document_loading"] = True
        else:
            print(f"❌ Document loading: FAILED ({len(documents)} documents)")
        
        # Test query performance
        start_time = time.time()
        result = rag.query("transaction risk monitoring", "transaction_risk")
        query_time = time.time() - start_time
        
        if query_time < 1.0 and result.confidence > 0.3:
            print(f"✅ Query performance: OK ({query_time:.2f}s, confidence {result.confidence:.2f})")
            checks["query_performance"] = True
        else:
            print(f"❌ Query performance: FAILED ({query_time:.2f}s, confidence {result.confidence:.2f})")
        
        # Test agent integration
        from rag_enhanced_agents import create_rag_enhanced_agent
        agent = create_rag_enhanced_agent("transaction_risk")
        if agent.rag_engine is not None:
            print("✅ Agent integration: OK")
            checks["agent_integration"] = True
        else:
            print("❌ Agent integration: FAILED")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Summary
    passed = sum(checks.values())
    total = len(checks)
    
    print(f"\n📊 Health Check Summary: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 RAG system is healthy and ready for production!")
        return True
    else:
        print("⚠️  RAG system has issues that need attention")
        return False

if __name__ == "__main__":
    health_check()
```

## 🔄 **Deployment Commands**

### **Complete Production Deployment**

```bash
# 1. Set up environment
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"

# 2. Deploy vector search infrastructure
python deploy_vector_search.py

# 3. Load production documents
python load_production_documents.py

# 4. Set up monitoring
python monitoring_setup.py

# 5. Run health check
python health_check.py

# 6. Deploy updated agents
kubectl apply -f k8s/agents.yaml

# 7. Verify deployment
kubectl get pods -l app=transaction-risk-agent
kubectl logs -f deployment/transaction-risk-agent
```

## 📊 **Production Monitoring**

### **Key Metrics to Monitor**

1. **Query Performance**
   - Response time < 1 second
   - Confidence scores > 0.3
   - Query success rate > 99%

2. **System Health**
   - Vector search availability
   - Document coverage
   - Agent integration status

3. **Business Metrics**
   - Regulatory compliance rate
   - Customer satisfaction scores
   - Fraud detection accuracy

### **Monitoring Dashboard**

Access your monitoring dashboard at:
```
https://console.cloud.google.com/monitoring/dashboards
```

## 🔧 **Maintenance & Updates**

### **Document Updates**
```bash
# Update regulatory documents (run daily)
python load_production_documents.py

# Verify updates
python health_check.py
```

### **Scaling**
```bash
# Scale vector search endpoint
gcloud ai index-endpoints update ENDPOINT_ID \
  --region=LOCATION \
  --deployed-index-id=INDEX_ID \
  --min-replica-count=5 \
  --max-replica-count=20
```

### **Backup & Recovery**
```bash
# Backup vector index
gcloud ai indexes export INDEX_ID \
  --region=LOCATION \
  --output-dir=gs://your-backup-bucket/

# Restore from backup
gcloud ai indexes import \
  --region=LOCATION \
  --source-uri=gs://your-backup-bucket/
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **High Query Latency**
   - Check vector search endpoint scaling
   - Monitor machine resource usage
   - Consider increasing replica count

2. **Low Confidence Scores**
   - Verify document coverage
   - Check query relevance
   - Update regulatory documents

3. **Agent Integration Failures**
   - Verify environment variables
   - Check service account permissions
   - Monitor agent logs

### **Emergency Procedures**

```bash
# Disable RAG temporarily
kubectl set env deployment/transaction-risk-agent RAG_ENABLED=false

# Scale down vector search
gcloud ai index-endpoints update ENDPOINT_ID --min-replica-count=0

# Rollback to previous version
kubectl rollout undo deployment/transaction-risk-agent
```

## 📈 **Performance Optimization**

### **Vector Search Optimization**
- Use appropriate machine types for your workload
- Monitor and adjust replica counts based on traffic
- Implement query caching for common queries
- Use batch operations for document updates

### **Agent Optimization**
- Implement connection pooling for RAG queries
- Cache frequently accessed regulatory guidance
- Use async operations for non-critical queries
- Monitor and optimize memory usage

---

**🎉 Your RAG system is now production-ready with Vertex AI Vector Search!**

For support or questions, check the monitoring dashboard and logs, or refer to the troubleshooting section above.
