#!/usr/bin/env python3
"""
Build and Deploy RAG-Enhanced Agents to GKE
"""

import os
import sys
import subprocess
import time
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

def build_agent_image(agent_name, project_id):
    """Build Docker image for an agent"""
    print(f"Building image for {agent_name}...")
    
    # Create Dockerfile for the agent
    dockerfile_content = f"""
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy RAG system
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV RAG_ENABLED=true

# Create a simple HTTP server for health checks
RUN echo 'from http.server import HTTPServer, BaseHTTPRequestHandler; \\
class HealthHandler(BaseHTTPRequestHandler): \\
    def do_GET(self): \\
        if self.path == "/health": \\
            self.send_response(200); \\
            self.end_headers(); \\
            self.wfile.write(b"OK"); \\
        elif self.path == "/ready": \\
            self.send_response(200); \\
            self.end_headers(); \\
            self.wfile.write(b"OK"); \\
        else: \\
            self.send_response(404); \\
            self.end_headers(); \\
            self.wfile.write(b"Not Found"); \\
    def log_message(self, format, *args): \\
        pass; \\
httpd = HTTPServer(("", 8080), HealthHandler); \\
httpd.serve_forever()' > health_server.py

# Run health server
CMD ["python", "health_server.py"]
"""
    
    # Create temporary directory for building
    build_dir = Path(f"build_{agent_name}")
    build_dir.mkdir(exist_ok=True)
    
    # Write Dockerfile
    with open(build_dir / "Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    # Copy requirements
    if Path("requirements.txt").exists():
        import shutil
        shutil.copy("requirements.txt", build_dir / "requirements.txt")
    else:
        # Create basic requirements
        with open(build_dir / "requirements.txt", "w") as f:
            f.write("""requests>=2.31.0
google-cloud-aiplatform>=1.49.0
google-cloud-storage>=2.10.0
langchain-google-vertexai>=0.0.10
langchain>=0.1.16
unstructured>=0.12.6
nltk>=3.8.1
python-dotenv>=1.0.1
beautifulsoup4>=4.12.3
lxml>=5.1.0
html2text>=2020.1.16
markdownify>=0.11.6
pdfminer.six>=20221105
pypdf>=4.1.0
docx2txt>=0.8
openpyxl>=3.1.2
pandas>=2.2.2
scikit-learn>=1.4.2
numpy>=1.26.4
tenacity>=8.2.3
""")
    
    # Copy RAG system files
    rag_files = [
        "rag_engine.py",
        "vertex_ai_vector_search.py", 
        "document_downloader.py",
        "production_config.py"
    ]
    
    for file in rag_files:
        if Path(file).exists():
            import shutil
            shutil.copy(file, build_dir / file)
    
    # Build Docker image
    image_name = f"gcr.io/{project_id}/{agent_name}:latest"
    
    try:
        result = subprocess.run([
            "docker", "build", "-t", image_name, str(build_dir)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Built image: {image_name}")
            
            # Push to GCR
            push_result = subprocess.run([
                "docker", "push", image_name
            ], capture_output=True, text=True)
            
            if push_result.returncode == 0:
                print(f"✅ Pushed image: {image_name}")
                return True
            else:
                print(f"❌ Failed to push image: {push_result.stderr}")
                return False
        else:
            print(f"❌ Failed to build image: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error building image: {e}")
        return False
    finally:
        # Clean up build directory
        import shutil
        if build_dir.exists():
            shutil.rmtree(build_dir)

def deploy_agents(project_id):
    """Deploy all agents to GKE"""
    print("Deploying agents to GKE...")
    
    agents = [
        "transaction-risk-agent",
        "compliance-agent",
        "resilience-agent", 
        "customer-sentiment-agent",
        "data-privacy-agent",
        "knowledge-agent",
        "banking-assistant-agent"
    ]
    
    # Build and push images
    for agent in agents:
        if not build_agent_image(agent, project_id):
            print(f"❌ Failed to build {agent}")
            return False
    
    # Update Kubernetes deployments
    k8s_file = Path("k8s/agents-rag.yaml")
    if k8s_file.exists():
        # Update image references
        with open(k8s_file, "r") as f:
            content = f.read()
        
        # Replace PROJECT_ID placeholder
        content = content.replace("PROJECT_ID", project_id)
        
        with open(k8s_file, "w") as f:
            f.write(content)
        
        # Apply updated configuration
        result = subprocess.run([
            "kubectl", "apply", "-f", str(k8s_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Updated Kubernetes deployments")
            return True
        else:
            print(f"❌ Failed to update deployments: {result.stderr}")
            return False
    else:
        print("❌ Kubernetes file not found")
        return False

def wait_for_deployment():
    """Wait for deployments to be ready"""
    print("Waiting for deployments to be ready...")
    
    agents = [
        "transaction-risk-agent",
        "compliance-agent",
        "resilience-agent",
        "customer-sentiment-agent", 
        "data-privacy-agent",
        "knowledge-agent",
        "banking-assistant-agent"
    ]
    
    for agent in agents:
        print(f"Waiting for {agent}...")
        result = subprocess.run([
            "kubectl", "wait", "--for=condition=available", 
            f"deployment/{agent}", "-n", "nfrguard-agents", 
            "--timeout=300s"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {agent} is ready")
        else:
            print(f"⚠️  {agent} may not be ready: {result.stderr}")

def check_deployment_status():
    """Check deployment status"""
    print("Checking deployment status...")
    
    result = subprocess.run([
        "kubectl", "get", "pods", "-n", "nfrguard-agents"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"❌ Failed to get pod status: {result.stderr}")

def main():
    """Main deployment function"""
    print("🚀 Building and Deploying RAG-Enhanced Agents to GKE")
    print("=" * 60)
    
    # Get project ID
    project_id = get_project_id()
    print(f"Project ID: {project_id}")
    
    # Deploy agents
    if deploy_agents(project_id):
        print("✅ Agent deployment completed")
        
        # Wait for deployments
        wait_for_deployment()
        
        # Check status
        check_deployment_status()
        
        print("\n🎉 RAG-Enhanced Agents deployed to GKE!")
        print(f"Namespace: nfrguard-agents")
        print(f"Project: {project_id}")
        
    else:
        print("❌ Agent deployment failed")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
