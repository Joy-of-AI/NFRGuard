#!/usr/bin/env python3
"""
Complete Setup Script - NFRGuard Agents on AWS EKS
Automated setup from scratch to running agents
"""

import subprocess
import sys
import time
import json
import os

def run_command(cmd, check=True, shell=True):
    """Run a shell command and return output"""
    print(f"▶ Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=shell, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        if check:
            sys.exit(1)
        return e

def check_prerequisites():
    """Check if required tools are installed"""
    print("\n📋 Checking prerequisites...")
    
    tools = {
        'aws': 'aws --version',
        'kubectl': 'kubectl version --client',
        'eksctl': './eksctl/eksctl.exe version',
        'docker': 'docker --version'
    }
    
    for tool, cmd in tools.items():
        result = run_command(cmd, check=False)
        if result.returncode == 0:
            print(f"✅ {tool} found")
        else:
            print(f"❌ {tool} not found")
            sys.exit(1)

def check_aws_config():
    """Verify AWS CLI is configured"""
    print("\n🔐 Checking AWS configuration...")
    result = run_command('aws sts get-caller-identity', check=False)
    if result.returncode != 0:
        print("❌ AWS CLI not configured. Run: aws configure")
        sys.exit(1)
    
    identity = json.loads(result.stdout)
    print(f"✅ AWS Account: {identity['Account']}")
    print(f"✅ User: {identity['Arn']}")

def check_cluster_exists():
    """Check if EKS cluster already exists"""
    print("\n☸️ Checking for existing EKS cluster...")
    result = run_command('aws eks list-clusters --region ap-southeast-2', check=False)
    if result.returncode == 0:
        clusters = json.loads(result.stdout)
        if 'fintech-ai-aws-cluster' in clusters.get('clusters', []):
            print("✅ Cluster exists: fintech-ai-aws-cluster")
            return True
    print("ℹ️ No existing cluster found")
    return False

def create_cluster():
    """Create EKS cluster"""
    print("\n🏗️ Creating EKS cluster (takes ~12-15 minutes)...")
    cmd = """./eksctl/eksctl.exe create cluster \
      --name fintech-ai-aws-cluster \
      --region ap-southeast-2 \
      --with-oidc \
      --managed \
      --nodegroup-name ng-spot \
      --nodes 2 \
      --nodes-min 1 \
      --nodes-max 3 \
      --node-type t3.large \
      --spot"""
    
    result = run_command(cmd, check=False)
    if result.returncode != 0 and 'AlreadyExistsException' not in result.stderr:
        print("❌ Failed to create cluster")
        sys.exit(1)
    print("✅ Cluster ready")

def connect_to_cluster():
    """Connect kubectl to the cluster"""
    print("\n🔌 Connecting to cluster...")
    run_command('aws eks update-kubeconfig --region ap-southeast-2 --name fintech-ai-aws-cluster')
    print("✅ Connected to cluster")

def setup_bedrock_permissions():
    """Add Bedrock permissions to node IAM role"""
    print("\n🔐 Setting up Bedrock permissions...")
    
    # Get node role name
    result = run_command('aws iam list-roles --query "Roles[?contains(RoleName, \'fintech-ai-aws-cluster-node-NodeInstanceRole\')].RoleName" --output text', check=False)
    if result.returncode == 0 and result.stdout.strip():
        role_name = result.stdout.strip()
        print(f"✅ Found node role: {role_name}")
        
        # Attach Bedrock policy
        run_command(f'aws iam attach-role-policy --role-name {role_name} --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess', check=False)
        print("✅ Bedrock permissions added")
    else:
        print("⚠️ Could not find node role automatically")

def build_and_push_images():
    """Build and push Docker images"""
    print("\n🐳 Building and pushing Docker images...")
    result = run_command('bash scripts/build_and_push_images.sh', check=False)
    if result.returncode == 0:
        print("✅ Images built and pushed")
    else:
        print("⚠️ Some images may have failed")

def deploy_agents():
    """Deploy agents to EKS"""
    print("\n🚀 Deploying agents to EKS...")
    
    # Update environment variable for working Claude model
    run_command('kubectl set env deployment -n nfrguard-agents --all BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0', check=False)
    
    result = run_command('bash scripts/deploy_to_eks.sh', check=False)
    print("✅ Agents deployed")

def deploy_bank_of_anthos():
    """Deploy Bank of Anthos application"""
    print("\n🏦 Deploying Bank of Anthos...")
    
    # Create JWT secret
    run_command('kubectl apply -f ../extras/jwt/jwt-secret.yaml', check=False)
    
    # Deploy application
    run_command('kubectl apply -f ../kubernetes-manifests/', check=False)
    
    # Disable tracing (GCP-specific feature)
    print("⚙️ Configuring for AWS...")
    deployments = ['frontend', 'contacts', 'userservice', 'balancereader', 'ledgerwriter', 'transactionhistory']
    for dep in deployments:
        run_command(f'kubectl set env deployment/{dep} ENABLE_TRACING=false', check=False)
    
    print("✅ Bank of Anthos deployed")

def verify_deployment():
    """Verify all pods are running"""
    print("\n📊 Verifying deployment...")
    
    print("\n🤖 Agent Pods:")
    run_command('kubectl get pods -n nfrguard-agents')
    
    print("\n🏦 Bank of Anthos Pods:")
    run_command('kubectl get pods -n default')
    
    print("\n🌐 Services:")
    run_command('kubectl get svc -n nfrguard-agents')
    run_command('kubectl get svc frontend -n default')

def main():
    """Main setup flow"""
    print("🚀 NFRGuard Agents - Complete Setup")
    print("=" * 50)
    
    # Change to agents directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Step 1: Prerequisites
    check_prerequisites()
    check_aws_config()
    
    # Step 2: Cluster
    cluster_exists = check_cluster_exists()
    if not cluster_exists:
        create_cluster()
    else:
        connect_to_cluster()
    
    # Step 3: Permissions
    setup_bedrock_permissions()
    
    # Step 4: Build images
    build_images = input("\n❓ Build and push Docker images? (y/n): ").lower()
    if build_images == 'y':
        build_and_push_images()
    
    # Step 5: Deploy agents
    deploy_agents = input("\n❓ Deploy agents to EKS? (y/n): ").lower()
    if deploy_agents == 'y':
        deploy_agents()
        
        # Wait for agents to be ready
        print("\n⏳ Waiting for agents to start (30 seconds)...")
        time.sleep(30)
    
    # Step 6: Deploy Bank of Anthos
    deploy_bank = input("\n❓ Deploy Bank of Anthos? (y/n): ").lower()
    if deploy_bank == 'y':
        deploy_bank_of_anthos()
        
        # Wait for Bank of Anthos to start
        print("\n⏳ Waiting for Bank of Anthos to start (60 seconds)...")
        time.sleep(60)
    
    # Step 7: Verify
    verify_deployment()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\n📝 Next steps:")
    print("  1. Test agents: kubectl port-forward -n nfrguard-agents svc/banking-assistant-agent 8080:8080")
    print("  2. Access Bank of Anthos: kubectl get svc frontend")
    print("  3. Pause cluster: bash scripts/pause_cluster.sh")
    print("  4. Resume cluster: bash scripts/resume_cluster.sh")

if __name__ == '__main__':
    main()

