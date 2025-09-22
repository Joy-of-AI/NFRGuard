#!/usr/bin/env python3
"""
Create GCP Dashboard via Console - Step by Step Guide
"""

import webbrowser
import subprocess
import json

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

def create_dashboard_guide():
    """Create step-by-step guide for dashboard creation"""
    project_id = get_project_id()
    
    print("🛡️  NFRGuard GCP Dashboard Creation Guide")
    print("=" * 50)
    print(f"📊 Project ID: {project_id}")
    print()
    
    # Dashboard URL
    dashboard_url = f"https://console.cloud.google.com/monitoring/dashboards?project={project_id}"
    print(f"🌐 Dashboard URL: {dashboard_url}")
    
    # Step-by-step instructions
    steps = [
        {
            "step": 1,
            "title": "Open GCP Console",
            "description": "Click the dashboard URL above to open GCP Monitoring",
            "action": "Click 'Create Dashboard' button"
        },
        {
            "step": 2,
            "title": "Add System Health Widget",
            "description": "Add a scorecard widget for system health",
            "action": "Click 'Add Widget' > 'Scorecard'",
            "config": {
                "title": "System Health Overview",
                "metric": "kubernetes.io/container/ready",
                "filter": f"resource.type=\"k8s_container\" AND resource.labels.cluster_name=\"bank-of-anthos\" AND resource.labels.namespace_name=\"nfrguard-agents\"",
                "aggregation": "Mean",
                "alignment": "60s"
            }
        },
        {
            "step": 3,
            "title": "Add CPU Usage Widget",
            "description": "Add a line chart for CPU usage by agent",
            "action": "Click 'Add Widget' > 'Line Chart'",
            "config": {
                "title": "AI Agent CPU Usage",
                "metric": "kubernetes.io/container/cpu/core_usage_time",
                "filter": f"resource.type=\"k8s_container\" AND resource.labels.cluster_name=\"bank-of-anthos\" AND resource.labels.namespace_name=\"nfrguard-agents\"",
                "aggregation": "Rate",
                "groupBy": "resource.labels.container_name",
                "alignment": "60s"
            }
        },
        {
            "step": 4,
            "title": "Add Memory Usage Widget",
            "description": "Add a line chart for memory usage",
            "action": "Click 'Add Widget' > 'Line Chart'",
            "config": {
                "title": "AI Agent Memory Usage",
                "metric": "kubernetes.io/container/memory/used_bytes",
                "filter": f"resource.type=\"k8s_container\" AND resource.labels.cluster_name=\"bank-of-anthos\" AND resource.labels.namespace_name=\"nfrguard-agents\"",
                "aggregation": "Mean",
                "groupBy": "resource.labels.container_name",
                "alignment": "60s"
            }
        },
        {
            "step": 5,
            "title": "Add Network Traffic Widget",
            "description": "Add a line chart for network traffic",
            "action": "Click 'Add Widget' > 'Line Chart'",
            "config": {
                "title": "Network Traffic",
                "metric": "kubernetes.io/container/network/received_bytes_count",
                "filter": f"resource.type=\"k8s_container\" AND resource.labels.cluster_name=\"bank-of-anthos\" AND resource.labels.namespace_name=\"nfrguard-agents\"",
                "aggregation": "Rate",
                "alignment": "300s"
            }
        },
        {
            "step": 6,
            "title": "Add Error Rate Widget",
            "description": "Add a scorecard for error monitoring",
            "action": "Click 'Add Widget' > 'Scorecard'",
            "config": {
                "title": "Error Rate",
                "metric": "kubernetes.io/container/restart_count",
                "filter": f"resource.type=\"k8s_container\" AND resource.labels.cluster_name=\"bank-of-anthos\" AND resource.labels.namespace_name=\"nfrguard-agents\"",
                "aggregation": "Rate",
                "alignment": "300s"
            }
        },
        {
            "step": 7,
            "title": "Save Dashboard",
            "description": "Save your dashboard with a descriptive name",
            "action": "Click 'Save' and name it 'NFRGuard AI Banking Security Dashboard'"
        }
    ]
    
    print("📋 Step-by-Step Dashboard Creation:")
    print()
    
    for step in steps:
        print(f"Step {step['step']}: {step['title']}")
        print(f"   📝 {step['description']}")
        print(f"   🎯 {step['action']}")
        
        if 'config' in step:
            print("   ⚙️  Configuration:")
            for key, value in step['config'].items():
                print(f"      {key}: {value}")
        
        print()
    
    print("🎉 Dashboard Creation Complete!")
    print()
    print("📊 Your dashboard will show:")
    print("   • System health status")
    print("   • CPU usage by AI agent")
    print("   • Memory usage by AI agent")
    print("   • Network traffic")
    print("   • Error rates")
    print()
    print("🚨 Next Steps:")
    print("   1. Set up alerts for critical metrics")
    print("   2. Configure notification channels")
    print("   3. Test the dashboard with real data")
    print("   4. Share with your team")
    print()
    print("=" * 50)
    
    return dashboard_url

def open_dashboard():
    """Open the dashboard URL in browser"""
    dashboard_url = create_dashboard_guide()
    
    print("🌐 Opening GCP Console...")
    try:
        webbrowser.open(dashboard_url)
        print("✅ Dashboard opened in your browser!")
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print(f"💡 Please manually open: {dashboard_url}")

if __name__ == "__main__":
    open_dashboard()
