#!/usr/bin/env python3
"""
MCP Integration Example for NFRGuard
Demonstrates how to integrate Model Context Protocol with existing agents
"""

import asyncio
import json
import sys
import os
from typing import Dict, List, Any

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

# Mock MCP implementation (replace with actual mcp library)
class MockMCPServer:
    """Mock MCP Server for demonstration"""
    
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        
    def register_tool(self, name: str, description: str, input_schema: Dict, handler):
        self.tools[name] = {
            "description": description,
            "input_schema": input_schema,
            "handler": handler
        }
        
    async def call_tool(self, name: str, arguments: Dict) -> Dict:
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        
        handler = self.tools[name]["handler"]
        result = await handler(arguments)
        return {
            "tool": name,
            "result": result,
            "server": self.name
        }

class MockMCPClient:
    """Mock MCP Client for demonstration"""
    
    def __init__(self, name: str):
        self.name = name
        self.connected_servers = {}
        
    async def connect_server(self, server: MockMCPServer):
        self.connected_servers[server.name] = server
        print(f"[MCP] {self.name} connected to {server.name}")
        
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict) -> Dict:
        if server_name not in self.connected_servers:
            raise ValueError(f"Server {server_name} not connected")
            
        server = self.connected_servers[server_name]
        result = await server.call_tool(tool_name, arguments)
        print(f"[MCP] {self.name} called {server_name}.{tool_name}")
        return result

# MCP Servers Implementation

