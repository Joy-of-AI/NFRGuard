#!/bin/bash
# Pause Cluster - Scale down to save money

echo "🛑 Pausing cluster to save money..."
echo ""

# Scale all agents to 0 replicas
echo "📉 Scaling agents to 0 replicas..."
kubectl scale deployment --all --replicas=0 -n nfrguard-agents

# Scale Bank of Anthos to 0 replicas
echo "📉 Scaling Bank of Anthos to 0 replicas..."
kubectl scale deployment --all --replicas=0 -n default

# Scale stateful sets to 0
kubectl scale statefulset --all --replicas=0 -n default

echo ""
echo "✅ Cluster paused! Resources scaled to 0."
echo ""
echo "💰 Cost: Only ~$0.10/hour for the cluster control plane"
echo ""
echo "🚀 To resume tomorrow: bash scripts/resume_cluster.sh"

