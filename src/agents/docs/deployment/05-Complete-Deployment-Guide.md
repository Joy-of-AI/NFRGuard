# 🔄 Complete Restart Guide - NFRGuard Agents on AWS

## 🚀 **Quick Start (If You've Done This Before)**

**If cluster exists and you just paused it:**
```bash
cd /d/Joy_of_AI/Fintech_AI_AWS/bank-of-anthos/src/agents
bash scripts/resume_cluster.sh
```

**Start from scratch (automated):**
```bash
cd /d/Joy_of_AI/Fintech_AI_AWS/bank-of-anthos/src/agents
python scripts/complete_setup.py
```

**Pause when done:**
```bash
bash scripts/pause_cluster.sh  # Scale to 0, keep cluster (~$2.40/day)
# OR
bash scripts/cleanup_aws_resources.sh  # Delete everything ($0/day)
```

---

## 🛑 **Current Status: Resources Stopped**

All AWS resources have been cleaned up to avoid charges. This guide will help you restart the entire system when needed.

## ⚡ **Critical Fixes Applied**

This guide includes all fixes for common issues:

1. ✅ **Bedrock Model**: Uses `anthropic.claude-3-5-sonnet-20240620-v1:0` (supported version)
2. ✅ **IAM Permissions**: Bedrock + EventBridge policies attached
3. ✅ **Agent Class**: All agents use `BedrockAgent` (not `Agent`)
4. ✅ **/ready Endpoint**: All agents respond to readiness probes
5. ✅ **JWT Secret**: Bank of Anthos JWT key included
6. ✅ **Tracing Disabled**: GCP Cloud Trace disabled for AWS
7. ✅ **Windows Support**: PowerShell commands documented

## 💰 **AWS Charges - What to Expect**

### **When Resources Are Running:**
- **EKS Cluster**: ~$0.10/hour (with spot instances)
- **ECR Storage**: ~$0.10/GB/month  
- **S3 Storage**: ~$0.023/GB/month
- **DynamoDB**: ~$0.25/million requests
- **Bedrock**: ~$0.003/1K tokens (Claude 3.5 Sonnet)

### **When Resources Are Stopped:**
- ✅ **EKS Cluster**: $0 (deleted)
- ✅ **ECR Storage**: $0 (repositories deleted)
- ✅ **S3 Storage**: $0 (buckets deleted)
- ✅ **DynamoDB**: $0 (tables deleted)
- ✅ **Bedrock**: Only charged when you make API calls

### **Cost Optimization Features:**
- ✅ **Spot instances** for EKS nodes (up to 90% savings)
- ✅ **Auto-scaling** based on demand
- ✅ **Resource limits** to prevent over-provisioning
- ✅ **On-demand billing** for transparency

## 📋 **What Was Preserved (No Charges)**

- ✅ **All source code** - Complete agent implementations
- ✅ **All scripts** - Setup, deployment, and cleanup scripts
- ✅ **All documentation** - Deployment guides and troubleshooting
- ✅ **All configurations** - Kubernetes manifests, Dockerfiles
- ✅ **Environment setup** - `.env` file with your credentials
- ✅ **All fixes and improvements** - HTTP server code, image fixes

## 📋 **Quick Reference - Prerequisites Checklist**

| Tool | Command to Check | Required Version | Status |
|------|------------------|------------------|--------|
| AWS CLI | `aws --version` | v2.x.x | ✅ |
| kubectl | `kubectl version --client` | v1.x.x | ✅ |
| eksctl | `./eksctl/eksctl.exe version` | 0.215.0 (bundled) | ✅ |
| Docker | `docker --version` | v20+ | ✅ |
| Git Bash | `bash --version` | Any recent version | ✅ |

**AWS Configuration:**
- [ ] AWS CLI configured with access keys
- [ ] Default region set to `ap-southeast-2`
- [ ] AWS account ID verified: `491085381971`

**AWS Resources Needed:**
- [ ] EKS cluster created or existing
- [ ] ECR repositories for images
- [ ] S3 buckets for storage
- [ ] DynamoDB tables
- [ ] Bedrock model access approved

## 🚀 **Restart Process** - ⚠️ RUN ALL COMMANDS IN GIT BASH

### Step 0: AWS CLI Configuration

**⚠️ CRITICAL: Do this first!** If AWS CLI is not configured, all subsequent steps will fail.

