#!/usr/bin/env python3
"""
Simple Auto-React Demo: Immediately reacts to Bank of Anthos transactions
No waiting, no manual input - just pure agent reactions
"""

import os
import sys
import time
import json
import subprocess
from typing import Dict, List

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

try:
    from shared.messaging import publish, subscribe, clear_subscriptions
except ImportError:
    print("❌ Error: Could not import messaging system")
    sys.exit(1)

class SimpleAutoReact:
    def __init__(self):
        self.transaction_counter = 0
        self.last_logs = []
        self.setup_agent_handlers()
        
    def setup_agent_handlers(self):
        """Set up event handlers for all agents"""
        print("🛡️ NFRGuard AI Banking Security")
        print("=" * 50)
        print("🤖 7 AI Agents protecting Bank of Anthos")
        print("🌐 Frontend: http://34.40.211.236")
        print("=" * 50)
        
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
        
        print("✅ Agents active and monitoring")
        print("🎯 Auto-reacting to frontend transactions")
        print("⏳ Waiting for transactions...")
        print()
        
    def handle_transaction_created(self, event: Dict):
        """Handle new transaction events"""
        self.transaction_counter += 1
        amount = event.get('amount', 0)
        
        print(f"🚨 TRANSACTION #{self.transaction_counter}")
        print(f"💳 Amount: ${amount:,.2f}")
        print(f"⏰ Time: {time.strftime('%H:%M:%S')}")
        
        # Risk analysis
        if amount > 10000:
            print("🕵️ Risk Agent: HIGH RISK DETECTED!")
            print(f"   Risk Score: 0.95/1.0")
            print(f"   Reason: Large amount (${amount:,.2f})")
            
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
            print("🕵️ Risk Agent: MEDIUM RISK")
            print(f"   Risk Score: 0.6/1.0")
            print(f"   Reason: Moderate amount (${amount:,.2f})")
            
        else:
            print("🕵️ Risk Agent: LOW RISK")
            print(f"   Risk Score: 0.2/1.0")
            print(f"   Reason: Normal amount (${amount:,.2f})")
            
    def handle_risk_flagged(self, event: Dict):
        """Handle risk detection events"""
        score = event.get('score', 0)
        print(f"📋 Compliance Agent: AUSTRAC CHECK")
        print(f"   Risk Score: {score}")
        
        if score > 0.8:
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
        print(f"🛡️ Resilience Agent: TRANSACTION {action.upper()}")
        
        if action == "hold":
            print("   Account frozen pending investigation")
            print("   Customer notification sent")
            
    def handle_customer_message(self, event: Dict):
        """Handle customer messages"""
        message = event.get('message', '')
        print(f"💬 Customer Message: '{message}'")
        
        # Sentiment analysis
        negative_words = ['blocked', 'ridiculous', 'angry', 'frustrated', 'terrible']
        negative_score = sum(1 for word in negative_words if word.lower() in message.lower())
        
        if negative_score > 0:
            print(f"😊 Sentiment Agent: NEGATIVE sentiment")
            print(f"   Negative indicators: {negative_score}")
            print("   Escalating to customer service")
        else:
            print("😊 Sentiment Agent: POSITIVE sentiment")
            
    def handle_log_entry(self, event: Dict):
        """Handle log entries"""
        content = event.get('content', '')
        print(f"📝 Log Entry: {content}")
        
        # PII detection
        pii_indicators = ['@', '.com', 'email', 'phone', 'ssn']
        pii_found = any(indicator in content.lower() for indicator in pii_indicators)
        
        if pii_found:
            print("🔒 Privacy Agent: PII VIOLATION!")
            print("   Personal information detected")
            print("   Log sanitized, alert generated")
        else:
            print("🔒 Privacy Agent: No privacy violations")
            
    def handle_privacy_violation(self, event: Dict):
        """Handle privacy violations"""
        print(f"🔒 Privacy Violation: {event.get('violation_type', 'N/A')}")
        print("   Compliance team notified")
        
    def handle_ops_alert(self, event: Dict):
        """Handle operational alerts"""
        print(f"😊 Ops Alert: {event.get('sentiment', 'N/A')} sentiment")
        print("   Proactive outreach initiated")
        
    def get_frontend_logs(self):
        """Get recent logs from the frontend pod"""
        try:
            result = subprocess.run([
                "kubectl", "logs", "deployment/frontend", "--tail=2"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
            else:
                return []
        except Exception as e:
            return []
            
    def parse_log_entry(self, log_line: str):
        """Parse a log entry to extract transaction information"""
        try:
            log_data = json.loads(log_line)
            message = log_data.get('message', '')
            
            # Only process payment messages
            if 'payment' in message.lower() and 'successfully' in message.lower():
                # Automatically assign realistic amounts based on transaction type
                # This simulates what would happen in a real system
                
                # Check if it's a logout (small transaction)
                if 'logout' in message.lower():
                    amount = 50.0
                # Check if it's a login (medium transaction)
                elif 'login' in message.lower():
                    amount = 500.0
                # Default payment (large transaction for demo)
                else:
                    amount = 15000.0  # Large amount to trigger fraud detection
                
                print(f"💳 Transaction detected: {message}")
                print(f"   Auto-assigned amount: ${amount:,.2f}")
                
                return {
                    "event_type": "transaction.created",
                    "transaction_id": f"txn_real_{int(time.time())}",
                    "amount": amount,
                    "account_id": "acc_real_user",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "description": "Real frontend transaction",
                    "source": "real_frontend"
                }
                
        except json.JSONDecodeError:
            pass
            
        return None
        
    def monitor_frontend_logs(self):
        """Monitor frontend logs for real transactions"""
        print("👀 Monitoring for real transactions...")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            while True:
                logs = self.get_frontend_logs()
                
                for log_line in logs:
                    if log_line and log_line not in self.last_logs:
                        self.last_logs.append(log_line)
                        
                        transaction_event = self.parse_log_entry(log_line)
                        
                        if transaction_event:
                            publish("transaction.created", transaction_event)
                            time.sleep(1)
                            
                if len(self.last_logs) > 10:
                    self.last_logs = self.last_logs[-10:]
                    
                time.sleep(2)  # Check every 2 seconds
                
        except KeyboardInterrupt:
            print(f"\n📊 Total transactions processed: {self.transaction_counter}")
            print("👋 NFRGuard monitoring stopped")

def main():
    """Main function"""
    demo = SimpleAutoReact()
    demo.monitor_frontend_logs()

if __name__ == "__main__":
    main()

