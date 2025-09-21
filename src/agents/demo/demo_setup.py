#!/usr/bin/env python3
"""
Demo Setup Script for NFRGuard Agents
Deploys agents and creates demo scenarios for video recording
"""

import os
import sys
import time
import json
import subprocess
from typing import Dict, List

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))
from shared.messaging import publish, subscribe, clear_subscriptions

class NFRGuardDemo:
    def __init__(self):
        self.agents = [
            "transaction-risk-agent",
            "compliance-agent", 
            "resilience-agent",
            "customer-sentiment-agent",
            "knowledge-agent",
            "data-privacy-agent",
            "banking-assistant"
        ]
        self.demo_events = []
        
    def setup_environment(self):
        """Set up the demo environment"""
        print("🚀 Setting up NFRGuard Demo Environment...")
        
        # Check if we're in the right directory
        if not os.path.exists("k8s/agents.yaml"):
            print("❌ Error: Run this script from src/agents directory")
            return False
            
        print("✅ Environment check passed")
        return True
        
    def deploy_agents(self):
        """Deploy agents to Kubernetes"""
        print("\n📦 Deploying NFRGuard Agents to GKE...")
        
        try:
            # Deploy agents
            result = subprocess.run([
                "kubectl", "apply", "-f", "k8s/agents.yaml"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Agents deployed successfully")
                print(result.stdout)
            else:
                print(f"❌ Deployment failed: {result.stderr}")
                return False
                
            # Wait for deployments to be ready
            print("\n⏳ Waiting for agents to be ready...")
            for agent in self.agents:
                subprocess.run([
                    "kubectl", "wait", "--for=condition=Available", 
                    f"deployment/{agent}", "--timeout=300s"
                ])
                
            print("✅ All agents are ready!")
            return True
            
        except Exception as e:
            print(f"❌ Error deploying agents: {e}")
            return False
            
    def setup_monitoring(self):
        """Set up real-time monitoring of agent logs"""
        print("\n📊 Setting up agent monitoring...")
        
        # Create monitoring script
        monitor_script = """#!/bin/bash
echo "🔍 NFRGuard Agent Monitoring Dashboard"
echo "======================================"
echo ""

# Function to show agent logs
show_agent_logs() {
    local agent=$1
    echo "📋 $agent logs:"
    kubectl logs deployment/$agent --tail=5 --follow &
}

# Start monitoring all agents
for agent in transaction-risk-agent compliance-agent resilience-agent customer-sentiment-agent knowledge-agent data-privacy-agent banking-assistant; do
    show_agent_logs $agent
done

echo "Press Ctrl+C to stop monitoring"
wait
"""
        
        with open("monitor_agents.sh", "w") as f:
            f.write(monitor_script)
            
        os.chmod("monitor_agents.sh", 0o755)
        print("✅ Monitoring script created: ./monitor_agents.sh")
        
    def create_demo_scenarios(self):
        """Create demo scenarios for the video"""
        print("\n🎬 Creating demo scenarios...")
        
        scenarios = {
            "normal_transaction": {
                "name": "Normal Transaction Flow",
                "description": "Customer makes a normal $50 purchase",
                "event": {
                    "event_type": "transaction.created",
                    "transaction_id": "txn_normal_001",
                    "amount": 50.00,
                    "account_id": "acc_12345",
                    "timestamp": "2025-01-14T14:30:00Z",
                    "destination": "local_store_abc",
                    "customer_profile": "normal_user"
                }
            },
            "suspicious_transaction": {
                "name": "Suspicious Transaction Detection",
                "description": "Customer attempts $25,000 transfer at 2 AM to foreign account",
                "event": {
                    "event_type": "transaction.created",
                    "transaction_id": "txn_suspicious_001",
                    "amount": 25000.00,
                    "account_id": "acc_12345",
                    "timestamp": "2025-01-14T02:00:00Z",  # 2 AM
                    "destination": "foreign_account_high_risk",
                    "customer_profile": "normal_user",  # But unusual behavior
                    "risk_factors": ["unusual_amount", "unusual_time", "foreign_destination"]
                }
            },
            "customer_complaint": {
                "name": "Customer Sentiment Analysis",
                "description": "Customer complains about blocked transaction",
                "event": {
                    "event_type": "customer.message",
                    "message_id": "msg_001",
                    "customer_id": "acc_12345",
                    "message": "Why was my transaction blocked? This is ridiculous! I need this money for my business!",
                    "timestamp": "2025-01-14T02:05:00Z",
                    "channel": "web_chat"
                }
            },
            "privacy_violation": {
                "name": "Data Privacy Protection",
                "description": "System log contains customer PII",
                "event": {
                    "event_type": "log.entry",
                    "log_id": "log_001",
                    "content": "Transaction txn_001 processed for customer john.doe@email.com with amount $25,000",
                    "timestamp": "2025-01-14T02:10:00Z",
                    "log_level": "INFO",
                    "service": "ledger-writer"
                }
            }
        }
        
        # Save scenarios to file
        with open("demo_scenarios.json", "w") as f:
            json.dump(scenarios, f, indent=2)
            
        print("✅ Demo scenarios created: demo_scenarios.json")
        return scenarios
        
    def run_demo_scenario(self, scenario_name: str, scenarios: Dict):
        """Run a specific demo scenario"""
        if scenario_name not in scenarios:
            print(f"❌ Scenario '{scenario_name}' not found")
            return False
            
        scenario = scenarios[scenario_name]
        print(f"\n🎬 Running scenario: {scenario['name']}")
        print(f"📝 Description: {scenario['description']}")
        
        # Publish the event
        event = scenario['event']
        publish(event['event_type'], event)
        
        print(f"✅ Event published: {event['event_type']}")
        print(f"📊 Event data: {json.dumps(event, indent=2)}")
        
        # Wait for agent responses
        print("⏳ Waiting for agent responses...")
        time.sleep(3)
        
        return True
        
    def show_agent_status(self):
        """Show current status of all agents"""
        print("\n📊 NFRGuard Agent Status:")
        print("=" * 50)
        
        for agent in self.agents:
            try:
                result = subprocess.run([
                    "kubectl", "get", "deployment", agent, 
                    "-o", "jsonpath={.status.readyReplicas}/{.spec.replicas}"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    status = result.stdout.strip()
                    if status and status != "0/0":
                        print(f"✅ {agent}: {status} replicas ready")
                    else:
                        print(f"❌ {agent}: Not ready")
                else:
                    print(f"❌ {agent}: Error checking status")
                    
            except Exception as e:
                print(f"❌ {agent}: {e}")
                
    def create_demo_script(self):
        """Create a script to run the full demo"""
        demo_script = """#!/usr/bin/env python3
'''
NFRGuard Demo Execution Script
Run this to execute the full demo sequence
'''

import time
import json
from demo_setup import NFRGuardDemo

def main():
    demo = NFRGuardDemo()
    
    print("🎬 NFRGuard Demo - AI Banking Security")
    print("=" * 50)
    
    # Load scenarios
    with open("demo_scenarios.json", "r") as f:
        scenarios = json.load(f)
    
    # Demo sequence
    print("\\n🎯 Demo Sequence:")
    print("1. Normal Transaction")
    print("2. Suspicious Transaction (Fraud Detection)")
    print("3. Customer Complaint (Sentiment Analysis)")
    print("4. Privacy Violation (Data Protection)")
    
    input("\\nPress Enter to start demo...")
    
    # Run each scenario
    for i, (scenario_name, scenario) in enumerate(scenarios.items(), 1):
        print(f"\\n--- Scenario {i}: {scenario['name']} ---")
        demo.run_demo_scenario(scenario_name, scenarios)
        
        if i < len(scenarios):
            input("\\nPress Enter for next scenario...")
    
    print("\\n🎉 Demo completed!")
    print("\\n📊 Check agent logs for detailed responses:")
    print("kubectl logs deployment/transaction-risk-agent")
    print("kubectl logs deployment/compliance-agent")
    print("kubectl logs deployment/resilience-agent")
    print("kubectl logs deployment/customer-sentiment-agent")
    print("kubectl logs deployment/knowledge-agent")
    print("kubectl logs deployment/data-privacy-agent")

if __name__ == "__main__":
    main()
"""
        
        with open("run_demo.py", "w") as f:
            f.write(demo_script)
            
        os.chmod("run_demo.py", 0o755)
        print("✅ Demo execution script created: ./run_demo.py")
        
    def cleanup(self):
        """Clean up demo resources"""
        print("\n🧹 Cleaning up demo resources...")
        
        try:
            # Delete agents
            subprocess.run(["kubectl", "delete", "-f", "k8s/agents.yaml"])
            print("✅ Agents removed")
            
            # Clean up files
            files_to_remove = ["monitor_agents.sh", "demo_scenarios.json", "run_demo.py"]
            for file in files_to_remove:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"✅ Removed {file}")
                    
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

def main():
    """Main demo setup function"""
    demo = NFRGuardDemo()
    
    print("🛡️ NFRGuard Demo Setup")
    print("=" * 30)
    
    # Setup environment
    if not demo.setup_environment():
        return
        
    # Deploy agents
    if not demo.deploy_agents():
        print("❌ Failed to deploy agents")
        return
        
    # Setup monitoring
    demo.setup_monitoring()
    
    # Create scenarios
    scenarios = demo.create_demo_scenarios()
    
    # Create demo script
    demo.create_demo_script()
    
    # Show status
    demo.show_agent_status()
    
    print("\n🎉 Demo setup complete!")
    print("\n📋 Next steps:")
    print("1. Run: ./monitor_agents.sh (in separate terminal)")
    print("2. Run: python run_demo.py")
    print("3. Record your demo video!")
    print("\n🌐 Bank of Anthos frontend: http://34.40.211.236")

if __name__ == "__main__":
    main()

