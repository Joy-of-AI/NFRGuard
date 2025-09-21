# 🚀 Deployment & Operations Guide

## How to Deploy and Run Your AI Agents

This guide covers everything you need to deploy Bank of Anthos with NFRGuard AI agents and keep them running smoothly.

## Quick Start (5 minutes)

### Prerequisites
- Google Cloud project with billing enabled
- `gcloud` and `kubectl` installed
- This repository downloaded

### Installing Google Agent Development Kit (ADK)

```bash
# Navigate to the right directory
cd D:\Joy_of_AI\Google_Bank_of_Anthos

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
.venv\Scripts\activate.ps1

# Install ADK - Follow https://google.github.io/adk-docs/get-started/
pip install google-adk

# Verify your installation
pip show google-adk
```

**Note:** The ADK is required for building and deploying AI agents. Make sure to follow the official documentation for the latest installation instructions.

### Deploy Everything
```bash
# Set your project
export PROJECT_ID="your-project-id"
export REGION="australia-southeast1"

# Create the cluster
gcloud container clusters create-auto bank-of-anthos \
  --project=$PROJECT_ID \
  --region=$REGION

# Deploy the application
kubectl apply -f ./bank-of-anthos/extras/jwt/jwt-secret.yaml
kubectl apply -f ./bank-of-anthos/kubernetes-manifests

# Wait for everything to start
kubectl wait --for=condition=Available deployment --all --timeout=600s

# Get your frontend URL
kubectl get service frontend -o jsonpath="http://{.status.loadBalancer.ingress[0].ip}"
```

**Result:** You'll have a working banking application with AI agents monitoring it!

## Detailed Deployment Steps

### Step 1: Set Up Google Cloud

#### Enable Required APIs
```bash
gcloud services enable container.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
```

#### Authenticate and Set Project
```bash
gcloud auth login
gcloud config set project $PROJECT_ID
```

### Step 2: Create GKE Cluster

#### Why GKE?
- **Microservices need orchestration** - Bank of Anthos has 8+ separate services
- **Auto-scaling** - Handles traffic spikes automatically
- **Load balancing** - Distributes traffic across multiple instances
- **Managed infrastructure** - Google handles the complex parts

#### Create Cluster
```bash
gcloud container clusters create-auto bank-of-anthos \
  --project=$PROJECT_ID \
  --region=$REGION \
  --enable-stackdriver-kubernetes
```

**What this creates:**
- Kubernetes cluster with 3 nodes
- Automatic container orchestration
- Built-in monitoring and logging
- Load balancer for external access

### Step 3: Deploy Bank of Anthos

#### Deploy Authentication
```bash
kubectl apply -f ./bank-of-anthos/extras/jwt/jwt-secret.yaml
```
**Why needed:** Users need to login - this provides the security keys.

#### Deploy Application Services
```bash
kubectl apply -f ./bank-of-anthos/kubernetes-manifests
```

**What gets deployed:**
- **Frontend** - Web interface users see
- **User Service** - Handles login and accounts
- **Ledger Services** - Process transactions
- **Database Services** - Store user data and transactions
- **Load Generator** - Simulates user activity

### Step 4: Verify Deployment

#### Check All Services Are Running
```bash
kubectl get pods
```
**Expected:** All pods should show `STATUS: Running` and `READY: 1/1`

#### Get Frontend URL
```bash
kubectl get service frontend -o jsonpath="http://{.status.loadBalancer.ingress[0].ip}"
```
**Expected:** URL like `http://34.xx.xx.xx`

#### Test the Application
1. Open the URL in your browser
2. Create an account or use demo credentials
3. Make a test transaction
4. Verify everything works

## Running Your AI Agents

### Option 1: Demo Mode (Easiest)
```bash
cd bank-of-anthos/src/agents/demo
python enhanced_database_monitor.py
```

**What this does:**
- Monitors real database transactions
- Shows all 7 agents reacting in real-time
- Perfect for demos and testing
- No additional deployment needed

### Option 2: Full Production Deployment
```bash
# Deploy agents to Kubernetes
kubectl apply -f ./bank-of-anthos/src/agents/k8s/agents.yaml

# Monitor agent logs
kubectl logs deployment/transaction-risk-agent --tail=10 -f
kubectl logs deployment/compliance-agent --tail=10 -f
# ... (repeat for each agent)
```

**What this does:**
- Runs agents as production services
- Integrates with monitoring systems
- Handles high transaction volumes
- Requires building Docker images first

## Daily Operations

### Check System Health
```bash
# Are all services running?
kubectl get pods

# How much resources are they using?
kubectl top pods

# Any recent errors?
kubectl get events --sort-by='.lastTimestamp'
```

### Monitor AI Agent Performance
```bash
# Watch live agent activity
python demo/enhanced_database_monitor.py

# Check agent logs
kubectl logs deployment/transaction-risk-agent --tail=50
kubectl logs deployment/compliance-agent --tail=50
```

