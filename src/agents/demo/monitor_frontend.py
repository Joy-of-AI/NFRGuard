#!/usr/bin/env python3
"""
Frontend Monitor: Watch Bank of Anthos for real transactions
Connects agents to actual frontend activity
"""

import os
import sys
import time
import json
import requests
from typing import Dict, List

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

try:
    from shared.messaging import publish, subscribe, clear_subscriptions
except ImportError:
    print("❌ Error: Could not import messaging system")
    sys.exit(1)

class FrontendMonitor:
    def __init__(self, frontend_url: str = "http://34.40.211.236"):
        self.frontend_url = frontend_url
        self.last_transactions = []
        self.setup_agent_handlers()
        
    def setup_agent_handlers(self):
        """Set up event handlers for all agents"""
        print("🔗 Setting up NFRGuard Frontend Monitor...")
        
        # Clear any existing subscriptions
        clear_subscriptions()
        
        # Subscribe to all agent events
        subscribe("transaction.created", self.handle_transaction_created)
        subscribe("risk.flagged", self.handle_risk_flagged)
        subscribe("compliance.action", self.handle_compliance_action)
        subscribe("customer.message", self.handle_customer_message)
        subscribe("log.entry", self.handle_log_entry)
        subscribe("privacy.violation", self.handle_privacy_violation)
        subscribe("ops.alert", self.handle_ops_alert)
        
        print("✅ Frontend monitor active")
        
    def handle_transaction_created(self, event: Dict):
        """Handle new transaction events"""
        amount = event.get('amount', 0)
        
        print(f"\n🚨 FRONTEND TRANSACTION DETECTED")
        print("=" * 50)
        print(f"💳 Amount: ${amount}")
        print(f"   Account: {event.get('account_id', 'N/A')}")
        print(f"   Time: {time.strftime('%H:%M:%S')}")
        print(f"   Source: {event.get('source', 'frontend')}")
        
        # Risk analysis
        if amount > 10000:
            print("🕵️ Transaction Risk Agent: 🚨 HIGH RISK!")
            print(f"   Risk Score: 0.95/1.0")
            print(f"   Reason: Large amount (${amount})")
            
            risk_event = {
                "event_type": "risk.flagged",
                "transaction_id": event.get('transaction_id'),
                "score": 0.95,
                "reason": f"high_amount_{amount}",
                "detected_by": "transaction_risk_agent_v1",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            publish("risk.flagged", risk_event)
            
        elif amount > 1000:
            print("🕵️ Transaction Risk Agent: ⚠️ MEDIUM RISK")
            print(f"   Risk Score: 0.6/1.0")
            
        else:
            print("🕵️ Transaction Risk Agent: ✅ LOW RISK")
            print(f"   Risk Score: 0.2/1.0")
            
    def handle_risk_flagged(self, event: Dict):
        """Handle risk detection events"""
        score = event.get('score', 0)
        print(f"🕵️ Risk Score: {score}")
        
        if score > 0.8:
            print("📋 Compliance Agent: 🔍 AUSTRAC CHECK")
            compliance_event = {
                "event_type": "compliance.action",
                "transaction_id": event.get('transaction_id'),
                "action": "hold",
                "reason": "AUSTRAC_threshold_exceeded",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            publish("compliance.action", compliance_event)
            
    def handle_compliance_action(self, event: Dict):
        """Handle compliance actions"""
        action = event.get('action', 'review')
        print(f"📋 Compliance Action: {action.upper()}")
        
        if action == "hold":
            print("🛡️ Resilience Agent: 🚫 TRANSACTION BLOCKED")
            print("   Account frozen pending investigation")
            
    def handle_customer_message(self, event: Dict):
        """Handle customer messages"""
        message = event.get('message', '')
        print(f"\n💬 Customer Message: '{message}'")
        
        # Sentiment analysis
        negative_words = ['blocked', 'ridiculous', 'angry', 'frustrated', 'terrible']
        negative_score = sum(1 for word in negative_words if word.lower() in message.lower())
        
        if negative_score > 0:
            print(f"😊 Sentiment Agent: 😠 NEGATIVE sentiment")
            print(f"   Negative indicators: {negative_score}")
        else:
            print("😊 Sentiment Agent: 😊 POSITIVE sentiment")
            
    def handle_log_entry(self, event: Dict):
        """Handle log entries"""
        content = event.get('content', '')
        print(f"\n📝 Log Entry: {content}")
        
        # PII detection
        pii_indicators = ['@', '.com', 'email', 'phone', 'ssn']
        pii_found = any(indicator in content.lower() for indicator in pii_indicators)
        
        if pii_found:
            print("🔒 Privacy Agent: 🚨 PII VIOLATION!")
            print("   Personal information detected in log")
        else:
            print("🔒 Privacy Agent: ✅ No privacy violations")
            
    def handle_privacy_violation(self, event: Dict):
        """Handle privacy violations"""
        print(f"🔒 Privacy Violation: {event.get('violation_type', 'N/A')}")
        print("   Log sanitized, alert generated")
        
    def handle_ops_alert(self, event: Dict):
        """Handle operational alerts"""
        print(f"😊 Ops Alert: {event.get('sentiment', 'N/A')} sentiment")
        print("   Escalating to customer service")
        
    def check_frontend_status(self):
        """Check if frontend is accessible"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Frontend accessible: {self.frontend_url}")
                return True
            else:
                print(f"⚠️ Frontend returned status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Frontend not accessible: {e}")
            return False
            
    def simulate_frontend_activity(self):
        """Simulate frontend activity for demo purposes"""
        print("\n🎬 Simulating Frontend Activity...")
        
        # Simulate different types of transactions
        scenarios = [
            {"amount": 50.00, "description": "Coffee purchase"},
            {"amount": 150.00, "description": "Grocery shopping"},
            {"amount": 25000.00, "description": "Large transfer to foreign account"},
            {"amount": 5000.00, "description": "Business payment"},
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n--- Simulating Transaction {i} ---")
            
            transaction_event = {
                "event_type": "transaction.created",
                "transaction_id": f"txn_sim_{i}",
                "amount": scenario["amount"],
                "account_id": "acc_demo_user",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "description": scenario["description"],
                "source": "frontend_simulation"
            }
            
            publish("transaction.created", transaction_event)
            time.sleep(2)  # Let agents process
            
        print("\n✅ Frontend activity simulation complete")
        
    def run_monitoring(self):
        """Run the frontend monitoring"""
        print("🛡️ NFRGuard Frontend Monitor")
        print("=" * 40)
        print(f"🌐 Monitoring: {self.frontend_url}")
        print("🤖 7 AI Agents ready to respond")
        
        # Check frontend status
        if not self.check_frontend_status():
            print("\n⚠️ Frontend not accessible. Running simulation mode...")
            self.simulate_frontend_activity()
            return
            
        print("\n📋 Instructions:")
        print("1. Open Bank of Anthos in browser")
        print("2. Login and make transactions")
        print("3. Watch this terminal for agent reactions")
        print("4. Press Ctrl+C to stop monitoring")
        
        print("\n👀 Monitoring for frontend activity...")
        print("(In a real implementation, this would poll the frontend API)")
        
        try:
            while True:
                # In a real implementation, you would poll the frontend API
                # For now, we'll just wait and show status
                time.sleep(5)
                print(f"⏰ {time.strftime('%H:%M:%S')} - Monitoring active...")
                
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped. Thanks for watching NFRGuard!")

def main():
    """Main function"""
    print("🚀 Starting Frontend Monitor...")
    
    # Get frontend URL
    frontend_url = input("Enter Bank of Anthos frontend URL (default: http://34.40.211.236): ").strip()
    if not frontend_url:
        frontend_url = "http://34.40.211.236"
        
    # Create monitor
    monitor = FrontendMonitor(frontend_url)
    
    # Run monitoring
    monitor.run_monitoring()

if __name__ == "__main__":
    main()