```bash
# Configure AWS CLI (if not already done)
aws configure
```

**You will be prompted for:**

| Prompt | Where to Find | Example |
|--------|---------------|---------|
| **AWS Access Key ID** | AWS Console → IAM → Security Credentials → Access keys | `AKIAIOSFODNN7EXAMPLE` |
| **AWS Secret Access Key** | Same location (shown only once when created) | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| **Default region name** | Use: `ap-southeast-2` | `ap-southeast-2` |
| **Default output format** | Use: `json` | `json` |

**Verify AWS CLI configuration:**
```bash
# Check AWS identity
aws sts get-caller-identity

# Should show your AWS Account ID and User ARN
```

**Expected Output:**
```json
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "491085381971",
    "Arn": "arn:aws:iam::491085381971:user/AWS_Acct"
}
```

### Step 1: Verify Prerequisites

```bash
# Navigate to agents directory
cd /d/Joy_of_AI/Fintech_AI_AWS/bank-of-anthos/src/agents

# Check if required tools are installed
aws --version
kubectl version --client
docker --version
git --version

# Check eksctl (use local bundled version)
./eksctl/eksctl.exe version

# Add eksctl to PATH for this session
export PATH=$PATH:$(pwd)/eksctl
eksctl version
```

**Expected Output:**
```
aws-cli/2.31.3 Python/3.13.7 Windows/11 exe/AMD64
Client Version: v1.32.2
Docker version 28.3.2
git version 2.x.x
0.215.0
```

### Step 1.5: Check Existing EKS Cluster

**Before creating a new cluster, check if one already exists:**

```bash
# List existing EKS clusters
aws eks list-clusters --region ap-southeast-2
```

**If cluster exists:**
```json
{
  "clusters": ["fintech-ai-aws-cluster"]
}
```

**Connect to existing cluster:**
```bash
aws eks update-kubeconfig --region ap-southeast-2 --name fintech-ai-aws-cluster

# Verify connection
kubectl get nodes
```

**If no cluster exists (empty list), continue to Step 2 to create one.**

### Step 2: Create EKS Cluster (if needed)

**Only run this if Step 1.5 showed no existing cluster.**

```bash
# Create EKS cluster with spot instances (takes ~12-15 minutes)
./eksctl/eksctl.exe create cluster \
  --name fintech-ai-aws-cluster \
  --region ap-southeast-2 \
  --with-oidc \
  --managed \
  --nodegroup-name ng-spot \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --node-type t3.large \
  --spot
```

**What this creates:**
- ✅ EKS Kubernetes cluster (v1.32)
- ✅ 2 managed nodes using t3.large spot instances (cost optimized)
- ✅ VPC with public/private subnets across 3 availability zones
- ✅ OIDC provider for IRSA (IAM Roles for Service Accounts)
- ✅ Add-ons: vpc-cni, kube-proxy, coredns, metrics-server
- ✅ Auto-scaling from 1-3 nodes based on demand

**Expected Output:**
```
2025-10-11 22:26:10 [ℹ]  eksctl version 0.215.0
2025-10-11 22:26:10 [ℹ]  using region ap-southeast-2
...
2025-10-11 22:40:18 [✔]  EKS cluster "fintech-ai-aws-cluster" in "ap-southeast-2" region is ready
2025-10-11 22:40:20 [ℹ]  kubectl command should work with "C:\\Users\\ah_am\\.kube\\config"
```

### Step 2.5: Verify Cluster and Node Group

```bash
# Verify cluster exists
aws eks list-clusters --region ap-southeast-2

# Check nodegroup status
aws eks list-nodegroups \
  --cluster-name fintech-ai-aws-cluster \
  --region ap-southeast-2

# Verify nodegroup is ACTIVE
aws eks describe-nodegroup \
  --cluster-name fintech-ai-aws-cluster \
  --nodegroup-name ng-spot \
  --region ap-southeast-2 \
  --query "nodegroup.status"
```

**Expected Output:**
```
"ACTIVE"
```

**Verify nodes are ready:**
```bash
kubectl get nodes
```

**Expected Output:**
```
NAME                                                STATUS   ROLES    AGE   VERSION
ip-192-168-7-230.ap-southeast-2.compute.internal    Ready    <none>   2m    v1.32.9-eks-113cf36
ip-192-168-77-101.ap-southeast-2.compute.internal   Ready    <none>   2m    v1.32.9-eks-113cf36
```

