# 🔗 MCP Integration Plan (Future Enhancement)

> **Note:** This is a **FUTURE ENHANCEMENT** document. MCP is **NOT IMPLEMENTED** in the current system. The current implementation uses **Google Cloud Pub/Sub** for agent communication. For the actual implementation, see the [Architecture Overview](01-Architecture-Overview.md) and [Technical Implementation](05-Technical-Implementation.md) guides.

# Future MCP Integration for NFRGuard

**⚠️ IMPORTANT: This is a planning document only. The current system uses Pub/Sub for agent communication, not MCP.**

## 🎯 **MCP Integration Points**

### **1. MCP Host Process (Orchestrator)**
- **Role**: Central coordinator managing all agent interactions
- **Responsibilities**: Security, workflow orchestration, resource management
- **Location**: New service `mcp-orchestrator/`

### **2. MCP Servers (Tool Providers)**
- **Banking Tools Server**: Balance, transaction, account management tools
- **Risk Analysis Server**: ML models, risk scoring, anomaly detection tools
- **Compliance Server**: Regulatory rules, AUSTRAC checks, compliance tools
- **Knowledge Server**: Documentation, alerts, human-readable explanations

### **3. MCP Clients (Your Agents)**
- Each agent becomes an MCP client
- Standardized tool access via MCP protocol
- Enhanced resource and prompt management

## 🏗️ **Enhanced Architecture with MCP**

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Host Process                            │
│              (Orchestrator & Security Layer)                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼───┐         ┌───▼───┐         ┌───▼───┐
│ MCP   │         │ MCP   │         │ MCP   │
│Server │         │Server │         │Server │
│Banking│         │Risk   │         │Comply │
│Tools  │         │Tools  │         │Tools  │
└───┬───┘         └───┬───┘         └───┬───┘
    │                 │                 │
    └─────────────────┼─────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼───┐         ┌───▼───┐         ┌───▼───┐
