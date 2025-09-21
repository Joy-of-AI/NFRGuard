#!/usr/bin/env python3
"""
Frontend Integration for NFRGuard Agents
Connects agents to Bank of Anthos frontend for real-time demo
"""

import os
import sys
import time
import json
import requests
from typing import Dict, List, Optional

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))
from shared.messaging import publish, subscribe

class FrontendAgentIntegration:
    def __init__(self, frontend_url: str = "http://34.40.211.236"):
        self.frontend_url = frontend_url
        self.agent_responses = []
        
    def setup_agent_subscriptions(self):
        """Set up agent event subscriptions for demo"""
        print("🔗 Setting up agent subscriptions...")
        
        # Subscribe to all agent events
        subscribe("risk.flagged", self.handle_risk_event)
        subscribe("compliance.action", self.handle_compliance_event)
        subscribe("ops.alert", self.handle_sentiment_event)
        subscribe("privacy.violation", self.handle_privacy_event)
        
        print("✅ Agent subscriptions active")
        
    def handle_risk_event(self, event: Dict):
        """Handle risk detection events"""
        print(f"🕵️ Risk Agent: {event}")
        self.agent_responses.append({
            "agent": "Transaction Risk Agent",
            "event": "risk.flagged",
            "message": f"Suspicious transaction detected! Risk score: {event.get('score', 'N/A')}",
            "timestamp": time.time()
        })
        
    def handle_compliance_event(self, event: Dict):
        """Handle compliance events"""
        print(f"📋 Compliance Agent: {event}")
        self.agent_responses.append({
            "agent": "Compliance Agent", 
            "event": "compliance.action",
            "message": f"Compliance check: {event.get('action', 'review required')}",
            "timestamp": time.time()
        })
        
    def handle_sentiment_event(self, event: Dict):
        """Handle sentiment analysis events"""
        print(f"😊 Sentiment Agent: {event}")
        self.agent_responses.append({
            "agent": "Customer Sentiment Agent",
            "event": "ops.alert", 
            "message": f"Customer sentiment: {event.get('sentiment', 'analyzing')}",
            "timestamp": time.time()
        })
        
    def handle_privacy_event(self, event: Dict):
        """Handle privacy violation events"""
        print(f"🔒 Privacy Agent: {event}")
        self.agent_responses.append({
            "agent": "Data Privacy Agent",
            "event": "privacy.violation",
            "message": f"Privacy violation detected: {event.get('violation_type', 'PII found')}",
            "timestamp": time.time()
        })
        
    def simulate_transaction(self, amount: float, description: str = "Demo transaction"):
        """Simulate a transaction through the frontend"""
        print(f"\n💳 Simulating transaction: ${amount} - {description}")
        
        # Create transaction event
        transaction_event = {
            "event_type": "transaction.created",
            "transaction_id": f"txn_demo_{int(time.time())}",
            "amount": amount,
            "account_id": "acc_demo_12345",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "description": description,
            "customer_profile": "demo_user"
        }
        
        # Publish transaction event
        publish("transaction.created", transaction_event)
        
        # Wait for agent responses
        print("⏳ Waiting for agent analysis...")
        time.sleep(2)
        
        # Show agent responses
        self.show_agent_responses()
        
        return transaction_event
        
    def simulate_customer_message(self, message: str):
        """Simulate a customer message for sentiment analysis"""
        print(f"\n💬 Simulating customer message: '{message}'")
        
        # Create customer message event
        message_event = {
            "event_type": "customer.message",
            "message_id": f"msg_demo_{int(time.time())}",
            "customer_id": "acc_demo_12345",
            "message": message,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "channel": "web_chat"
        }
        
        # Publish message event
        publish("customer.message", message_event)
        
        # Wait for sentiment analysis
        print("⏳ Analyzing customer sentiment...")
        time.sleep(1)
        
        # Show agent responses
        self.show_agent_responses()
        
        return message_event
        
    def simulate_privacy_violation(self, log_content: str):
        """Simulate a privacy violation in logs"""
        print(f"\n🔍 Simulating privacy violation in log: '{log_content}'")
        
        # Create log entry event
        log_event = {
            "event_type": "log.entry",
            "log_id": f"log_demo_{int(time.time())}",
            "content": log_content,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "log_level": "INFO",
            "service": "demo_service"
        }
        
        # Publish log event
        publish("log.entry", log_event)
        
        # Wait for privacy analysis
        print("⏳ Checking for privacy violations...")
        time.sleep(1)
        
        # Show agent responses
        self.show_agent_responses()
        
        return log_event
        
    def show_agent_responses(self):
        """Show recent agent responses"""
        if not self.agent_responses:
            print("📭 No agent responses yet")
            return
            
        print("\n🤖 Recent Agent Responses:")
        print("-" * 50)
        
        # Show last 5 responses
        recent_responses = self.agent_responses[-5:]
        for response in recent_responses:
            timestamp = time.strftime("%H:%M:%S", time.localtime(response['timestamp']))
            print(f"[{timestamp}] {response['agent']}: {response['message']}")
            
    def run_interactive_demo(self):
        """Run an interactive demo"""
        print("🎬 NFRGuard Interactive Demo")
        print("=" * 40)
        print("This demo shows how AI agents protect Bank of Anthos")
        print("Frontend URL:", self.frontend_url)
        
        # Setup subscriptions
        self.setup_agent_subscriptions()
        
        while True:
            print("\n🎯 Demo Options:")
            print("1. Normal transaction ($50)")
            print("2. Suspicious transaction ($25,000 at 2 AM)")
            print("3. Customer complaint message")
            print("4. Privacy violation in logs")
            print("5. Show agent responses")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                self.simulate_transaction(50.00, "Normal purchase")
            elif choice == "2":
                self.simulate_transaction(25000.00, "Suspicious large transfer")
            elif choice == "3":
                message = input("Enter customer message: ").strip()
                if message:
                    self.simulate_customer_message(message)
            elif choice == "4":
                log_content = input("Enter log content: ").strip()
                if log_content:
                    self.simulate_privacy_violation(log_content)
            elif choice == "5":
                self.show_agent_responses()
            elif choice == "6":
                print("👋 Demo ended. Thanks for watching NFRGuard in action!")
                break
            else:
                print("❌ Invalid option. Please try again.")
                
    def run_automated_demo(self):
        """Run an automated demo sequence"""
        print("🎬 NFRGuard Automated Demo")
        print("=" * 40)
        
        # Setup subscriptions
        self.setup_agent_subscriptions()
        
        # Demo sequence
        scenarios = [
            ("Normal Transaction", lambda: self.simulate_transaction(50.00, "Coffee purchase")),
            ("Suspicious Transaction", lambda: self.simulate_transaction(25000.00, "Large transfer to foreign account")),
            ("Customer Complaint", lambda: self.simulate_customer_message("Why was my transaction blocked? This is ridiculous!")),
            ("Privacy Violation", lambda: self.simulate_privacy_violation("Transaction processed for customer@email.com"))
        ]
        
        for i, (name, scenario_func) in enumerate(scenarios, 1):
            print(f"\n--- Scenario {i}: {name} ---")
            scenario_func()
            
            if i < len(scenarios):
                print("\n⏳ Waiting 3 seconds before next scenario...")
                time.sleep(3)
                
        print("\n🎉 Automated demo completed!")
        print("\n📊 Final Agent Responses:")
        self.show_agent_responses()

def main():
    """Main function"""
    print("🛡️ NFRGuard Frontend Integration")
    print("=" * 40)
    
    # Get frontend URL
    frontend_url = input("Enter Bank of Anthos frontend URL (default: http://34.40.211.236): ").strip()
    if not frontend_url:
        frontend_url = "http://34.40.211.236"
        
    # Create integration
    integration = FrontendAgentIntegration(frontend_url)
    
    # Choose demo mode
    print("\n🎯 Demo Mode:")
    print("1. Interactive demo (you control the scenarios)")
    print("2. Automated demo (runs all scenarios automatically)")
    
    mode = input("Select mode (1-2): ").strip()
    
    if mode == "1":
        integration.run_interactive_demo()
    elif mode == "2":
        integration.run_automated_demo()
    else:
        print("❌ Invalid mode. Running interactive demo...")
        integration.run_interactive_demo()

if __name__ == "__main__":
    main()

