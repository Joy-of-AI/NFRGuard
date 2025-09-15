# Bank of Anthos Agents

This directory contains AI agents built with Google's Agent Development Kit (ADK) for the Bank of Anthos application.

## Architecture

The agents are designed as independent microservices that integrate with the existing Bank of Anthos services:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Banking       │    │   Fraud         │    │   Customer      │
│   Assistant     │    │   Detection     │    │   Support       │
│   Agent         │    │   Agent         │    │   Agent         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Shared        │
                    │   Components    │
                    │   (API Client,  │
                    │    Auth, etc.)  │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Balance       │    │   Transaction   │    │   Ledger        │
│   Reader        │    │   History       │    │   Writer        │
│   Service       │    │   Service       │    │   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Available Agents

### 1. Banking Assistant (`banking-assistant/`)
- **Purpose**: Primary banking operations and customer assistance
- **Capabilities**: Balance checking, transaction history, account management
- **Tools**: BalanceTools, TransactionTools

### 2. Fraud Detection (`fraud-detection/`)
- **Purpose**: Monitor transactions for suspicious activity
- **Capabilities**: Real-time fraud detection, risk scoring, alert generation
- **Tools**: FraudAnalysisTools, RiskAssessmentTools

### 3. Customer Support (`customer-support/`)
- **Purpose**: Handle customer inquiries and support requests
- **Capabilities**: FAQ responses, ticket management, issue resolution
- **Tools**: SupportTools, KnowledgeBaseTools

### 4. Transaction Analyzer (`transaction-analyzer/`)
- **Purpose**: Analyze transaction patterns and provide insights
- **Capabilities**: Spending analysis, trend detection, reporting
- **Tools**: AnalysisTools, ReportingTools

## Directory Structure

```
agents/
├── banking-assistant/          # Banking operations agent
│   ├── __init__.py
│   ├── agent.py               # Main agent implementation
│   ├── .env                   # Environment configuration
│   ├── tools/                 # Agent-specific tools
│   │   ├── __init__.py
│   │   ├── balance_tools.py
│   │   └── transaction_tools.py
│   ├── config.yaml            # Agent configuration
│   ├── tests/                 # Test suite
│   ├── README.md              # Agent documentation
│   ├── Dockerfile             # Container definition
│   ├── skaffold.yaml          # Development deployment
│   └── k8s/                   # Kubernetes manifests
│       ├── deployment.yaml
│       └── service.yaml
├── fraud-detection/           # Fraud detection agent
├── customer-support/          # Customer support agent
├── transaction-analyzer/      # Transaction analysis agent
├── shared/                    # Shared components
│   ├── __init__.py
│   ├── bank_api_client.py     # API client for Bank services
│   ├── database_connector.py  # Database utilities
│   └── auth_helper.py         # Authentication helpers
└── README.md                  # This file
```

## Getting Started

### Prerequisites
- Python 3.12+
- Google ADK installed
- Bank of Anthos services running
- Kubernetes cluster (for deployment)

### Development Setup

1. **Clone and navigate to agents directory**:
   ```bash
   cd bank-of-anthos/src/agents
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install google-adk
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cd banking-assistant
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run an agent**:
   ```bash
   python agent.py
   ```

### Deployment

Each agent can be deployed independently using Kubernetes:

```bash
# Deploy banking assistant
kubectl apply -f banking-assistant/k8s/

# Deploy fraud detection
kubectl apply -f fraud-detection/k8s/