### View Application Logs
```bash
# Frontend logs
kubectl logs deployment/frontend --tail=50

# Database logs
kubectl logs deployment/ledger-db-0 --tail=50

# All services
kubectl logs --all-containers=true --tail=10
```

## Scaling and Performance

### Scale Services Up
```bash
# Scale frontend to handle more users
kubectl scale deployment frontend --replicas=3

# Scale transaction processing
kubectl scale deployment ledgerwriter --replicas=2
```

### Monitor Performance
```bash
# Check resource usage
kubectl top pods

# Check service performance
kubectl get services
kubectl describe service frontend
```

## Troubleshooting

### Common Issues and Solutions

#### "Pods won't start"
```bash
# Check pod status
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Common fixes:
kubectl delete pod <pod-name>  # Restart pod
kubectl apply -f ./bank-of-anthos/kubernetes-manifests  # Re-apply config
```

#### "Can't access frontend"
```bash
# Check service
kubectl get service frontend
kubectl describe service frontend

# Check if load balancer is ready
kubectl get service frontend -o jsonpath="http://{.status.loadBalancer.ingress[0].ip}"

# If empty, wait 2-3 minutes and retry
```

#### "Agents not responding"
```bash
# Check if demo script can connect to database
kubectl exec ledger-db-0 -- psql -U admin -d postgresdb -c "SELECT COUNT(*) FROM transactions;"

# Restart demo script
cd demo
python enhanced_database_monitor.py
```

#### "High resource usage"
```bash
# Check resource usage
kubectl top pods

# Scale up if needed
kubectl scale deployment frontend --replicas=2
```

### Emergency Procedures

#### Restart Everything
```bash
# Delete and recreate all deployments
kubectl delete deployment --all
kubectl apply -f ./bank-of-anthos/kubernetes-manifests
kubectl wait --for=condition=Available deployment --all --timeout=600s
```

#### Reset Database
```bash
# Delete and recreate databases (WARNING: Loses all data)
kubectl delete statefulset ledger-db accounts-db
kubectl apply -f ./bank-of-anthos/kubernetes-manifests
```

## Monitoring and Alerting

### Set Up Monitoring
```bash
# Enable monitoring services
gcloud services enable monitoring.googleapis.com

# Apply alert policies
gcloud alpha monitoring policies create --policy-from-file=monitoring/alert_policies.yaml
```

### View Metrics
1. **Google Cloud Console:** https://console.cloud.google.com/monitoring
2. **Kubernetes Dashboard:** `kubectl proxy` then http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
3. **Command Line:** `kubectl top pods`

## Security Best Practices

### Network Security
- Services communicate within the cluster
- External access only through load balancer
- Database not directly accessible from internet

### Access Control
- Use Kubernetes RBAC for user permissions
- Rotate JWT secrets regularly
- Monitor access logs

### Data Protection
- Databases use persistent volumes
- Regular backups recommended
- Encrypt sensitive data

## Cost Management

### Monitor Costs
```bash
# Check cluster resource usage
kubectl top nodes
kubectl top pods

# View costs in Google Cloud Console
# https://console.cloud.google.com/billing
```

### Optimize Costs
- Use appropriate machine types
- Scale down during low usage
- Delete cluster when not needed
- Monitor resource usage patterns

## Backup and Recovery

### Backup Data
```bash
# Create database backups
kubectl exec ledger-db-0 -- pg_dump -U admin postgresdb > ledger_backup.sql
kubectl exec accounts-db-0 -- pg_dump -U admin postgresdb > accounts_backup.sql
```

### Restore Data
```bash
# Restore from backup
kubectl exec -i ledger-db-0 -- psql -U admin postgresdb < ledger_backup.sql
kubectl exec -i accounts-db-0 -- psql -U admin postgresdb < accounts_backup.sql
```

## Cleanup

### When You're Done
```bash
# Delete the cluster (stops all charges)
gcloud container clusters delete bank-of-anthos \
  --project=$PROJECT_ID \
  --region=$REGION \
  --quiet
```

### Keep Running
If you want to keep the system running:
- Monitor costs in Google Cloud Console
- Set up billing alerts
- Consider using preemptible instances for cost savings

## Production Considerations

### For Production Deployment
1. **Use managed databases** (Cloud SQL) instead of in-cluster PostgreSQL
2. **Set up proper monitoring** and alerting
3. **Implement backup strategies** for data
4. **Use production-grade secrets management**
5. **Set up CI/CD pipelines** for deployments
6. **Implement proper logging** and log aggregation
7. **Use production-ready container images**
8. **Set up disaster recovery** procedures

### Security Hardening
1. **Network policies** to restrict pod communication
2. **Pod security policies** to limit container capabilities
3. **Regular security updates** for base images
4. **Secrets management** using Google Secret Manager
5. **Audit logging** for all access

This guide gets you from zero to a fully functional AI-powered banking system in minutes! 🚀