### Step 3: Setup Additional AWS Infrastructure (S3, ECR, DynamoDB)

```bash
# Set up S3 buckets, ECR repositories, DynamoDB tables
bash scripts/setup_aws_infrastructure.sh
```

**What this creates:**
- ✅ ECR repositories for all 7 agents
- ✅ S3 buckets for data storage
- ✅ DynamoDB tables for state management
- ✅ EventBridge for messaging
- ✅ IAM roles and policies

**Note:** You may see some "already exists" errors - this is normal and can be ignored.

### Step 4: Request Bedrock Model Access

**⚠️ Manual Step Required:**

1. **Go to AWS Console**: https://console.aws.amazon.com/bedrock/
2. **Navigate to**: Model Access
3. **Request access to**:
   - ✅ Claude 3.5 Sonnet
   - ✅ Titan Embeddings V2
4. **Wait for approval** (usually takes a few minutes)

**💡 Pro Tip:** Do this step while the infrastructure is being created to save time!

### Step 5: Build and Push Docker Images

```bash
# Build Docker images for all 7 agents and push to ECR
bash scripts/build_and_push_images.sh
```

**What this does:**
- ✅ Creates Dockerfiles for each agent
- ✅ Builds 7 Docker images locally
- ✅ Pushes images to ECR repositories
- ✅ Tags images with latest version

**Expected Output:**
```
✅ banking_assistant agent built and pushed successfully
✅ compliance_agent agent built and pushed successfully
✅ customer_sentiment agent built and pushed successfully
✅ data_privacy agent built and pushed successfully
✅ knowledge_agent agent built and pushed successfully
✅ resilience_agent agent built and pushed successfully
✅ transaction_risk agent built and pushed successfully
🎉 All Docker images built and pushed successfully!
```

### Step 6: Deploy to EKS

```bash
# Deploy all agents to EKS cluster
bash scripts/deploy_to_eks.sh
```

**What this deploys:**
- ✅ Namespace: `nfrguard-agents`
- ✅ Service Account with IRSA
- ✅ ConfigMap with environment variables
- ✅ Secrets for AWS credentials
- ✅ 7 Agent deployments (2 replicas each)
- ✅ Services for each agent
- ✅ Ingress for external access

**Expected Output:**
```
🚀 Deploying NFRGuard Agents to EKS
📋 Checking prerequisites...
✅ Prerequisites check passed
📦 Deploying namespace and service account...
✅ Namespace and service account deployed
⚙️ Deploying configuration...
✅ Configuration deployed
🤖 Deploying agents...
✅ Agents deployed
⏳ Waiting for deployments to be ready...
```

**Note:** If you see a timeout error, this is often normal. Pods may still be starting. Continue to Step 7 to verify.

### Step 7: Verify Deployment

**Check all resources across all namespaces:**
```bash
# Check all pods (across all namespaces)
kubectl get pods -A

# Check all services
kubectl get svc -A

# Check specific namespace pods
kubectl get pods -n nfrguard-agents

# Watch pods come online (wait until all show Running)
kubectl get pods -n nfrguard-agents -w
```

**Expected Result:**
```
NAME                                       READY   STATUS    RESTARTS   AGE
banking-assistant-agent-785b8b8c55-2bnwz   1/1     Running   0          2m
compliance-agent-95bc96889-j4cff           1/1     Running   0          2m
customer-sentiment-agent-55f6f8cff-9m9jx   1/1     Running   0          2m
data-privacy-agent-69fbcfdc46-k9wvv        1/1     Running   0          2m
knowledge-agent-7cb55cb45f-ffbr9           1/1     Running   0          2m
resilience-agent-54798b4d94-99l9d          1/1     Running   0          2m
transaction-risk-agent-9d49c9ffd-4smdg     1/1     Running   0          2m
```

### Step 8: Access the Application

**Check for LoadBalancer service:**
```bash
# List all services
kubectl get svc -A

# Look for LoadBalancer type services
kubectl get svc -n nfrguard-agents
```

**Expected Output (example):**
```
NAME                      TYPE           CLUSTER-IP       EXTERNAL-IP                                                                 PORT(S)          AGE
banking-assistant-agent   LoadBalancer   10.100.123.45    a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6.ap-southeast-2.elb.amazonaws.com        8080:30549/TCP   5m
compliance-agent          ClusterIP      10.100.234.56    <none>                                                                      8080/TCP         5m
...
```

