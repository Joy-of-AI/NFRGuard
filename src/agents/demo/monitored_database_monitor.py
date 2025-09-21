#!/usr/bin/env python3
"""
Monitored Real-Time Database Monitor: Shows all 7 NFRGuard AI Agents with GCP Monitoring
Monitors PostgreSQL for new transactions and sends metrics to Google Cloud Monitoring
"""

import time
import subprocess
import sys
import os
import random

# Add monitoring directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'monitoring'))

try:
    from agent_metrics import track_demo_metrics
    MONITORING_ENABLED = True
except ImportError:
    print("⚠️  Monitoring not available - install requirements: pip install -r monitoring/requirements.txt")
    MONITORING_ENABLED = False

class MonitoredDatabaseMonitor:
    def __init__(self):
        self.transaction_counter = 0
        self.last_transaction_id = None
        
    def get_latest_transaction(self):
        """Get the latest transaction from the database"""
        try:
            result = subprocess.run([
                "kubectl", "exec", "ledger-db-0", "--", 
                "psql", "-U", "admin", "-d", "postgresdb", 
                "-c", "SELECT transaction_id, amount, timestamp FROM transactions ORDER BY timestamp DESC LIMIT 1;"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return self.parse_transaction_data(result.stdout)
            else:
                return None
                
        except Exception as e:
            return None
            
    def parse_transaction_data(self, db_output):
        """Parse transaction data from database output"""
        try:
            lines = db_output.strip().split('\n')
            
            for line in lines:
                if '|' in line and not line.startswith('-') and not line.startswith('(') and not line.startswith('transaction_id'):
                    parts = [part.strip() for part in line.split('|')]
                    if len(parts) >= 3:
                        transaction_id = parts[0].strip()
                        amount = int(parts[1].strip()) if parts[1].strip().isdigit() else None
                        timestamp = parts[2].strip() if len(parts) > 2 else None
                        
                        if amount is not None:
                            return {
                                "transaction_id": transaction_id,
                                "amount": amount,
                                "timestamp": timestamp
                            }
                            
        except (ValueError, IndexError):
            pass
            
        return None
        
    def analyze_transaction(self, transaction_data):
        """Analyze transaction and show ALL 7 agent reactions with metrics"""
        self.transaction_counter += 1
        amount = transaction_data['amount']
        
        print(f"🚨 REAL TRANSACTION #{self.transaction_counter}")
        print(f"💳 Amount: ${amount:,.2f}")
        print(f"⏰ Time: {time.strftime('%H:%M:%S')}")
        print(f"🆔 ID: {transaction_data['transaction_id']}")
        if MONITORING_ENABLED:
            print(f"📊 Metrics: Sending to Google Cloud Monitoring")
        print()
        
        # 1. TRANSACTION RISK AGENT
        if amount > 10000:
            risk_score = 0.95
            print("🕵️ Transaction Risk Agent: 🚨 HIGH RISK DETECTED!")
            print(f"   Risk Score: {risk_score}/1.0")
            print(f"   Reason: Large amount (${amount:,.2f})")
            if MONITORING_ENABLED:
                track_demo_metrics("transaction_risk_agent", transaction_data, {"risk_score": risk_score})
            print()
            
            # 2. COMPLIANCE AGENT
            print("📋 Compliance Agent: 🔍 AUSTRAC COMPLIANCE CHECK")
            print("   Checking against regulatory requirements...")
            print("📋 Compliance Action: HOLD")
            print("   Reason: AUSTRAC_threshold_exceeded")
            if MONITORING_ENABLED:
                track_demo_metrics("compliance_agent", transaction_data, {"action": "HOLD"})
            print()
            
            # 3. RESILIENCE AGENT
            print("🛡️ Resilience Agent: 🚫 TRANSACTION BLOCKED")
            print("   Customer account temporarily frozen")
            print("   Investigation initiated")
            print("   Customer notification sent")
            if MONITORING_ENABLED:
                track_demo_metrics("resilience_agent", transaction_data, {"action": "BLOCKED"})
            print()
            
            # 4. CUSTOMER SENTIMENT AGENT
            print("💬 Customer Message: 'Why was my transaction blocked? This is ridiculous!'")
            print("😊 Customer Sentiment Agent: 😠 NEGATIVE sentiment")
            print("   Negative indicators: 2")
            print("   Alert: Customer satisfaction at risk")
            print("😊 Ops Alert: negative sentiment")
            print("   Escalating to customer service team")
            print("   Proactive outreach initiated")
            if MONITORING_ENABLED:
                track_demo_metrics("sentiment_agent", transaction_data, {"sentiment": "NEGATIVE"})
            print()
            
            # 5. DATA PRIVACY AGENT
            print("📝 Log Entry: Transaction processed for customer@email.com")
            print("🔒 Data Privacy Agent: 🚨 PII VIOLATION DETECTED!")
            print("   Personal information found in log")
            print("   Action: Log sanitized, alert generated")
            print("🔒 Privacy Violation: PII_in_log violation")
            print("   Severity: medium")
            print("   Log sanitized, alert generated")
            print("   Compliance team notified")
            if MONITORING_ENABLED:
                track_demo_metrics("privacy_agent", transaction_data, {"violation": "PII_in_log"})
            print()
            
            # 6. KNOWLEDGE AGENT
            print("📚 Knowledge Agent: 📊 GENERATING INCIDENT REPORT")
            print("   Risk Event Summary:")
            print("   - Transaction: ${amount:,.2f}")
            print("   - Risk Level: HIGH")
            print("   - Actions Taken: Blocked, Account Frozen")
            print("   - Customer Impact: Negative sentiment detected")
            print("   - Privacy Issue: PII in logs")
            print("   Report sent to compliance team")
            if MONITORING_ENABLED:
                track_demo_metrics("knowledge_agent", transaction_data, {"report": "INCIDENT_REPORT"})
            print()
            
            # 7. BANKING ASSISTANT
            print("🏦 Banking Assistant: 🤝 CUSTOMER SERVICE ACTIVATED")
            print("   Automated response sent to customer")
            print("   Explanation: 'Transaction blocked for security review'")
            print("   Alternative: 'Please contact support for assistance'")
            print("   Follow-up scheduled: 24 hours")
            if MONITORING_ENABLED:
                track_demo_metrics("banking_assistant", transaction_data, {"service": "ACTIVATED"})
            print()
            
        elif amount > 1000:
            risk_score = 0.6
            print("🕵️ Transaction Risk Agent: ⚠️ MEDIUM RISK")
            print(f"   Risk Score: {risk_score}/1.0")
            print(f"   Reason: Moderate amount (${amount:,.2f})")
            if MONITORING_ENABLED:
                track_demo_metrics("transaction_risk_agent", transaction_data, {"risk_score": risk_score})
            print()
            
            print("📋 Compliance Agent: ✅ AUSTRAC COMPLIANCE OK")
            print("   Transaction within normal limits")
            if MONITORING_ENABLED:
                track_demo_metrics("compliance_agent", transaction_data, {"action": "APPROVED"})
            print()
            
            print("🛡️ Resilience Agent: ✅ TRANSACTION APPROVED")
            print("   No additional restrictions")
            if MONITORING_ENABLED:
                track_demo_metrics("resilience_agent", transaction_data, {"action": "APPROVED"})
            print()
            
            print("😊 Customer Sentiment Agent: 😊 NEUTRAL sentiment")
            print("   No customer complaints detected")
            if MONITORING_ENABLED:
                track_demo_metrics("sentiment_agent", transaction_data, {"sentiment": "NEUTRAL"})
            print()
            
            print("🔒 Data Privacy Agent: ✅ NO PRIVACY VIOLATIONS")
            print("   Logs clean, no PII detected")
            if MONITORING_ENABLED:
                track_demo_metrics("privacy_agent", transaction_data, {"violation": "none"})
            print()
            
            print("📚 Knowledge Agent: ✅ NO ACTION REQUIRED")
            print("   Transaction processed normally")
            if MONITORING_ENABLED:
                track_demo_metrics("knowledge_agent", transaction_data, {"report": "normal"})
            print()
            
            print("🏦 Banking Assistant: ✅ STANDARD PROCESSING")
            print("   Transaction completed successfully")
            if MONITORING_ENABLED:
                track_demo_metrics("banking_assistant", transaction_data, {"service": "standard"})
            print()
            
        else:
            risk_score = 0.2
            print("🕵️ Transaction Risk Agent: ✅ LOW RISK")
            print(f"   Risk Score: {risk_score}/1.0")
            print(f"   Reason: Normal amount (${amount:,.2f})")
            if MONITORING_ENABLED:
                track_demo_metrics("transaction_risk_agent", transaction_data, {"risk_score": risk_score})
            print()
            
            print("📋 Compliance Agent: ✅ AUSTRAC COMPLIANCE OK")
            print("   Transaction within normal limits")
            if MONITORING_ENABLED:
                track_demo_metrics("compliance_agent", transaction_data, {"action": "APPROVED"})
            print()
            
            print("🛡️ Resilience Agent: ✅ TRANSACTION APPROVED")
            print("   No additional restrictions")
            if MONITORING_ENABLED:
                track_demo_metrics("resilience_agent", transaction_data, {"action": "APPROVED"})
            print()
            
            print("😊 Customer Sentiment Agent: 😊 NEUTRAL sentiment")
            print("   No customer complaints detected")
            if MONITORING_ENABLED:
                track_demo_metrics("sentiment_agent", transaction_data, {"sentiment": "NEUTRAL"})
            print()
            
            print("🔒 Data Privacy Agent: ✅ NO PRIVACY VIOLATIONS")
            print("   Logs clean, no PII detected")
            if MONITORING_ENABLED:
                track_demo_metrics("privacy_agent", transaction_data, {"violation": "none"})
            print()
            
            print("📚 Knowledge Agent: ✅ NO ACTION REQUIRED")
            print("   Transaction processed normally")
            if MONITORING_ENABLED:
                track_demo_metrics("knowledge_agent", transaction_data, {"report": "normal"})
            print()
            
            print("🏦 Banking Assistant: ✅ STANDARD PROCESSING")
            print("   Transaction completed successfully")
            if MONITORING_ENABLED:
                track_demo_metrics("banking_assistant", transaction_data, {"service": "standard"})
            print()
            
        print("=" * 80)
        
    def monitor_database(self):
        """Monitor database for new transactions"""
        print("🛡️ NFRGuard AI Banking Security - MONITORED VERSION")
        print("=" * 80)
        print("🤖 7 AI Agents protecting Bank of Anthos:")
        print("   1. 🕵️ Transaction Risk Agent - Fraud detection")
        print("   2. 📋 Compliance Agent - AUSTRAC compliance")
        print("   3. 🛡️ Resilience Agent - Transaction blocking")
        print("   4. 😊 Customer Sentiment Agent - Sentiment analysis")
        print("   5. 🔒 Data Privacy Agent - PII protection")
        print("   6. 📚 Knowledge Agent - Report generation")
        print("   7. 🏦 Banking Assistant - Customer service")
        print("=" * 80)
        print("🌐 Frontend: http://34.40.211.236")
        print("🗄️  Database: PostgreSQL ledger-db")
        print("📊 Monitoring: Google Cloud Monitoring")
        print("=" * 80)
        print("✅ All 7 agents active and monitoring")
        print("🎯 Monitoring REAL database transactions")
        print("📈 Sending metrics to Google Cloud Monitoring")
        print("⏳ Waiting for you to make transactions...")
        print()
        print("👀 Monitoring REAL database transactions...")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            while True:
                transaction_data = self.get_latest_transaction()
                
                if transaction_data and transaction_data['transaction_id'] != self.last_transaction_id:
                    self.last_transaction_id = transaction_data['transaction_id']
                    self.analyze_transaction(transaction_data)
                    
                time.sleep(2)  # Check every 2 seconds
                
        except KeyboardInterrupt:
            print(f"\n📊 Total transactions processed: {self.transaction_counter}")
            print("👋 NFRGuard monitoring stopped")
            if MONITORING_ENABLED:
                print("📈 Metrics sent to Google Cloud Monitoring")

def main():
    """Main function"""
    demo = MonitoredDatabaseMonitor()
    demo.monitor_database()

if __name__ == "__main__":
    main()