# Deploy all agents
kubectl apply -f */k8s/
```

## Development Guidelines

### Adding a New Agent

1. Create new agent directory following the structure above
2. Implement `agent.py` with your agent logic
3. Create agent-specific tools in `tools/` directory
4. Add configuration files (`.env`, `config.yaml`)
5. Create Kubernetes manifests in `k8s/` directory
6. Add tests in `tests/` directory
7. Update this README with agent information

### Shared Components

Use the `shared/` directory for components that multiple agents need:
- API clients for Bank of Anthos services
- Database connection utilities
- Authentication helpers
- Common logging configurations

### Testing

Each agent should have comprehensive tests:
- Unit tests for individual tools
- Integration tests for service communication
- End-to-end tests for complete workflows

Run tests:
```bash
cd <agent-directory>
python -m pytest tests/
```

## Integration with Bank of Anthos

The agents integrate with existing Bank of Anthos services:

- **Balance Reader**: For account balance information
- **Transaction History**: For transaction records
- **Ledger Writer**: For processing transactions
- **User Service**: For authentication and user management
- **Accounts DB**: For account data
- **Ledger DB**: For transaction data

## Monitoring and Observability

Each agent includes:
- Structured logging
- Health check endpoints
- Metrics collection
- Distributed tracing support

## Contributing

1. Follow the existing code structure and patterns
2. Add comprehensive tests for new features
3. Update documentation for any changes
4. Ensure all agents can be deployed independently
5. Follow Google ADK best practices

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.


################################################################################################
### Change git repo to below:
git remote set-url origin https://github.com/Joy-of-AI/NFRGuard.git


### venv
cd bank-of-anthos/src/agents
.venv/Scripts/Activate.ps1  


### This code is ADK Compliant: Still follows the ADK pattern with __init__.py, agent.py, .env
# ADK Guide- https://google.github.io/adk-docs/get-started/quickstart/#set-up-environment-install-adk
# ADK Sample Git- https://github.com/google/adk-samples/tree/main/python

### Create multiple folders in each agent's file
mkdir transaction-analyzer\tools, transaction-analyzer\tests, transaction-analyzer\k8s

### Create .env in each agent file
# Navigate to agent directory
cd banking-assistant

# Create .env file
echo "# Banking Assistant Agent Environment Configuration" > .env

# Create config.yaml file  
echo "# Banking Assistant Agent Configuration" > config.yaml

# Create README.md file
echo "# Banking Assistant Agent" > README.md

# Create __init__.py file
echo "# Banking Assistant Agent" > __init__.py

# Create agent.py file
echo "# Banking Assistant Agent Implementation" > agent.py

# Create Dockerfile
echo "# Banking Assistant Agent Dockerfile" > Dockerfile

# Create skaffold.yaml
echo "# Banking Assistant Agent Skaffold" > skaffold.yaml

# Create requirements.txt
echo "google-adk" > requirements.txt

### Now create an __init__.py file in the folder:
echo "from . import agent" > multi_tool_agent/__init__.py

# Your __init__.py should now look like this:
from . import agent

### Configuration File Options:
YAML (config.yaml) - What we're using now
TOML (config.toml) - More readable, better for complex configs
JSON (config.json) - Simple but less readable
Python (config.py) - Most flexible

For Agent Development Kit (ADK) and multi-agent AI systems, the recommended configuration format is usually YAML. Here’s why:

Format	Alignment with ADK & Multi-Agent Systems	Why (Reasoning)
YAML	✅ Recommended	Google ADK samples (adk-samples repo) and most agentic frameworks use config.yaml. YAML handles nested structures (agents, tools, endpoints, roles, memory, etc.) clearly.
TOML	⚠️ Possible but not common	Simpler, but not widely adopted in agent frameworks. Harder to express deep nesting compared to YAML.
JSON	⚠️ Sometimes used	Works if agents are deployed as services (APIs), but becomes messy for deeply hierarchical configs like multi-agent orchestration.
Python (config.py)	❌ Not aligned	Too dynamic, less portable, and not recommended by Google ADK. Could break standardization for multi-agent configs.

🔑 Why YAML is the best fit for ADK & multi-agent orchestration
Supports hierarchical definitions (e.g., multiple agents with different roles, tools, memory).
Easy to integrate with Kubernetes & GKE (which heavily use YAML for deployment).
Used directly in Google’s ADK examples (e.g., config.yaml defines agent capabilities, tools, endpoints).
Readable by both humans and systems, critical for debugging large multi-agent systems.


### To check the current directory structure and show you what we've created:
tree /f

### Next Steps: 
- Add the remaining agents (fraud-detection, customer-support, transaction-analyzer) by copying the banking-assistant structure
- Add Kubernetes manifests in each agent's k8s/ directory
- Add to main skaffold.yaml to integrate with Bank of Anthos deployment
- The structure is now ADK-compliant, scalable, and production-ready! Each agent can be developed, tested, and deployed independently while sharing common components.


### Install GCP CLI
# The Google Cloud CLI is a set of tools to create and manage Google Cloud resources.
# Google Cloud CLI includes the gcloud, gsutil and bq command-line tools.
# Download and install it from here- https://cloud.google.com/sdk/docs/install

# Then add the path to env variables
$env:Path += ";C:\Users\ah_Am\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"

# Then check it
gcloud --version 

# Then 
gcloud auth application-default login


