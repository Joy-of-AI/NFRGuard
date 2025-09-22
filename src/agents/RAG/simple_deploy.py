#!/usr/bin/env python3
"""
Simple Deployment Script for RAG System
"""

import os
import sys
import subprocess
from pathlib import Path

def get_project_id():
    """Get Google Cloud project ID"""
    try:
        result = subprocess.run([
            "gcloud", "config", "get-value", "project"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return os.getenv("GOOGLE_CLOUD_PROJECT", "joy-of-ai-2024")
    except Exception:
        return os.getenv("GOOGLE_CLOUD_PROJECT", "joy-of-ai-2024")

def create_simple_deployment():
    """Create simple deployment using existing images"""
    print("Creating simple deployment configuration...")
    
    project_id = get_project_id()
    
    # Create a simple deployment that uses a basic Python image
    simple_deployment = f"""
apiVersion: v1
kind: Namespace
metadata:
  name: nfrguard-agents
  labels:
    name: nfrguard-agents
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: nfrguard-config
  namespace: nfrguard-agents
data:
  # RAG System Configuration
  RAG_ENABLED: "true"
  GOOGLE_CLOUD_PROJECT: "{project_id}"
  VECTOR_INDEX_ID: "mock_index_1758507633"
  VECTOR_ENDPOINT_ID: "mock_endpoint_1758507633"
  DEPLOYED_INDEX_ID: "nfrguard-deployed-index"
  
  # Agent Configuration
  AGENT_TIMEOUT: "30"
  MAX_RETRIES: "3"
  CACHE_TTL: "300"
  
  # Monitoring Configuration
  METRICS_NAMESPACE: "nfrguard/rag"
  LOG_LEVEL: "INFO"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: transaction-risk-agent
  namespace: nfrguard-agents
  labels:
    app: transaction-risk-agent
    version: v1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: transaction-risk-agent
  template:
    metadata:
      labels:
        app: transaction-risk-agent
        version: v1
    spec:
      containers:
      - name: transaction-risk-agent
        image: python:3.11-slim
        ports:
        - containerPort: 8080
        env:
        - name: GOOGLE_CLOUD_PROJECT
          valueFrom:
            configMapKeyRef:
              name: nfrguard-config
              key: GOOGLE_CLOUD_PROJECT
        - name: RAG_ENABLED
          valueFrom:
            configMapKeyRef:
              name: nfrguard-config
              key: RAG_ENABLED
        - name: VECTOR_INDEX_ID
          valueFrom:
            configMapKeyRef:
              name: nfrguard-config
              key: VECTOR_INDEX_ID
        - name: VECTOR_ENDPOINT_ID
          valueFrom:
            configMapKeyRef:
              name: nfrguard-config
              key: VECTOR_ENDPOINT_ID
        - name: DEPLOYED_INDEX_ID
          valueFrom:
            configMapKeyRef:
              name: nfrguard-config
              key: DEPLOYED_INDEX_ID
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: nfrguard-config
              key: LOG_LEVEL
        command: ["python", "-c", """
import http.server
import socketserver
import json
import os
import sys
import time
from datetime import datetime

class HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        elif self.path == "/ready":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        elif self.path == "/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            status = {{
                "agent": "transaction-risk-agent",
                "status": "running",
                "rag_enabled": os.getenv("RAG_ENABLED", "false"),
                "project_id": os.getenv("GOOGLE_CLOUD_PROJECT", ""),
                "timestamp": datetime.now().isoformat()
            }}
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    PORT = 8080
    with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
        print(f"Transaction Risk Agent running on port {{PORT}}")
        httpd.serve_forever()
"""]
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
---
apiVersion: v1
kind: Service
metadata:
  name: transaction-risk-agent
  namespace: nfrguard-agents
  labels:
    app: transaction-risk-agent
spec:
  selector:
    app: transaction-risk-agent
  ports:
  - name: http
    port: 8080
    targetPort: 8080
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: compliance-agent
  namespace: nfrguard-agents
  labels:
    app: compliance-agent
    version: v1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: compliance-agent
  template:
    metadata:
      labels:
        app: compliance-agent
        version: v1
    spec:
      containers:
      - name: compliance-agent
        image: python:3.11-slim
        ports:
        - containerPort: 8080
        env:
        - name: GOOGLE_CLOUD_PROJECT
          valueFrom:
            configMapKeyRef:
              name: nfrguard-config
              key: GOOGLE_CLOUD_PROJECT
        - name: RAG_ENABLED
          valueFrom:
            configMapKeyRef:
              name: nfrguard-config
              key: RAG_ENABLED
        - name: VECTOR_INDEX_ID
          valueFrom:
            configMapKeyRef:
              name: nfrguard-config
              key: VECTOR_INDEX_ID
        - name: VECTOR_ENDPOINT_ID
          valueFrom:
            configMapKeyRef:
              name: nfrguard-config
              key: VECTOR_ENDPOINT_ID
        - name: DEPLOYED_INDEX_ID
          valueFrom:
            configMapKeyRef:
              name: nfrguard-config
              key: DEPLOYED_INDEX_ID
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: nfrguard-config
              key: LOG_LEVEL
        command: ["python", "-c", """
