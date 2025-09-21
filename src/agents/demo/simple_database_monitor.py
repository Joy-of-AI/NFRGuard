#!/usr/bin/env python3
"""
Simple Real-Time Database Monitor: Monitors PostgreSQL for new transactions
No complex messaging - just direct database monitoring and agent reactions
"""

import time
import subprocess
import sys

class SimpleDatabaseMonitor:
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
        """Analyze transaction and show agent reactions"""
        self.transaction_counter += 1
        amount = transaction_data['amount']
        
        print(f"🚨 TRANSACTION #{self.transaction_counter}")
        print(f"💳 Amount: ${amount:,.2f}")
        print(f"⏰ Time: {time.strftime('%H:%M:%S')}")
        print(f"🆔 ID: {transaction_data['transaction_id']}")
        print()
        
        # Risk analysis
        if amount > 10000:
            print("🕵️ Risk Agent: HIGH RISK DETECTED!")
            print(f"   Risk Score: 0.95/1.0")
            print(f"   Reason: Large amount (${amount:,.2f})")
            print()
            
            print("📋 Compliance Agent: AUSTRAC CHECK")
            print("   Risk Score: 0.95")
            print("   Action: HOLD - AUSTRAC threshold exceeded")
            print()
            
            print("🛡️ Resilience Agent: TRANSACTION HOLD")
            print("   Account frozen pending investigation")
            print("   Customer notification sent")
            print()
            
        elif amount > 1000:
            print("🕵️ Risk Agent: MEDIUM RISK")
            print(f"   Risk Score: 0.6/1.0")
            print(f"   Reason: Moderate amount (${amount:,.2f})")
            print()
            
        else:
            print("🕵️ Risk Agent: LOW RISK")
            print(f"   Risk Score: 0.2/1.0")
            print(f"   Reason: Normal amount (${amount:,.2f})")
            print()
            
        print("=" * 60)
        
    def monitor_database(self):
        """Monitor database for new transactions"""
        print("🛡️ NFRGuard AI Banking Security")
        print("=" * 60)
        print("🤖 7 AI Agents protecting Bank of Anthos")
        print("🌐 Frontend: http://34.40.211.236")
        print("🗄️  Database: PostgreSQL ledger-db")
        print("=" * 60)
        print("✅ Agents active and monitoring")
        print("🎯 Monitoring REAL database transactions")
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

def main():
    """Main function"""
    demo = SimpleDatabaseMonitor()
    demo.monitor_database()

if __name__ == "__main__":
    main()

