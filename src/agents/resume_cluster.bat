@echo off
REM Resume Cluster - Scale back up

echo 🚀 Resuming cluster...
echo.

REM Check cluster connection
echo 📋 Checking cluster connection...
kubectl cluster-info >nul 2>&1
if errorlevel 1 (
    echo ❌ Cannot connect. Updating kubeconfig...
    aws eks update-kubeconfig --region ap-southeast-2 --name fintech-ai-aws-cluster
)

REM Resume agents
echo 📈 Scaling agents back up...
kubectl scale deployment banking-assistant-agent --replicas=3 -n nfrguard-agents
kubectl scale deployment compliance-agent --replicas=2 -n nfrguard-agents
kubectl scale deployment transaction-risk-agent --replicas=2 -n nfrguard-agents
kubectl scale deployment customer-sentiment-agent --replicas=2 -n nfrguard-agents
kubectl scale deployment data-privacy-agent --replicas=2 -n nfrguard-agents
kubectl scale deployment knowledge-agent --replicas=1 -n nfrguard-agents
kubectl scale deployment resilience-agent --replicas=1 -n nfrguard-agents

REM Resume Bank of Anthos
echo 📈 Scaling Bank of Anthos back up...
kubectl scale deployment frontend --replicas=1
kubectl scale deployment contacts --replicas=1
kubectl scale deployment userservice --replicas=1
kubectl scale deployment balancereader --replicas=1
kubectl scale deployment ledgerwriter --replicas=1
kubectl scale deployment transactionhistory --replicas=1
kubectl scale deployment loadgenerator --replicas=1
kubectl scale statefulset accounts-db --replicas=1
kubectl scale statefulset ledger-db --replicas=1

echo.
echo ⏳ Waiting 30 seconds for pods to start...
timeout /t 30 /nobreak

echo.
echo 📊 Current status:
kubectl get pods -n nfrguard-agents
echo.
kubectl get pods

echo.
echo ✅ Cluster resumed!
echo.
echo 🌐 Frontend URL:
kubectl get svc frontend -o jsonpath="{.status.loadBalancer.ingress[0].hostname}"
echo.
echo.
pause