class BankingToolsMCPServer(MockMCPServer):
    """Banking Tools MCP Server"""
    
    def __init__(self):
        super().__init__("banking-tools")
        self._register_tools()
        
    def _register_tools(self):
        # Register check_balance tool
        self.register_tool(
            "check_balance",
            "Check account balance",
            {
                "type": "object",
                "properties": {
                    "account_id": {"type": "string"}
                },
                "required": ["account_id"]
            },
            self._check_balance_handler
        )
        
        # Register get_transaction_history tool
        self.register_tool(
            "get_transaction_history",
            "Get transaction history for account",
            {
                "type": "object",
                "properties": {
                    "account_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["account_id"]
            },
            self._get_transaction_history_handler
        )
        
        # Register process_transaction tool
        self.register_tool(
            "process_transaction",
            "Process a new transaction",
            {
                "type": "object",
                "properties": {
                    "from_account": {"type": "string"},
                    "to_account": {"type": "string"},
                    "amount": {"type": "number"},
                    "description": {"type": "string"}
                },
                "required": ["from_account", "to_account", "amount"]
            },
            self._process_transaction_handler
        )
    
    async def _check_balance_handler(self, args: Dict) -> Dict:
        account_id = args["account_id"]
        # Simulate balance check
        return {
            "status": "success",
            "account_id": account_id,
            "balance": "1,250.50",
            "currency": "USD",
            "last_updated": "2025-01-14T21:46:00Z"
        }
    
    async def _get_transaction_history_handler(self, args: Dict) -> Dict:
        account_id = args["account_id"]
        limit = args.get("limit", 10)
        
        # Simulate transaction history
        transactions = [
            {
                "transaction_id": "txn_001",
                "amount": "100.00",
                "type": "debit",
                "description": "Purchase at Store ABC",
                "timestamp": "2025-01-14T10:30:00Z"
            },
            {
                "transaction_id": "txn_002",
                "amount": "500.00",
                "type": "credit", 
                "description": "Salary deposit",
                "timestamp": "2025-01-13T09:00:00Z"
            }
        ]
        
        return {
            "status": "success",
            "account_id": account_id,
            "transactions": transactions[:limit],
            "total_count": len(transactions)
        }
    
    async def _process_transaction_handler(self, args: Dict) -> Dict:
        from_account = args["from_account"]
        to_account = args["to_account"]
        amount = args["amount"]
        description = args.get("description", "")
        
        # Simulate transaction processing
        return {
            "status": "success",
            "transaction_id": "txn_new_001",
            "from_account": from_account,
            "to_account": to_account,
            "amount": amount,
            "description": description,
            "timestamp": "2025-01-14T21:46:00Z",
            "status": "completed"
        }

class RiskAnalysisMCPServer(MockMCPServer):
    """Risk Analysis MCP Server"""
    
    def __init__(self):
        super().__init__("risk-analysis")
        self._register_tools()
        
    def _register_tools(self):
        # Register analyze_transaction_risk tool
        self.register_tool(
            "analyze_transaction_risk",
            "Analyze transaction for risk factors",
            {
                "type": "object",
                "properties": {
                    "transaction_data": {"type": "object"}
                },
                "required": ["transaction_data"]
            },
            self._analyze_transaction_risk_handler
        )
        
        # Register get_risk_score tool
        self.register_tool(
            "get_risk_score",
            "Calculate risk score for transaction",
            {
                "type": "object",
                "properties": {
                    "transaction_id": {"type": "string"},
                    "amount": {"type": "number"},
                    "metadata": {"type": "object"}
                },
                "required": ["transaction_id", "amount"]
            },
            self._get_risk_score_handler
        )
    
    async def _analyze_transaction_risk_handler(self, args: Dict) -> Dict:
        transaction_data = args["transaction_data"]
        
        # Simulate ML-based risk analysis
        risk_factors = []
        if transaction_data.get("amount", 0) > 10000:
            risk_factors.append("high_amount")
        if transaction_data.get("metadata", {}).get("cross_border", False):
            risk_factors.append("cross_border")
        if transaction_data.get("metadata", {}).get("unusual_time", False):
            risk_factors.append("unusual_timing")
            
        return {
            "risk_factors": risk_factors,
            "analysis": f"Transaction analyzed: {len(risk_factors)} risk factors detected",
            "confidence": 0.95
        }
    
    async def _get_risk_score_handler(self, args: Dict) -> Dict:
        transaction_id = args["transaction_id"]
        amount = args["amount"]
        metadata = args.get("metadata", {})
        
        # Simple risk scoring algorithm
        score = 0.0
        if amount > 10000:
            score += 0.4
        if metadata.get("cross_border", False):
            score += 0.3
        if metadata.get("unusual_time", False):
            score += 0.2
        if metadata.get("new_merchant", False):
            score += 0.1
            
        return {
            "transaction_id": transaction_id,
            "risk_score": min(score, 1.0),
            "risk_level": "high" if score > 0.7 else "medium" if score > 0.3 else "low"
        }

class ComplianceMCPServer(MockMCPServer):
    """Compliance MCP Server"""
    
    def __init__(self):
        super().__init__("compliance")
        self._register_tools()
        
    def _register_tools(self):
        # Register check_austrac_compliance tool
        self.register_tool(
            "check_austrac_compliance",
            "Check AUSTRAC compliance rules",
            {
                "type": "object",
                "properties": {
                    "transaction_data": {"type": "object"}
                },
                "required": ["transaction_data"]
            },
            self._check_austrac_compliance_handler
        )
        
        # Register get_compliance_action tool
        self.register_tool(
            "get_compliance_action",
            "Determine required compliance action",
            {
                "type": "object",
                "properties": {
                    "risk_score": {"type": "number"},
                    "transaction_amount": {"type": "number"}
                },
                "required": ["risk_score", "transaction_amount"]
            },
            self._get_compliance_action_handler
        )
    
    async def _check_austrac_compliance_handler(self, args: Dict) -> Dict:
        transaction_data = args["transaction_data"]
        amount = transaction_data.get("amount", 0)
        
        # AUSTRAC compliance rules
        compliance_checks = {
            "amount_threshold": amount > 10000,
            "cross_border": transaction_data.get("metadata", {}).get("cross_border", False),
            "suspicious_pattern": transaction_data.get("metadata", {}).get("suspicious", False)
        }
        
        return {
            "compliant": not any(compliance_checks.values()),
            "checks": compliance_checks,
            "required_reporting": compliance_checks["amount_threshold"]
        }
    
    async def _get_compliance_action_handler(self, args: Dict) -> Dict:
        risk_score = args["risk_score"]
        transaction_amount = args["transaction_amount"]
        
        # Determine compliance action based on risk and amount
        if risk_score > 0.8 or transaction_amount > 10000:
            action = "hold_and_report"
        elif risk_score > 0.5:
            action = "monitor_closely"
        else:
            action = "monitor"
            
        return {
            "action": action,
            "reason": f"Risk score: {risk_score}, Amount: {transaction_amount}",
            "rule": "AUSTRAC_threshold"
        }

# Enhanced Agent with MCP Integration

class MCPEnhancedTransactionRiskAgent:
    """Transaction Risk Agent enhanced with MCP"""
    
    def __init__(self):
        self.name = "transaction_risk_agent_mcp"
        self.mcp_client = MockMCPClient(self.name)
        self.banking_tools = None
        self.risk_tools = None
        self.compliance_tools = None
        
    async def initialize_mcp_connections(self):
        """Initialize MCP server connections"""
        # Create MCP servers
        banking_server = BankingToolsMCPServer()
        risk_server = RiskAnalysisMCPServer()
        compliance_server = ComplianceMCPServer()
        
        # Connect to servers
        await self.mcp_client.connect_server(banking_server)
        await self.mcp_client.connect_server(risk_server)
        await self.mcp_client.connect_server(compliance_server)
        
        self.banking_tools = banking_server
        self.risk_tools = risk_server
        self.compliance_tools = compliance_server
        
        print(f"[{self.name}] MCP connections initialized")
    
    async def analyze_transaction_with_mcp(self, transaction_data: Dict) -> Dict:
        """Analyze transaction using MCP tools"""
        print(f"[{self.name}] Analyzing transaction: {transaction_data['transaction_id']}")
        
        # Use risk analysis MCP tools
        risk_analysis = await self.mcp_client.call_tool(
            "risk-analysis",
            "analyze_transaction_risk",
            {"transaction_data": transaction_data}
        )
        
        risk_score = await self.mcp_client.call_tool(
            "risk-analysis", 
            "get_risk_score",
            {
                "transaction_id": transaction_data["transaction_id"],
                "amount": transaction_data["amount"],
                "metadata": transaction_data.get("metadata", {})
            }
        )
        
        # Determine if transaction is suspicious
        suspicious = risk_score["result"]["risk_score"] > 0.8
        
        result = {
            "transaction_id": transaction_data["transaction_id"],
            "risk_analysis": risk_analysis["result"],
            "risk_score": risk_score["result"]["risk_score"],
            "risk_level": risk_score["result"]["risk_level"],
            "suspicious": suspicious,
            "detected_by": f"{self.name}_v1"
        }
        
        if suspicious:
            print(f"[{self.name}] Suspicious transaction detected: {result}")
            
        return result
    
    async def get_account_info_with_mcp(self, account_id: str) -> Dict:
        """Get account information using MCP banking tools"""
        balance = await self.mcp_client.call_tool(
            "banking-tools",
            "check_balance", 
            {"account_id": account_id}
        )
        
        history = await self.mcp_client.call_tool(
            "banking-tools",
            "get_transaction_history",
            {"account_id": account_id, "limit": 5}
        )
        
        return {
            "balance": balance["result"],
            "recent_transactions": history["result"]
        }

# MCP Orchestrator

class MCPOrchestrator:
    """Central MCP orchestrator for NFRGuard"""
    
    def __init__(self):
        self.name = "nfrguard-orchestrator"
        self.agents = {}
        self.servers = {}
        
    async def initialize(self):
        """Initialize MCP servers and agents"""
        print(f"[{self.name}] Initializing MCP infrastructure...")
        
        # Create MCP servers
        self.servers["banking"] = BankingToolsMCPServer()
        self.servers["risk"] = RiskAnalysisMCPServer()
        self.servers["compliance"] = ComplianceMCPServer()
        
        # Create and initialize agents
        self.agents["risk"] = MCPEnhancedTransactionRiskAgent()
        await self.agents["risk"].initialize_mcp_connections()
        
        print(f"[{self.name}] MCP infrastructure initialized")
    
    async def process_transaction_flow(self, transaction_data: Dict) -> Dict:
        """Process complete transaction flow using MCP"""
        print(f"[{self.name}] Processing transaction flow: {transaction_data['transaction_id']}")
        
        # 1. Risk Analysis
        risk_result = await self.agents["risk"].analyze_transaction_with_mcp(transaction_data)
        
        flow_result = {
            "transaction_id": transaction_data["transaction_id"],
            "risk_analysis": risk_result,
            "compliance_check": None,
            "action_taken": None
        }
        
        # 2. Compliance Check (if suspicious)
        if risk_result["suspicious"]:
            compliance_result = await self.agents["risk"].mcp_client.call_tool(
                "compliance",
                "get_compliance_action",
                {
                    "risk_score": risk_result["risk_score"],
                    "transaction_amount": transaction_data["amount"]
                }
            )
            
            flow_result["compliance_check"] = compliance_result["result"]
            
            # 3. Determine action
            if compliance_result["result"]["action"] == "hold_and_report":
                flow_result["action_taken"] = "Transaction held for compliance review"
            else:
                flow_result["action_taken"] = f"Transaction monitored: {compliance_result['result']['action']}"
        
        return flow_result

# Test Functions

async def test_mcp_integration():
    """Test MCP integration functionality"""
    print("🚀 Testing MCP Integration for NFRGuard")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = MCPOrchestrator()
    await orchestrator.initialize()
    
    # Test transaction data
    test_transaction = {
        "transaction_id": "txn_mcp_test_001",
        "amount": 15000,
        "from_account": "acc_001",
        "to_account": "acc_002",
        "description": "Large transfer",
        "metadata": {
            "cross_border": True,
            "unusual_time": False,
            "new_merchant": False
        }
    }
    
    # Process transaction flow
    result = await orchestrator.process_transaction_flow(test_transaction)
    
    print("\n📊 Transaction Flow Result:")
    print(json.dumps(result, indent=2))
    
    # Test account info retrieval
    print("\n🏦 Testing Account Info Retrieval:")
    account_info = await orchestrator.agents["risk"].get_account_info_with_mcp("acc_001")
    print(json.dumps(account_info, indent=2))
    
    print("\n✅ MCP Integration Test Completed!")

async def test_individual_mcp_tools():
    """Test individual MCP tools"""
    print("\n🔧 Testing Individual MCP Tools")
    print("=" * 30)
    
    # Test banking tools
    banking_server = BankingToolsMCPServer()
    balance_result = await banking_server.call_tool("check_balance", {"account_id": "acc_test"})
    print(f"Balance Check: {balance_result}")
    
    # Test risk analysis tools
    risk_server = RiskAnalysisMCPServer()
    risk_result = await risk_server.call_tool("get_risk_score", {
        "transaction_id": "txn_test",
        "amount": 15000,
        "metadata": {"cross_border": True}
    })
    print(f"Risk Analysis: {risk_result}")
    
    # Test compliance tools
    compliance_server = ComplianceMCPServer()
    compliance_result = await compliance_server.call_tool("get_compliance_action", {
        "risk_score": 0.9,
        "transaction_amount": 15000
    })
    print(f"Compliance Check: {compliance_result}")

if __name__ == "__main__":
    async def main():
        await test_individual_mcp_tools()
        await test_mcp_integration()
    
    asyncio.run(main())