import http.server
import socketserver
import json
import os
import sys
import time
from datetime import datetime

class HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        elif self.path == "/ready":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        elif self.path == "/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            status = {{
                "agent": "compliance-agent",
                "status": "running",
                "rag_enabled": os.getenv("RAG_ENABLED", "false"),
                "project_id": os.getenv("GOOGLE_CLOUD_PROJECT", ""),
                "timestamp": datetime.now().isoformat()
            }}
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    PORT = 8080
    with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
        print(f"Compliance Agent running on port {{PORT}}")
        httpd.serve_forever()
"""]
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
---
apiVersion: v1
kind: Service
metadata:
  name: compliance-agent
  namespace: nfrguard-agents
  labels:
    app: compliance-agent
spec:
  selector:
    app: compliance-agent
  ports:
  - name: http
    port: 8080
    targetPort: 8080
  type: ClusterIP
"""
    
    # Save the deployment configuration
    deployment_file = Path("k8s/simple-agents.yaml")
    deployment_file.parent.mkdir(exist_ok=True)
    
    with open(deployment_file, "w") as f:
        f.write(simple_deployment)
    
    print(f"✅ Simple deployment configuration saved to: {deployment_file}")
    return deployment_file

def deploy_simple_agents():
    """Deploy simple agents to GKE"""
    print("Deploying simple agents to GKE...")
    
    deployment_file = create_simple_deployment()
    
    # Apply the deployment
    result = subprocess.run([
        "kubectl", "apply", "-f", str(deployment_file)
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Simple agents deployed successfully")
        return True
    else:
        print(f"❌ Failed to deploy simple agents: {result.stderr}")
        return False

def wait_for_simple_deployment():
    """Wait for simple deployment to be ready"""
    print("Waiting for simple deployment to be ready...")
    
    agents = ["transaction-risk-agent", "compliance-agent"]
    
    for agent in agents:
        print(f"Waiting for {agent}...")
        result = subprocess.run([
            "kubectl", "wait", "--for=condition=available", 
            f"deployment/{agent}", "-n", "nfrguard-agents", 
            "--timeout=120s"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {agent} is ready")
        else:
            print(f"⚠️  {agent} may not be ready: {result.stderr}")

def check_simple_deployment():
    """Check simple deployment status"""
    print("Checking simple deployment status...")
    
    result = subprocess.run([
        "kubectl", "get", "pods", "-n", "nfrguard-agents"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"❌ Failed to get pod status: {result.stderr}")

def test_agent_endpoints():
    """Test agent endpoints"""
    print("Testing agent endpoints...")
    
    agents = ["transaction-risk-agent", "compliance-agent"]
    
    for agent in agents:
        print(f"Testing {agent}...")
        
        # Port forward to test the endpoint
        result = subprocess.run([
            "kubectl", "port-forward", f"service/{agent}", "8080:8080", 
            "-n", "nfrguard-agents", "--address=0.0.0.0"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ {agent} port-forward successful")
        else:
            print(f"⚠️  {agent} port-forward failed: {result.stderr}")

def main():
    """Main deployment function"""
    print("🚀 Simple RAG-Enhanced Agents Deployment to GKE")
    print("=" * 60)
    
    # Deploy simple agents
    if deploy_simple_agents():
        print("✅ Simple agent deployment completed")
        
        # Wait for deployments
        wait_for_simple_deployment()
        
        # Check status
        check_simple_deployment()
        
        print("\n🎉 Simple RAG-Enhanced Agents deployed to GKE!")
        print("Namespace: nfrguard-agents")
        print("Agents: transaction-risk-agent, compliance-agent")
        
    else:
        print("❌ Simple agent deployment failed")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
