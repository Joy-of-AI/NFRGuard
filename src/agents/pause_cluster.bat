@echo off
REM Pause Cluster - Scale to 0 to save money

echo 🛑 Pausing cluster to save money...
echo.

REM Scale all agents to 0
echo 📉 Scaling agents to 0...
kubectl scale deployment --all --replicas=0 -n nfrguard-agents

REM Scale Bank of Anthos to 0
echo 📉 Scaling Bank of Anthos to 0...
kubectl scale deployment --all --replicas=0
kubectl scale statefulset --all --replicas=0

echo.
echo ✅ Cluster paused! Resources scaled to 0.
echo.
echo 💰 Cost: Only ~$0.10/hour for control plane (~$2.40/day)
echo.
echo 🚀 To resume tomorrow: Run RESUME_TOMORROW.bat
echo.
pause