**Access the application:**
```bash
# Once EXTERNAL-IP is shown (may take 2-3 minutes), access via browser:
# http://<EXTERNAL-IP>:8080

# Or use curl to test:
curl http://<EXTERNAL-IP>:8080/health
```

### Step 9: (Optional) Deploy RAG System

**RAG** = Retrieval-Augmented Generation (regulatory citations)

**Choose One:**

**Option A: Mock RAG (Recommended - $0 cost)** ⭐
```bash
# Deploy mock RAG (simple text search, no OpenSearch)
python RAG/mock_rag_engine.py

# Test it
kubectl port-forward -n nfrguard-agents svc/compliance-agent 8082:8080

curl -X POST http://localhost:8082/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are APRA CPS 230 requirements?"}'
```

**Benefits:**
- ✅ $0 cost (no OpenSearch)
- ✅ 42 regulatory documents
- ✅ Citations and sources
- ✅ Good accuracy (85%)
- ✅ Perfect for learning

**Option B: Full RAG with OpenSearch (~$700/month)**
```bash
# See: RAG/RAG_DEPLOYMENT.md for full deployment
# Only deploy if you need production-grade semantic search
```

**For details**: See `RAG/DEPLOY_RAG_DECISION.md`

### Step 10: Monitor and Check Logs

**View logs for specific pod:**
```bash
# Get pod name
kubectl get pods -n nfrguard-agents

# View logs for a specific pod
kubectl logs <pod-name> -n nfrguard-agents

# Example:
kubectl logs banking-assistant-agent-74f49d8575-h5fzm -n nfrguard-agents

# Follow logs in real-time
kubectl logs -f <pod-name> -n nfrguard-agents

# View logs for all pods of a deployment
kubectl logs -n nfrguard-agents deployment/banking-assistant-agent
```

**Monitor all pods continuously:**
```bash
# Watch all pods in real-time
kubectl get pods -A -w

# Watch specific namespace
kubectl get pods -n nfrguard-agents -w
```

**Check pod details if issues occur:**
```bash
# Describe pod for detailed status
kubectl describe pod <pod-name> -n nfrguard-agents

# Get events in namespace
kubectl get events -n nfrguard-agents --sort-by='.lastTimestamp'
```

## 🔧 **Troubleshooting (If Issues Occur)**

### Issue 1: Cannot access EKS cluster

**Symptoms:** `❌ Cannot access EKS cluster. Please check your kubeconfig.`

**Solution:**
```bash
# Check if cluster exists
aws eks list-clusters --region ap-southeast-2

# If empty [], no cluster exists - create one (see Step 2)
# If cluster exists, update kubeconfig
aws eks update-kubeconfig --region ap-southeast-2 --name fintech-ai-aws-cluster

# Verify connection
kubectl get nodes

# If still failing, check AWS CLI configuration
aws sts get-caller-identity
```

### Issue 2: eksctl Not Found

**Symptoms:** `❌ eksctl not found. Please install it first.`

**Solution:**
```bash
# Check if local eksctl exists
./eksctl/eksctl.exe version

# If it works, add to PATH
export PATH=$PATH:$(pwd)/eksctl

# Verify it works
eksctl version

# Then run setup again
bash scripts/setup_aws_infrastructure.sh
```

### Issue 3: Resource Already Exists

**Symptoms:** `ResourceInUseException: Table already exists` or similar

**Solution:**
```bash
# This is normal - ignore these errors
# The script will continue and create missing resources
# Just wait for the setup to complete
```

### Issue 4: ImagePullBackOff

**Symptoms:** Pods stuck in `ImagePullBackOff` status

**Solution:**
```bash
# Check if images exist in ECR
aws ecr describe-images --repository-name transaction-risk-agent --region ap-southeast-2

# Rebuild and push images
bash scripts/build_and_push_images.sh

# Restart deployments
kubectl rollout restart deployment -n nfrguard-agents
```

### Issue 5: CrashLoopBackOff

**Symptoms:** Pods starting but crashing immediately

**Solution:**
```bash
# Check pod logs
kubectl logs -n nfrguard-agents deployment/banking-assistant-agent

# Fix agent scripts if needed (HTTP server code)
python scripts/fix_agents.py

# Rebuild and redeploy
bash scripts/build_and_push_images.sh
bash scripts/deploy_to_eks.sh
```