│Agent  │         │Agent  │         │Agent  │
│Client │         │Client │         │Client │
│Risk   │         │Comply │         │Resil  │
└───────┘         └───────┘         └───────┘
```

## 🛠️ **MCP Implementation Plan**

### **Phase 1: MCP Server Setup**

#### **1. Banking Tools MCP Server**
```python
# mcp-servers/banking-tools-server.py
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("banking-tools")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="check_balance",
            description="Check account balance",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string"}
                }
            }
        ),
        Tool(
            name="get_transaction_history",
            description="Get transaction history",
            inputSchema={
                "type": "object", 
                "properties": {
                    "account_id": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "check_balance":
        # Call Bank of Anthos Balance Reader service
        return TextContent(type="text", text=check_balance(arguments["account_id"]))
    elif name == "get_transaction_history":
        # Call Bank of Anthos Transaction History service
        return TextContent(type="text", text=get_transaction_history(arguments["account_id"], arguments.get("limit", 10)))
```

#### **2. Risk Analysis MCP Server**
```python
# mcp-servers/risk-analysis-server.py
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("risk-analysis")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="analyze_transaction_risk",
            description="Analyze transaction for risk factors",
            inputSchema={
                "type": "object",
                "properties": {
                    "transaction_data": {"type": "object"}
                }
            }
        ),
        Tool(
            name="get_risk_score",
            description="Calculate risk score for transaction",
            inputSchema={
                "type": "object",
                "properties": {
                    "transaction_id": {"type": "string"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "analyze_transaction_risk":
        # ML model analysis
        risk_result = analyze_with_ml_model(arguments["transaction_data"])
        return TextContent(type="text", text=risk_result)
```

#### **3. Compliance MCP Server**
```python
# mcp-servers/compliance-server.py
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("compliance")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="check_austrac_compliance",
            description="Check AUSTRAC compliance rules",
            inputSchema={
                "type": "object",
                "properties": {
                    "transaction_data": {"type": "object"}
                }
            }
        ),
        Tool(
            name="get_compliance_action",
            description="Determine required compliance action",
            inputSchema={
                "type": "object",
                "properties": {
                    "risk_score": {"type": "number"}
                }
            }
        )
    ]
```

### **Phase 2: Agent MCP Client Integration**

#### **Enhanced Transaction Risk Agent**
```python
# transaction_risk_agent/agent.py
import asyncio
from mcp.client import Client
from google.adk.agents import Agent

class MCPTransactionRiskAgent:
    def __init__(self):
        self.mcp_client = Client("transaction-risk-agent")
        self.banking_tools = None
        self.risk_tools = None
        
    async def initialize_mcp_connections(self):
        # Connect to MCP servers
        self.banking_tools = await self.mcp_client.connect("banking-tools-server")
        self.risk_tools = await self.mcp_client.connect("risk-analysis-server")
        
    async def analyze_transaction_with_mcp(self, transaction_data):
        # Use MCP tools for analysis
        risk_analysis = await self.risk_tools.call_tool(
            "analyze_transaction_risk", 
            {"transaction_data": transaction_data}
        )
        
        risk_score = await self.risk_tools.call_tool(
            "get_risk_score",
            {"transaction_id": transaction_data["transaction_id"]}
        )
        
        return {
            "analysis": risk_analysis.text,
            "score": float(risk_score.text),
            "suspicious": float(risk_score.text) > 0.8
        }

# Initialize agent with MCP
agent = MCPTransactionRiskAgent()
await agent.initialize_mcp_connections()

root_agent = Agent(
    name="transaction_risk_agent_mcp",
    model="gemini-2.5-flash",
    description="MCP-enhanced transaction risk analysis",
    instruction="Use MCP tools for comprehensive risk analysis",
    tools=[agent.analyze_transaction_with_mcp]
)
```

### **Phase 3: MCP Orchestrator**

#### **Central MCP Host Process**
```python
# mcp-orchestrator/orchestrator.py
import asyncio
from mcp.server import Server
from mcp.client import Client
from typing import Dict, List

class MCPOrchestrator:
    def __init__(self):
        self.server = Server("nfrguard-orchestrator")
        self.agent_clients: Dict[str, Client] = {}
        self.tool_servers: Dict[str, Client] = {}
        
    async def initialize(self):
        # Initialize MCP servers
        self.tool_servers["banking"] = await self.connect_server("banking-tools-server")
        self.tool_servers["risk"] = await self.connect_server("risk-analysis-server")
        self.tool_servers["compliance"] = await self.connect_server("compliance-server")
        
        # Initialize agent clients
        self.agent_clients["risk"] = await self.connect_client("transaction-risk-agent")
        self.agent_clients["compliance"] = await self.connect_client("compliance-agent")
        self.agent_clients["resilience"] = await self.connect_client("resilience-agent")
        
    async def orchestrate_transaction_flow(self, transaction_data):
        """Orchestrate complete transaction processing flow"""
        
        # 1. Risk Analysis
        risk_result = await self.agent_clients["risk"].call_tool(
            "analyze_transaction_with_mcp",
            {"transaction_data": transaction_data}
        )
        
        if risk_result.get("suspicious", False):
            # 2. Compliance Check
            compliance_result = await self.agent_clients["compliance"].call_tool(
                "check_compliance_with_mcp",
                {"risk_data": risk_result}
            )
            
            # 3. Resilience Action
            if compliance_result.get("action") == "hold_and_report":
                resilience_result = await self.agent_clients["resilience"].call_tool(
                    "apply_hold_with_mcp",
                    {"compliance_data": compliance_result}
                )
                
        return {
            "risk": risk_result,
            "compliance": compliance_result,
            "resilience": resilience_result
        }

# Initialize orchestrator
orchestrator = MCPOrchestrator()
await orchestrator.initialize()
```

## 🎯 **Key Benefits of MCP Integration**

### **1. Standardized Tool Access**
- **Before**: Each agent implements its own API clients
- **After**: Standardized MCP tool interface across all agents

### **2. Enhanced Resource Management**
- **Centralized**: All tools managed by MCP servers
- **Scalable**: Easy to add new tools and capabilities
- **Secure**: Centralized security and access control

### **3. Improved Interoperability**
- **Cross-Framework**: Agents can use tools from different frameworks
- **Vendor Agnostic**: Easy integration with third-party tools
- **Future-Proof**: Standard protocol for tool integration

### **4. Better Prompt Management**
- **Centralized Prompts**: MCP servers can provide prompt templates
- **Context Sharing**: Agents can share context via MCP
- **Dynamic Prompts**: Context-aware prompt generation

## 🚀 **Implementation Steps**

### **Step 1: Install MCP Dependencies**
```bash
pip install mcp
pip install mcp-server
pip install mcp-client
```

### **Step 2: Create MCP Server Structure**
```
mcp-servers/
├── banking-tools-server/
│   ├── __init__.py
│   ├── server.py
│   └── tools/
├── risk-analysis-server/
│   ├── __init__.py
│   ├── server.py
│   └── models/
├── compliance-server/
│   ├── __init__.py
│   ├── server.py
│   └── rules/
└── knowledge-server/
    ├── __init__.py
    ├── server.py
    └── prompts/
```

### **Step 3: Enhance Existing Agents**
- Add MCP client initialization
- Replace direct API calls with MCP tool calls
- Maintain backward compatibility

### **Step 4: Deploy MCP Orchestrator**
- Central coordination service
- Security and access control
- Workflow orchestration

## 📊 **MCP vs Current Approach**

| Aspect | Current Approach | With MCP |
|--------|------------------|----------|
| **Tool Access** | Direct API calls | Standardized MCP tools |
| **Resource Management** | Per-agent | Centralized servers |
| **Security** | Distributed | Centralized control |
| **Scalability** | Limited | Highly scalable |
| **Interoperability** | Custom protocols | Standard MCP protocol |
| **Maintenance** | Per-agent updates | Centralized updates |

## 🎯 **Recommended Implementation Order**

1. **Start with Banking Tools MCP Server** - Most straightforward
2. **Enhance Transaction Risk Agent** - High impact, clear use case
3. **Add Compliance MCP Server** - Regulatory requirements
4. **Implement MCP Orchestrator** - Central coordination
5. **Migrate Remaining Agents** - Gradual migration

**Note: This MCP integration is a future enhancement. The current NFRGuard system successfully uses Pub/Sub for agent communication and is production-ready! 🚀**
