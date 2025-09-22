#!/usr/bin/env python3
"""
Setup GCP Alerting Policies for NFRGuard AI Agents
"""

import subprocess
import json
import os

def get_project_id():
    """Get Google Cloud project ID"""
    try:
        result = subprocess.run([
            "gcloud", "config", "get-value", "project"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "gen-lang-client-0578497058"
    except Exception:
        return "gen-lang-client-0578497058"

def create_alert_policies():
    """Create alerting policies for NFRGuard"""
    project_id = get_project_id()
    
    print("🚨 Setting up NFRGuard Alerting Policies...")
    print(f"📊 Project ID: {project_id}")
    print()
    
    # Alert policies
    alert_policies = [
        {
            "displayName": "NFRGuard - High CPU Usage",
            "conditions": [
                {
                    "displayName": "High CPU Usage",
                    "conditionThreshold": {
                        "filter": f'resource.type="k8s_container" AND resource.labels.cluster_name="bank-of-anthos" AND resource.labels.namespace_name="nfrguard-agents" AND metric.type="kubernetes.io/container/cpu/core_usage_time"',
                        "comparison": "COMPARISON_GREATER_THAN",
                        "thresholdValue": 0.8,
                        "duration": "300s",
                        "aggregations": [
                            {
                                "alignmentPeriod": "60s",
                                "perSeriesAligner": "ALIGN_MEAN",
                                "crossSeriesReducer": "REDUCE_MEAN"
                            }
                        ]
                    }
                }
            ],
            "alertStrategy": {
                "autoClose": "1800s"
            },
            "enabled": True
        },
        {
            "displayName": "NFRGuard - High Memory Usage",
            "conditions": [
                {
                    "displayName": "High Memory Usage",
                    "conditionThreshold": {
                        "filter": f'resource.type="k8s_container" AND resource.labels.cluster_name="bank-of-anthos" AND resource.labels.namespace_name="nfrguard-agents" AND metric.type="kubernetes.io/container/memory/used_bytes"',
                        "comparison": "COMPARISON_GREATER_THAN",
                        "thresholdValue": 500000000,  # 500MB
                        "duration": "300s",
                        "aggregations": [
                            {
                                "alignmentPeriod": "60s",
                                "perSeriesAligner": "ALIGN_MEAN",
                                "crossSeriesReducer": "REDUCE_MEAN"
                            }
                        ]
                    }
                }
            ],
            "alertStrategy": {
                "autoClose": "1800s"
            },
            "enabled": True
        }
    ]
    
    # Save alert policies
    alert_file = "nfrguard_alert_policies.json"
    with open(alert_file, "w") as f:
        json.dump(alert_policies, f, indent=2)
    
    print(f"✅ Alert policies saved to: {alert_file}")
    print()
    
    return alert_policies

def main():
    """Main function to set up alerting"""
    print("🛡️  NFRGuard Alerting Setup")
    print("=" * 50)
    
    # Create alert policies
    alert_policies = create_alert_policies()
    
    print("🎉 Alerting setup complete!")
    print()
    print("📋 Next Steps:")
    print("   1. Set up notification channels in GCP Console")
    print("   2. Create alert policies using the JSON files")
    print("   3. Test alert delivery")
    print()
    print("🌐 GCP Console Links:")
    print("   • Alerts: https://console.cloud.google.com/monitoring/alerting?project=gen-lang-client-0578497058")
    print("   • Notifications: https://console.cloud.google.com/monitoring/alerting/notifications?project=gen-lang-client-0578497058")
    print("   • Dashboard: https://console.cloud.google.com/monitoring/dashboards?project=gen-lang-client-0578497058")
    print()
    print("=" * 50)

if __name__ == "__main__":
    main()