### Issue 6: Bedrock Access Denied

**Symptoms:** Agents can't access Bedrock models

**Solution:**
1. **Check model access** in AWS Console
2. **Verify IAM permissions** for service account
3. **Check environment variables**:
   ```bash
   kubectl get configmap -n nfrguard-agents nfrguard-config -o yaml
   ```

### Issue 7: Pods Timeout During Deployment

**Symptoms:** `error: timed out waiting for the condition on deployments/transaction-risk-agent`

**Solution:**
```bash
# This is often normal - pods may still be starting
# Check pod status
kubectl get pods -n nfrguard-agents

# Check pod details
kubectl describe pod <pod-name> -n nfrguard-agents

# Check logs
kubectl logs <pod-name> -n nfrguard-agents

# Wait a few more minutes, then check again
# If ImagePullBackOff, see Issue 4
# If CrashLoopBackOff, see Issue 5
```

### Issue 8: Pods Running but Not Ready (0/1 Running)

**Symptoms:** 
- Pods show `0/1 Running` status
- Logs show `GET /ready HTTP/1.1 404` errors
- Pods are running but not becoming Ready

**Solution:**
```bash
# Check pod logs
kubectl logs <pod-name> -n nfrguard-agents --tail=20

# If you see "GET /ready HTTP/1.1 404" errors repeatedly:
# The agents need a /ready endpoint added

# This has been fixed in the current version
# Force restart to pull fixed images:
kubectl rollout restart deployment -n nfrguard-agents

# Verify all pods become Ready
kubectl get pods -n nfrguard-agents
```

### Issue 9: NameError: name 'Agent' is not defined

**Symptoms:**
```
Traceback (most recent call last):
  File "/app/agent.py", line 43, in <module>
    root_agent = Agent(
                 ^^^^^
NameError: name 'Agent' is not defined
```

**Solution:**
```bash
# This error occurs when agents use `Agent` instead of `BedrockAgent`
# Fixed in data_privacy_agent and resilience_agent

# After code fix, rebuild and push images:
bash scripts/build_and_push_images.sh

# Restart affected deployments:
kubectl rollout restart deployment/data-privacy-agent -n nfrguard-agents
kubectl rollout restart deployment/resilience-agent -n nfrguard-agents

# Verify pods are running
kubectl get pods -n nfrguard-agents
kubectl logs <pod-name> -n nfrguard-agents
```

### Issue 10: Bedrock Access Denied (CRITICAL)

**Symptoms:**
```
{"error": "An error occurred (AccessDeniedException) when calling the InvokeModel operation: 
User: arn:aws:sts::491085381971:assumed-role/eksctl-fintech-ai-aws-cluster-node-NodeInstanceRole-*/i-* 
is not authorized to perform: bedrock:InvokeModel on resource: arn:aws:bedrock:*::foundation-model/*"}
```

**This is CRITICAL** - Agents cannot function without Bedrock access!

**Solution:**

**Option A: Using AWS CLI (Fastest):**
```bash
# Get the node role name
kubectl get nodes -o wide

# Attach Bedrock policy to node role
aws iam attach-role-policy \
  --role-name eksctl-fintech-ai-aws-cluster-node-NodeInstanceRole-XXXXX \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

# Verify policy attached
aws iam list-attached-role-policies \
  --role-name eksctl-fintech-ai-aws-cluster-node-NodeInstanceRole-XXXXX

# Restart pods to pick up new permissions
kubectl rollout restart deployment -n nfrguard-agents

# Wait for pods to restart
kubectl get pods -n nfrguard-agents -w
```

**Option B: Using AWS Console:**
1. Go to: https://console.aws.amazon.com/iam/
2. Navigate to **Roles** → Search: `eksctl-fintech-ai-aws-cluster-node-NodeInstanceRole`
3. Click the role → **Add permissions** → **Attach policies**
4. Search: `AmazonBedrockFullAccess`
5. Select and **Attach policy**
6. Restart pods: `kubectl rollout restart deployment -n nfrguard-agents`

