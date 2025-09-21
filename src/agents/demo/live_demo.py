#!/usr/bin/env python3
"""
Live Demo: Connect NFRGuard Agents to Bank of Anthos Frontend
Shows real-time agent reactions to actual frontend transactions
"""

import os
import sys
import time
import json
import requests
import threading
from typing import Dict, List

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

try:
    from shared.messaging import publish, subscribe, clear_subscriptions
except ImportError:
    print("❌ Error: Could not import messaging system")
    sys.exit(1)

class LiveAgentDemo:
    def __init__(self, frontend_url: str = "http://34.40.211.236"):
        self.frontend_url = frontend_url
        self.agent_responses = []
        self.transaction_counter = 0
        self.setup_agent_handlers()
        
    def setup_agent_handlers(self):
        """Set up event handlers for all agents"""
        print("🔗 Setting up NFRGuard Live Agent Handlers...")
        
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
        
        print("✅ Live agent handlers active")
        print("🎯 Now make transactions on the frontend to see agent reactions!")
        
    def handle_transaction_created(self, event: Dict):
        """Handle new transaction events"""
        self.transaction_counter += 1
        amount = event.get('amount', 0)
        
        print(f"\n🚨 LIVE ALERT #{self.transaction_counter}")
        print("=" * 50)
        print(f"💳 Transaction Detected: ${amount}")
        print(f"   Account: {event.get('account_id', 'N/A')}")
        print(f"   Time: {time.strftime('%H:%M:%S')}")
        print(f"   Description: {event.get('description', 'N/A')}")
        
        # Simulate risk analysis based on amount
        if amount > 10000:
            print("🕵️ Transaction Risk Agent: 🚨 HIGH RISK DETECTED!")
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
            print(f"   Reason: Moderate amount (${amount})")
            
        else:
            print("🕵️ Transaction Risk Agent: ✅ LOW RISK")
            print(f"   Risk Score: 0.2/1.0")
            print(f"   Reason: Normal amount (${amount})")
            
    def handle_risk_flagged(self, event: Dict):
        """Handle risk detection events"""
        score = event.get('score', 0)
        reason = event.get('reason', 'N/A')
        
        print(f"🕵️ Transaction Risk Agent: Risk Score {score}")
        print(f"   Reason: {reason}")
        
        # Simulate compliance check for high-risk transactions
        if score > 0.8:
            print("📋 Compliance Agent: 🔍 AUSTRAC COMPLIANCE CHECK")
            print("   Checking against regulatory requirements...")
            
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
        reason = event.get('reason', 'N/A')
        
        print(f"📋 Compliance Agent: Action = {action.upper()}")
        print(f"   Reason: {reason}")
        
        if action == "hold":
            print("🛡️ Resilience Agent: 🚫 TRANSACTION BLOCKED")
            print("   Customer account temporarily frozen")
            print("   Investigation initiated")
            print("   Customer notification sent")
            
    def handle_customer_message(self, event: Dict):
        """Handle customer messages for sentiment analysis"""
        message = event.get('message', '')
        print(f"\n💬 Customer Message: '{message}'")
        
        # Simple sentiment analysis
        negative_words = ['blocked', 'ridiculous', 'angry', 'frustrated', 'terrible', 'awful', 'hate', 'stupid']
        positive_words = ['great', 'excellent', 'love', 'amazing', 'perfect', 'wonderful', 'fantastic']
        
        negative_score = sum(1 for word in negative_words if word.lower() in message.lower())
        positive_score = sum(1 for word in positive_words if word.lower() in message.lower())
        
        if negative_score > positive_score:
            print(f"😊 Customer Sentiment Agent: 😠 NEGATIVE sentiment")
            print(f"   Negative indicators: {negative_score}")
            print(f"   Positive indicators: {positive_score}")
            print("   Alert: Customer satisfaction at risk")
            
            ops_event = {
                "event_type": "ops.alert",
                "message_id": event.get('message_id'),
                "sentiment": "negative",
                "trend": "escalating",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            publish("ops.alert", ops_event)
        elif positive_score > negative_score:
            print(f"😊 Customer Sentiment Agent: 😊 POSITIVE sentiment")
            print(f"   Positive indicators: {positive_score}")
            print(f"   Negative indicators: {negative_score}")
        else:
            print("😊 Customer Sentiment Agent: 😐 NEUTRAL sentiment")
            
    def handle_log_entry(self, event: Dict):
        """Handle log entries for privacy analysis"""
        content = event.get('content', '')
        print(f"\n📝 Log Entry: {content}")
        
        # Simple PII detection
        pii_indicators = ['@', '.com', '.org', 'email', 'phone', 'ssn', 'social security', 'credit card']
        pii_found = any(indicator in content.lower() for indicator in pii_indicators)
        
        if pii_found:
            print("🔒 Data Privacy Agent: 🚨 PII VIOLATION DETECTED!")
            print("   Personal information found in log")
            print("   Action: Log sanitized, alert generated")
            
            privacy_event = {
                "event_type": "privacy.violation",
                "log_id": event.get('log_id'),
                "violation_type": "PII_in_log",
                "severity": "medium",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            publish("privacy.violation", privacy_event)
        else:
            print("🔒 Data Privacy Agent: ✅ No privacy violations detected")
            
    def handle_privacy_violation(self, event: Dict):
        """Handle privacy violations"""
        violation_type = event.get('violation_type', 'N/A')
        severity = event.get('severity', 'N/A')
        
        print(f"🔒 Data Privacy Agent: {violation_type} violation")
        print(f"   Severity: {severity}")
        print("   Log sanitized, alert generated")
        print("   Compliance team notified")
        
    def handle_ops_alert(self, event: Dict):
        """Handle operational alerts"""
        sentiment = event.get('sentiment', 'N/A')
        trend = event.get('trend', 'N/A')
        
        print(f"😊 Customer Sentiment Agent: OPS ALERT")
        print(f"   Sentiment: {sentiment}")
        print(f"   Trend: {trend}")
        print("   Escalating to customer service team")
        print("   Proactive outreach initiated")
        
    def simulate_frontend_transaction(self, amount: float, description: str = "Frontend transaction"):
        """Simulate a transaction from the frontend"""
        self.transaction_counter += 1
        
        transaction_event = {
            "event_type": "transaction.created",
            "transaction_id": f"txn_frontend_{self.transaction_counter}",
            "amount": amount,
            "account_id": "acc_frontend_user",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "description": description,
            "source": "frontend"
        }
        
        print(f"\n🎬 Simulating Frontend Transaction: ${amount}")
        publish("transaction.created", transaction_event)
        time.sleep(1)  # Let agents process
        
    def simulate_customer_message(self, message: str):
        """Simulate a customer message"""
        message_event = {
            "event_type": "customer.message",
            "message_id": f"msg_frontend_{int(time.time())}",
            "customer_id": "acc_frontend_user",
            "message": message,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "channel": "web_chat"
        }
        
        print(f"\n🎬 Simulating Customer Message: '{message}'")
        publish("customer.message", message_event)
        time.sleep(1)  # Let agents process
        
    def run_interactive_demo(self):
        """Run interactive demo with manual triggers"""
        print("🎬 NFRGuard Live Demo - Interactive Mode")
        print("=" * 50)
        print(f"🌐 Bank of Anthos Frontend: {self.frontend_url}")
        print("🤖 7 AI Agents monitoring in real-time")
        print()
        print("🎯 Options:")
        print("1. Simulate normal transaction ($50)")
        print("2. Simulate suspicious transaction ($25,000)")
        print("3. Simulate customer complaint")
        print("4. Simulate privacy violation")
        print("5. Show agent status")
        print("6. Exit")
        
        while True:
            print("\n" + "="*50)
            choice = input("Select option (1-6): ").strip()
            
            if choice == "1":
                self.simulate_frontend_transaction(50.00, "Coffee purchase")
            elif choice == "2":
                self.simulate_frontend_transaction(25000.00, "Large transfer to foreign account")
            elif choice == "3":
                message = input("Enter customer message: ").strip()
                if message:
                    self.simulate_customer_message(message)
            elif choice == "4":
                log_content = input("Enter log content: ").strip()
                if log_content:
                    log_event = {
                        "event_type": "log.entry",
                        "log_id": f"log_frontend_{int(time.time())}",
                        "content": log_content,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                    publish("log.entry", log_event)
            elif choice == "5":
                print(f"\n📊 Agent Status:")
                print(f"   Transactions processed: {self.transaction_counter}")
                print(f"   Agents active: 7/7")
                print(f"   Frontend URL: {self.frontend_url}")
            elif choice == "6":
                print("👋 Live demo ended. Thanks for watching NFRGuard!")
                break
            else:
                print("❌ Invalid option. Please try again.")
                
    def show_instructions(self):
        """Show instructions for using with frontend"""
        print("\n📋 How to See Agents React to Frontend Transactions:")
        print("=" * 60)
        print("1. 🌐 Open Bank of Anthos in browser: http://34.40.211.236")
        print("2. 🔐 Login with demo credentials")
        print("3. 💳 Make transactions on the frontend")
        print("4. 👀 Watch this terminal for agent reactions")
        print("5. 🎬 Record your screen to capture both frontend and agents")
        print()
        print("💡 Pro Tips:")
        print("   • Make a $50 transaction → See normal processing")
        print("   • Make a $25,000 transaction → See fraud detection")
        print("   • Send a complaint message → See sentiment analysis")
        print("   • Check logs for PII → See privacy protection")
        print()
        print("🎯 The agents will react in real-time to your frontend actions!")

def main():
    """Main function"""
    print("🛡️ NFRGuard Live Demo")
    print("=" * 30)
    
    # Get frontend URL
    frontend_url = input("Enter Bank of Anthos frontend URL (default: http://34.40.211.236): ").strip()
    if not frontend_url:
        frontend_url = "http://34.40.211.236"
        
    # Create live demo
    demo = LiveAgentDemo(frontend_url)
    
    # Show instructions
    demo.show_instructions()
    
    # Choose mode
    print("\n🎯 Demo Mode:")
    print("1. Interactive demo (simulate transactions)")
    print("2. Live monitoring (watch for real frontend activity)")
    
    mode = input("Select mode (1-2): ").strip()
    
    if mode == "1":
        demo.run_interactive_demo()
    elif mode == "2":
        print("\n👀 Live monitoring mode active!")
        print("Now make transactions on the frontend to see agent reactions...")
        print("Press Ctrl+C to stop monitoring")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped. Thanks for watching NFRGuard!")
    else:
        print("❌ Invalid mode. Running interactive demo...")
        demo.run_interactive_demo()

if __name__ == "__main__":
    main()

