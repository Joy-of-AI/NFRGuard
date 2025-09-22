#!/usr/bin/env python3
"""
Setup automated document updates using cron (Linux/Mac) or Task Scheduler (Windows)
"""

import os
import sys
import platform
from pathlib import Path

def setup_linux_cron():
    """Setup cron job for Linux/Mac"""
    print("Setting up cron job for Linux/Mac...")
    
    # Get current directory
    current_dir = Path(__file__).parent.absolute()
    python_path = sys.executable
    script_path = current_dir / "update_documents.py"
    
    # Create cron job entry
    cron_entry = f"0 2 * * * cd {current_dir} && {python_path} {script_path} >> {current_dir}/cron.log 2>&1"
    
    print(f"Cron entry to add:")
    print(f"  {cron_entry}")
    print()
    print("To add this cron job:")
    print("  1. Run: crontab -e")
    print("  2. Add the line above")
    print("  3. Save and exit")
    print()
    print("This will run the document update daily at 2:00 AM")

def setup_windows_task():
    """Setup Task Scheduler for Windows"""
    print("Setting up Task Scheduler for Windows...")
    
    # Get current directory
    current_dir = Path(__file__).parent.absolute()
    python_path = sys.executable
    script_path = current_dir / "update_documents.py"
    
    # Create PowerShell script for Task Scheduler
    ps_script = f"""
# PowerShell script for automated document updates
Set-Location "{current_dir}"
& "{python_path}" "{script_path}"
"""
    
    ps_script_path = current_dir / "update_documents.ps1"
    with open(ps_script_path, "w") as f:
        f.write(ps_script)
    
    print(f"Created PowerShell script: {ps_script_path}")
    print()
    print("To set up Task Scheduler:")
    print("  1. Open Task Scheduler")
    print("  2. Create Basic Task")
    print("  3. Name: 'RAG Document Update'")
    print("  4. Trigger: Daily at 2:00 AM")
    print("  5. Action: Start a program")
    print(f"  6. Program: powershell.exe")
    print(f"  7. Arguments: -File \"{ps_script_path}\"")
    print()
    print("This will run the document update daily at 2:00 AM")

def setup_kubernetes_cronjob():
    """Setup Kubernetes CronJob for containerized environments"""
    print("Setting up Kubernetes CronJob...")
    
    cronjob_yaml = """
apiVersion: batch/v1
kind: CronJob
metadata:
  name: rag-document-update
  namespace: nfrguard-agents
spec:
  schedule: "0 2 * * *"  # Daily at 2:00 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: document-updater
            image: gcr.io/PROJECT_ID/rag-document-updater:latest
            env:
            - name: GOOGLE_CLOUD_PROJECT
              value: "your-project-id"
            - name: GOOGLE_APPLICATION_CREDENTIALS
              value: "/var/secrets/google/key.json"
            command:
            - python
            - update_documents.py
            volumeMounts:
            - name: service-account
              mountPath: /var/secrets/google
              readOnly: true
          volumes:
          - name: service-account
            secret:
              secretName: google-service-account
          restartPolicy: OnFailure
"""
    
    cronjob_file = Path(__file__).parent / "k8s" / "document-update-cronjob.yaml"
    cronjob_file.parent.mkdir(exist_ok=True)
    
    with open(cronjob_file, "w") as f:
        f.write(cronjob_yaml)
    
    print(f"Created Kubernetes CronJob: {cronjob_file}")
    print()
    print("To deploy the CronJob:")
    print("  kubectl apply -f k8s/document-update-cronjob.yaml")
    print()
    print("To check CronJob status:")
    print("  kubectl get cronjobs -n nfrguard-agents")
    print("  kubectl get jobs -n nfrguard-agents")

def main():
    """Main setup function"""
    print("🔄 Setting up automated document updates")
    print("=" * 50)
    
    system = platform.system().lower()
    
    if system == "linux" or system == "darwin":  # Linux or Mac
        setup_linux_cron()
    elif system == "windows":
        setup_windows_task()
    else:
        print(f"Unsupported system: {system}")
        return False
    
    # Also show Kubernetes option
    print("\n" + "=" * 50)
    setup_kubernetes_cronjob()
    
    print("\n✅ Automated document update setup complete!")
    print("Choose the method that best fits your deployment environment.")
    
    return True

if __name__ == "__main__":
    main()