**Option C: Custom Policy (More Secure):**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/*"
        }
    ]
}
```

**Verify the fix:**
```bash
# Test an agent
kubectl port-forward -n nfrguard-agents svc/banking-assistant-agent 8080:8080
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What services do you provide?"}'
```

### Issue 11: EventBridge Access Denied (Warning)

**Symptoms:**
```
ERROR:shared.aws_messaging:Error ensuring rule exists for compliance.action: 
An error occurred (AccessDeniedException) when calling the DescribeRule operation
```

**Solution:**
```bash
# This is a warning - agents still function but EventBridge messaging is limited
# To fix, update the node IAM role with EventBridge permissions

# Attach EventBridge policy to node role
aws iam attach-role-policy \
  --role-name eksctl-fintech-ai-aws-cluster-node-NodeInstanceRole-XXXXX \
  --policy-arn arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess

# Restart pods
kubectl rollout restart deployment -n nfrguard-agents
```

## 🎯 **Quick Restart Commands (Summary)**

**Prerequisites (one-time setup):**
```bash
# Configure AWS CLI (if not done)
aws configure

# Verify configuration
aws sts get-caller-identity
```

**If cluster doesn't exist:**
```bash
# Create EKS cluster (~12-15 minutes)
./eksctl/eksctl.exe create cluster \
  --name fintech-ai-aws-cluster \
  --region ap-southeast-2 \
  --with-oidc \
  --managed \
  --nodegroup-name ng-spot \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --node-type t3.large \
  --spot
```

**If cluster exists:**
```bash
# Connect to existing cluster
aws eks update-kubeconfig --region ap-southeast-2 --name fintech-ai-aws-cluster
kubectl get nodes
```

**Deploy sequence:**
```bash
# 1. Setup infrastructure (S3, ECR, DynamoDB)
bash scripts/setup_aws_infrastructure.sh

# 2. Request Bedrock access (manual in AWS Console)

# 3. Build and push Docker images
bash scripts/build_and_push_images.sh

# 4. Deploy to EKS
bash scripts/deploy_to_eks.sh

# 5. Verify deployment
kubectl get pods -n nfrguard-agents
kubectl get svc -n nfrguard-agents
```

## 💰 **Cost Management**

### Estimated Costs (When Running)
- **EKS Cluster**: ~$0.10/hour (with spot instances)
- **ECR Storage**: ~$0.10/GB/month
- **S3 Storage**: ~$0.023/GB/month
- **DynamoDB**: ~$0.25/million requests
- **Bedrock**: ~$0.003/1K tokens (Claude 3.5 Sonnet)

### Cost Optimization Features
- ✅ **Spot instances** for EKS nodes (up to 90% savings)
- ✅ **Auto-scaling** based on demand
- ✅ **Resource limits** to prevent over-provisioning
- ✅ **On-demand billing** for transparency

## 🛑 **Stop Resources (When Done)**

### **Option 1: PAUSE - Keep Cluster, Stop Pods (Recommended)**

**Best for**: Coming back tomorrow or in a few days

**Git Bash:**
```bash
bash scripts/pause_cluster.sh
```

**Windows:**
```powershell
.\PAUSE_TONIGHT.bat
```

**What happens:**
- ✅ Scales all pods to 0 (stops them)
- ✅ Keeps cluster alive
- ✅ Preserves all configurations
- ✅ Keeps Docker images in ECR

**Cost:** ~$0.10/hour (~$2.40/day) - just control plane + nodes  
**Resume:** 2 minutes with `bash scripts/resume_cluster.sh`

---

### **Option 2: DELETE - Remove Everything**

**Best for**: Not using for a week+, want $0 cost

**Git Bash:**
```bash
echo "yes" | bash scripts/cleanup_aws_resources.sh
```

**What happens:**
- ❌ Deletes EKS cluster
- ❌ Deletes ECR repositories
- ❌ Deletes S3 buckets
- ❌ Deletes DynamoDB tables

**Cost:** $0/day  
**Restart:** 30 minutes with `python scripts/complete_setup.py`

## 📚 **Documentation References**

- **Complete Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Quick Redeploy Reference**: `QUICK_REDEPLOY.md`
- **Architecture Overview**: `ARCHITECTURE_AWS.md`
- **AWS Setup Guide**: `AWS_SETUP_GUIDE.md`

## 🎉 **Success Criteria**

Your restart is successful when:

- ✅ All 14 pods (7 agents × 2 replicas) are `Running`
- ✅ Health checks return `200 OK`
- ✅ Agents respond to chat requests
- ✅ No error logs in pod logs
- ✅ EKS cluster nodes are healthy

---

**🔒 All your code, configurations, and improvements are preserved!**
**🚀 You can restart the entire system anytime using this guide!**
