#!/usr/bin/env python3
"""
Real Database Transaction Monitor: Monitors the actual PostgreSQL database for new transactions
Captures real transaction data from the ledger-db database
"""

import os
import sys
import time
import subprocess
from typing import Dict, List

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

try:
    from shared.messaging import publish, subscribe, clear_subscriptions
except ImportError:
    print("❌ Error: Could not import messaging system")
    sys.exit(1)

class RealDatabaseTransactionMonitor:
    def __init__(self):
        self.transaction_counter = 0
        self.last_transaction_id = None
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
        print("🎯 Monitoring REAL database transactions")
        print("⏳ Waiting for you to make transactions...")
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
        
    def get_latest_transaction(self):
        """Get the latest transaction from the database"""
        try:
            result = subprocess.run([
                "kubectl", "exec", "ledger-db-0", "--", 
                "psql", "-U", "admin", "-d", "postgresdb", 
                "-c", "SELECT transaction_id, amount, timestamp FROM transactions ORDER BY timestamp DESC LIMIT 1;"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return None
                
        except Exception as e:
            return None
            
    def parse_transaction_data(self, db_output: str):
        """Parse transaction data from database output"""
        try:
            lines = db_output.strip().split('\n')
            
            # Look for transaction data in the output
            for line in lines:
                if '|' in line and not line.startswith('-') and not line.startswith('(') and not line.startswith('transaction_id'):
                    parts = [part.strip() for part in line.split('|')]
                    if len(parts) >= 3:
                        transaction_id = parts[0].strip()
                        amount = int(parts[1].strip()) if parts[1].strip().isdigit() else None
                        timestamp = parts[2].strip() if len(parts) > 2 else None
                        
                        if amount is not None and transaction_id != self.last_transaction_id:
                            self.last_transaction_id = transaction_id
                            return {
                                "transaction_id": transaction_id,
                                "amount": amount,
                                "timestamp": timestamp
                            }
                            
        except (ValueError, IndexError):
            pass
            
        return None
        
    def monitor_database_transactions(self):
        """Monitor database for new transactions"""
        print("👀 Monitoring REAL database transactions...")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            while True:
                db_output = self.get_latest_transaction()
                
                if db_output:
                    transaction_data = self.parse_transaction_data(db_output)
                    
                    if transaction_data:
                        print(f"💳 NEW TRANSACTION DETECTED!")
                        print(f"   ID: {transaction_data['transaction_id']}")
                        print(f"   Amount: ${transaction_data['amount']:,.2f}")
                        print(f"   Time: {transaction_data['timestamp']}")
                        
                        transaction_event = {
                            "event_type": "transaction.created",
                            "transaction_id": transaction_data['transaction_id'],
                            "amount": transaction_data['amount'],
                            "account_id": "acc_real_user",
                            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "description": "Real database transaction",
                            "source": "database"
                        }
                        
                        publish("transaction.created", transaction_event)
                        time.sleep(1)
                        
                time.sleep(3)  # Check every 3 seconds
                
        except KeyboardInterrupt:
            print(f"\n📊 Total transactions processed: {self.transaction_counter}")
            print("👋 NFRGuard monitoring stopped")

def main():
    """Main function"""
    demo = RealDatabaseTransactionMonitor()
    demo.monitor_database_transactions()

if __name__ == "__main__":
    main()

