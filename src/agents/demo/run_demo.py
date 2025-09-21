#!/usr/bin/env python3
"""
NFRGuard Demo Runner
Run this to see agents working with Bank of Anthos frontend
"""

import os
import sys
import time
import json
from typing import Dict

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

try:
    from shared.messaging import publish, subscribe, clear_subscriptions
except ImportError:
    print("❌ Error: Could not import messaging system")
    print("Make sure you're running from the agents directory")
    sys.exit(1)

class NFRGuardDemo:
    def __init__(self):
        self.frontend_url = "http://34.40.211.236"
        self.agent_responses = []
        self.setup_agent_handlers()
        
    def setup_agent_handlers(self):
        """Set up event handlers for all agents"""
        print("🔗 Setting up NFRGuard agent handlers...")
        
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
        
        print("✅ All agent handlers active")
        
    def handle_transaction_created(self, event: Dict):
        """Handle new transaction events"""
        print(f"\n💳 Transaction Created: ${event.get('amount', 'N/A')}")
        print(f"   Account: {event.get('account_id', 'N/A')}")
        print(f"   Time: {event.get('timestamp', 'N/A')}")
        
        # Simulate risk analysis
        amount = event.get('amount', 0)
        if amount > 10000:
            print("🕵️ Transaction Risk Agent: HIGH RISK detected!")
            risk_event = {
                "event_type": "risk.flagged",
                "transaction_id": event.get('transaction_id'),
                "score": 0.95,
                "reason": "high_amount",
                "detected_by": "transaction_risk_agent_v1",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            publish("risk.flagged", risk_event)
            
    def handle_risk_flagged(self, event: Dict):
        """Handle risk detection events"""
        print(f"🕵️ Transaction Risk Agent: Risk Score {event.get('score', 'N/A')}")
        print(f"   Reason: {event.get('reason', 'N/A')}")
        
        # Simulate compliance check
        if event.get('score', 0) > 0.8:
            print("📋 Compliance Agent: AUSTRAC compliance check required")
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
        print(f"📋 Compliance Agent: Action = {action.upper()}")
        print(f"   Reason: {event.get('reason', 'N/A')}")
        
        if action == "hold":
            print("🛡️ Resilience Agent: Transaction BLOCKED")
            print("   Customer account temporarily frozen")
            print("   Investigation initiated")
            
    def handle_customer_message(self, event: Dict):
        """Handle customer messages for sentiment analysis"""
        message = event.get('message', '')
        print(f"\n💬 Customer Message: '{message}'")
        
        # Simple sentiment analysis
        negative_words = ['blocked', 'ridiculous', 'angry', 'frustrated', 'terrible', 'awful']
        sentiment_score = sum(1 for word in negative_words if word.lower() in message.lower())
        
        if sentiment_score > 0:
            print(f"😊 Customer Sentiment Agent: NEGATIVE sentiment detected")
            print(f"   Score: {sentiment_score}/6 negative indicators")
            ops_event = {
                "event_type": "ops.alert",
                "message_id": event.get('message_id'),
                "sentiment": "negative",
                "trend": "escalating",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            publish("ops.alert", ops_event)
        else:
            print("😊 Customer Sentiment Agent: POSITIVE sentiment")
            
    def handle_log_entry(self, event: Dict):
        """Handle log entries for privacy analysis"""
        content = event.get('content', '')
        print(f"\n📝 Log Entry: {content}")
        
        # Simple PII detection
        pii_indicators = ['@', '.com', '.org', 'email', 'phone', 'ssn', 'social security']
        pii_found = any(indicator in content.lower() for indicator in pii_indicators)
        
        if pii_found:
            print("🔒 Data Privacy Agent: PII VIOLATION detected!")
            print("   Personal information found in log")
            privacy_event = {
                "event_type": "privacy.violation",
                "log_id": event.get('log_id'),
                "violation_type": "PII_in_log",
                "severity": "medium",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            publish("privacy.violation", privacy_event)
        else:
            print("🔒 Data Privacy Agent: No privacy violations detected")
            
    def handle_privacy_violation(self, event: Dict):
        """Handle privacy violations"""
        print(f"🔒 Data Privacy Agent: {event.get('violation_type', 'N/A')} violation")
        print(f"   Severity: {event.get('severity', 'N/A')}")
        print("   Log sanitized, alert generated")
        
    def handle_ops_alert(self, event: Dict):
        """Handle operational alerts"""
        print(f"😊 Customer Sentiment Agent: OPS ALERT")
        print(f"   Sentiment: {event.get('sentiment', 'N/A')}")
        print(f"   Trend: {event.get('trend', 'N/A')}")
        print("   Escalating to customer service team")
        
    def run_demo_scenario(self, scenario_name: str, event: Dict):
        """Run a demo scenario"""
        print(f"\n🎬 === {scenario_name} ===")
        print("=" * 50)
        
        # Publish the initial event
        event_type = event.get('event_type', 'unknown')
        publish(event_type, event)
        
        # Wait for agent responses
        print("\n⏳ Processing...")
        time.sleep(2)
        
        print(f"\n✅ {scenario_name} completed")
        
    def run_full_demo(self):
        """Run the complete demo sequence"""
        print("🛡️ NFRGuard AI Banking Security Demo")
        print("=" * 50)
        print(f"🌐 Bank of Anthos Frontend: {self.frontend_url}")
        print("🤖 7 AI Agents protecting your bank 24/7")
        print()
        
        # Demo scenarios
        scenarios = [
            {
                "name": "Normal Transaction",
                "event": {
                    "event_type": "transaction.created",
                    "transaction_id": "txn_normal_001",
                    "amount": 50.00,
                    "account_id": "acc_12345",
                    "timestamp": "2025-01-14T14:30:00Z",
                    "description": "Coffee purchase"
                }
            },
            {
                "name": "Suspicious Transaction (Fraud Detection)",
                "event": {
                    "event_type": "transaction.created",
                    "transaction_id": "txn_suspicious_001",
                    "amount": 25000.00,
                    "account_id": "acc_12345",
                    "timestamp": "2025-01-14T02:00:00Z",  # 2 AM
                    "description": "Large transfer to foreign account"
                }
            },
            {
                "name": "Customer Complaint (Sentiment Analysis)",
                "event": {
                    "event_type": "customer.message",
                    "message_id": "msg_001",
                    "customer_id": "acc_12345",
                    "message": "Why was my transaction blocked? This is ridiculous! I need this money for my business!",
                    "timestamp": "2025-01-14T02:05:00Z"
                }
            },
            {
                "name": "Privacy Violation (Data Protection)",
                "event": {
                    "event_type": "log.entry",
                    "log_id": "log_001",
                    "content": "Transaction txn_001 processed for customer john.doe@email.com with amount $25,000",
                    "timestamp": "2025-01-14T02:10:00Z"
                }
            }
        ]
        
        # Run each scenario
        for i, scenario in enumerate(scenarios, 1):
            self.run_demo_scenario(scenario["name"], scenario["event"])
            
            if i < len(scenarios):
                print("\n" + "="*50)
                input("Press Enter for next scenario...")
                
        # Demo summary
        print("\n🎉 Demo Complete!")
        print("=" * 50)
        print("📊 What you just saw:")
        print("✅ Real-time fraud detection")
        print("✅ Automated compliance checking")
        print("✅ Customer sentiment analysis")
        print("✅ Privacy violation detection")
        print("✅ Multi-agent coordination")
        print()
        print("🛡️ NFRGuard: Your AI security team never sleeps!")
        print(f"🌐 Try the frontend: {self.frontend_url}")

def main():
    """Main function"""
    print("🚀 Starting NFRGuard Demo...")
    
    try:
        demo = NFRGuardDemo()
        demo.run_full_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thanks for watching!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("Make sure you're in the agents directory and all files are present")

if __name__ == "__main__":
    main()

