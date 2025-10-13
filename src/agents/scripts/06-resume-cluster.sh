#!/bin/bash
# Resume Cluster - Scale back up

echo "🚀 Resuming cluster..."
echo ""

# Check if cluster is accessible
echo "📋 Checking cluster connection..."
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to cluster. Updating kubeconfig..."
    aws eks update-kubeconfig --region ap-southeast-2 --name fintech-ai-aws-cluster
fi

# Resume agents (to original replica counts)
echo "📈 Scaling agents back up..."
kubectl scale deployment banking-assistant-agent --replicas=3 -n nfrguard-agents
kubectl scale deployment compliance-agent --replicas=2 -n nfrguard-agents
kubectl scale deployment transaction-risk-agent --replicas=2 -n nfrguard-agents
kubectl scale deployment customer-sentiment-agent --replicas=2 -n nfrguard-agents
kubectl scale deployment data-privacy-agent --replicas=2 -n nfrguard-agents
kubectl scale deployment knowledge-agent --replicas=1 -n nfrguard-agents
kubectl scale deployment resilience-agent --replicas=1 -n nfrguard-agents

# Resume Bank of Anthos
echo "📈 Scaling Bank of Anthos back up..."
kubectl scale deployment frontend --replicas=1 -n default
kubectl scale deployment contacts --replicas=1 -n default
kubectl scale deployment userservice --replicas=1 -n default
kubectl scale deployment balancereader --replicas=1 -n default
kubectl scale deployment ledgerwriter --replicas=1 -n default
kubectl scale deployment transactionhistory --replicas=1 -n default
kubectl scale deployment loadgenerator --replicas=1 -n default

# Resume stateful sets
kubectl scale statefulset accounts-db --replicas=1 -n default
kubectl scale statefulset ledger-db --replicas=1 -n default

echo ""
echo "⏳ Waiting for pods to start (30 seconds)..."
sleep 30

echo ""
echo "📊 Current status:"
kubectl get pods -n nfrguard-agents
echo ""
kubectl get pods -n default

echo ""
echo "✅ Cluster resumed!"
echo ""
echo "🌐 Frontend URL:"
kubectl get svc frontend -n default -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
echo ""

