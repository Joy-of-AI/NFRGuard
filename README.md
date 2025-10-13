# 🏦 Fintech AI AWS - Banking Security System

**AI-Powered Banking Security on AWS EKS**

This project (`fintech-ai-aws`) extends Bank of Anthos with **7 specialized AI agents** powered by **AWS Bedrock Claude 3.5 Sonnet** that provide real-time fraud detection, compliance monitoring, and regulatory guidance. Built entirely on AWS services (EKS, Bedrock, EventBridge, OpenSearch), it demonstrates enterprise-grade AI security for banking operations.

### 🎯 **Project: Fintech-AI-AWS**
- **Repository**: `Fintech_AI_AWS`
- **Platform**: Amazon Web Services (AWS)
- **Region**: ap-southeast-2 (Sydney, Australia)
- **Cluster**: Amazon EKS with spot instances
- **AI**: AWS Bedrock (Claude 3.5 Sonnet + Titan Embeddings)
- **Status**: Production-ready, professionally organized

### 🤖 **AI Agents Included**
- **Transaction Risk Agent** - Detects suspicious transactions in real-time
- **Compliance Agent** - Ensures 100% AUSTRAC compliance
- **Resilience Agent** - Takes immediate action on threats
- **Customer Sentiment Agent** - Monitors customer satisfaction
- **Data Privacy Agent** - Protects personal information
- **Knowledge Agent** - Generates human-readable reports
- **Banking Assistant** - Provides automated customer service

### 📚 **Documentation** (All Numbered 00-17 for Easy Reading)

**🎯 Start Here:**
- **[00-START-HERE](src/agents/docs/reference/00-START-HERE.md)** ← **Read this first!**
- **[09-Getting-Started](src/agents/docs/reference/09-Getting-Started.txt)** - Quick reference card
- **[10-Quick-Reference](src/agents/docs/reference/10-Quick-Reference.txt)** - Command cheat sheet

**📖 Complete Guide (Read in Order 01-17):**

**Architecture (01-02):**
- 01️⃣ **[Architecture Overview](src/agents/docs/architecture/01-Architecture-Overview.md)** - System design & 7 agents
- 02️⃣ **[Agent Communication](src/agents/docs/architecture/02-Agent-Communication.md)** - EventBridge & 768-dim vectors

**Deployment (03-05):**
- 03️⃣ **[Quick Resume](src/agents/docs/deployment/03-Quick-Resume-Guide.md)** - Resume paused cluster (2 min)
- 04️⃣ **[Deployment Operations](src/agents/docs/deployment/04-Deployment-Operations.md)** - Operations guide
- 05️⃣ **[Complete Deployment](src/agents/docs/deployment/05-Complete-Deployment-Guide.md)** - Full setup + troubleshooting

**Technical (06-08):**
- 06️⃣ **[Monitoring](src/agents/docs/technical/06-Monitoring-Observability.md)** - CloudWatch & system health
- 07️⃣ **[Technical Implementation](src/agents/docs/technical/07-Technical-Implementation.md)** - Code deep dive
- 08️⃣ **[RAG System](src/agents/docs/technical/08-RAG-System-Guide.md)** - 42 regulatory documents

**Reference (11-17):**
- 11️⃣ **[Changelog](src/agents/docs/reference/11-Changelog.txt)** - Recent changes
- 12️⃣ **[Complete Answers](src/agents/docs/reference/12-Complete-Answers.md)** - Technical Q&A
- 13️⃣ **[Demo Presentation](src/agents/docs/reference/13-Demo-Presentation.md)** - Demo scripts
- 14️⃣ **[Deployment Status](src/agents/docs/reference/14-Deployment-Status.md)** - Current system status
- And 3 more reference docs...

### 🚀 **Quick Start - AWS EKS Deployment**

**First Time Setup (~30 minutes):**
```bash
cd src/agents

# Automated setup (recommended)
python scripts/01-complete-setup.py

# OR Manual step-by-step
# See: src/agents/docs/deployment/05-Complete-Deployment-Guide.md
```

**Daily Use (2 minutes):**
```bash
cd src/agents

# Resume paused cluster
bash scripts/06-resume-cluster.sh

# Test agents
kubectl port-forward -n nfrguard-agents svc/banking-assistant-agent 8080:8080
```

**When Done:**
```bash
# Pause (recommended) - ~$2.40/day
bash scripts/05-pause-cluster.sh

# OR Delete everything - $0/day
bash scripts/07-cleanup-aws-resources.sh
```

### 🎯 **Key Features**
- **Real-time Fraud Detection** - AI agents analyze every transaction using Claude 3.5 Sonnet
- **AWS Bedrock Integration** - Enterprise-grade AI with AWS security and scalability
- **EKS Deployment** - Production-ready Kubernetes on AWS with spot instances
- **Automated Compliance** - Ensures AUSTRAC compliance with Australian banking regulations
- **Customer Sentiment Analysis** - Detects customer frustration and escalates to support
- **Privacy Protection** - Automatically detects and sanitizes personal information in logs
- **Pause/Resume** - Save costs by pausing when not in use (2-minute resume)
- **Multi-agent Coordination** - 7 agents work together using event-driven architecture

### 💰 **Cost Management**
- **Running**: ~$0.10/hour (~$2.40/day) with spot instances
- **Paused**: ~$0.10/hour (pods at 0, cluster active)
- **Deleted**: $0/day (nothing running)

### 🧠 **RAG System (Optional)**
- **42 Regulatory Documents** - ASIC, APRA, AUSTRAC, AFCA
- **Mock RAG** - $0 cost, keyword search, citations included
- **Full RAG** - OpenSearch Serverless + Titan Embeddings (~$700/mo)
- **See**: `src/agents/RAG/DEPLOY_RAG_DECISION.md` for deployment options

### ☁️ **AWS Services Used**

**Core Infrastructure:**
- **Amazon EKS** - Kubernetes cluster (`fintech-ai-aws-cluster`)
- **Amazon EC2** - Spot instances (t3.large) for cost optimization
- **Amazon ECR** - Docker image registry (7 agent images)
- **Amazon VPC** - Network isolation and security

**AI & Machine Learning:**
- **AWS Bedrock** - Claude 3.5 Sonnet (LLM for agents)
- **AWS Bedrock** - Titan Embeddings V2 (768-dim vectors for RAG)
- **Amazon OpenSearch Serverless** - Vector database (optional, for RAG)

**Integration & Messaging:**
- **AWS EventBridge** - Event-driven agent communication
- **AWS SNS** - Fallback messaging system
- **AWS IAM** - Role-based access control (IRSA)

**Storage (Optional):**
- **Amazon S3** - Document and artifact storage
- **Amazon DynamoDB** - State management

### 📋 **Current Status**
- ✅ **Deployed**: AWS EKS cluster in `ap-southeast-2` (Sydney)
- ✅ **Agents**: 13 pods (7 AI agents) - Currently paused
- ✅ **Application**: Bank of Anthos integrated with AI agents
- ✅ **AI**: Claude 3.5 Sonnet working via AWS Bedrock
- ✅ **Communication**: AWS EventBridge event-driven architecture
- ✅ **RAG System**: 42 Australian regulatory documents ready
- ✅ **Mock RAG**: Tested and working ($0 cost)
- ✅ **Documentation**: Numbered 00-17 for easy reading
- ✅ **Scripts**: Numbered 01-07 for execution order
- ✅ **Professional**: Ready for presentation and sharing

### 🏗️ **Architecture**
<img width="1172" height="731" alt="Fintech-AI-AWS-Solution-Architecture" src="https://github.com/user-attachments/assets/a452a3d3-c069-4281-bcf0-18de6da70082" />

---

## 📁 **Project Structure**

```
Fintech_AI_AWS/
└── bank-of-anthos/
    └── src/agents/              ← Security AI Agents
        ├── agents/              7 AI agent implementations
        ├── docs/                Documentation (numbered 00-17)
        ├── RAG/                 42 regulatory documents
        ├── scripts/             Automation (numbered 01-07)
        ├── shared/              AWS libraries (Bedrock, EventBridge)
        ├── k8s/                 Kubernetes manifests
        └── tests/               Integration tests
```

---

##

# Bank of Anthos

**Bank of Anthos** is a sample HTTP-based web app that simulates a bank's payment processing network, allowing users to create artificial bank accounts and complete transactions.

Google uses this application to demonstrate how developers can modernize enterprise applications using Google Cloud products, including: [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine), [Anthos Service Mesh (ASM)](https://cloud.google.com/anthos/service-mesh), [Anthos Config Management (ACM)](https://cloud.google.com/anthos/config-management), [Migrate to Containers](https://cloud.google.com/migrate/containers), [Spring Cloud GCP](https://spring.io/projects/spring-cloud-gcp), [Cloud Operations](https://cloud.google.com/products/operations), [Cloud SQL](https://cloud.google.com/sql/docs), [Cloud Build](https://cloud.google.com/build), and [Cloud Deploy](https://cloud.google.com/deploy). This application works on any Kubernetes cluster.

If you are using Bank of Anthos, please ★Star this repository to show your interest!

**Note to Googlers:** Please fill out the form at [go/bank-of-anthos-form](https://goto2.corp.google.com/bank-of-anthos-form).

## Screenshots

| Sign in                                                                                                        | Home                                                                                                    |
| ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| [![Login](/docs/img/login.png)](/docs/img/login.png) | [![User Transactions](/docs/img/transactions.png)](/docs/img/transactions.png) |


## Service architecture

![Architecture Diagram](/docs/img/architecture.png)

| Service                                                 | Language      | Description                                                                                                                                  |
| ------------------------------------------------------- | ------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| [frontend](/src/frontend)                              | Python        | Exposes an HTTP server to serve the website. Contains login page, signup page, and home page.                                                |
| [ledger-writer](/src/ledger/ledgerwriter)              | Java          | Accepts and validates incoming transactions before writing them to the ledger.                                                               |
| [balance-reader](/src/ledger/balancereader)            | Java          | Provides efficient readable cache of user balances, as read from `ledger-db`.                                                                |
| [transaction-history](/src/ledger/transactionhistory)  | Java          | Provides efficient readable cache of past transactions, as read from `ledger-db`.                                                            |
| [ledger-db](/src/ledger/ledger-db)                     | PostgreSQL    | Ledger of all transactions. Option to pre-populate with transactions for demo users.                                                         |
| [user-service](/src/accounts/userservice)              | Python        | Manages user accounts and authentication. Signs JWTs used for authentication by other services.                                              |
| [contacts](/src/accounts/contacts)                     | Python        | Stores list of other accounts associated with a user. Used for drop down in "Send Payment" and "Deposit" forms.                              |
| [accounts-db](/src/accounts/accounts-db)               | PostgreSQL    | Database for user accounts and associated data. Option to pre-populate with demo users.                                                      |
| [loadgenerator](/src/loadgenerator)                    | Python/Locust | Continuously sends requests imitating users to the frontend. Periodically creates new accounts and simulates transactions between them.      |

## Interactive quickstart (GKE)

The following button opens up an interactive tutorial showing how to deploy Bank of Anthos in GKE:

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://ssh.cloud.google.com/cloudshell/editor?show=ide&cloudshell_git_repo=https://github.com/GoogleCloudPlatform/bank-of-anthos&cloudshell_workspace=.&cloudshell_tutorial=extras/cloudshell/tutorial.md)

## Quickstart (GKE)

1. Ensure you have the following requirements:
   - [Google Cloud project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project).
   - Shell environment with `gcloud`, `git`, and `kubectl`.

2. Clone the repository.

   ```sh
   git clone https://github.com/GoogleCloudPlatform/bank-of-anthos
   cd bank-of-anthos/
   ```

3. Set the Google Cloud project and region and ensure the Google Kubernetes Engine API is enabled.

   ```sh
   export PROJECT_ID=<PROJECT_ID>
   export REGION=us-central1
   gcloud services enable container.googleapis.com \
     --project=${PROJECT_ID}
   ```

   Substitute `<PROJECT_ID>` with the ID of your Google Cloud project.

4. Create a GKE cluster and get the credentials for it.

   ```sh
   gcloud container clusters create-auto bank-of-anthos \
     --project=${PROJECT_ID} --region=${REGION}
   ```

   Creating the cluster may take a few minutes.

5. Deploy Bank of Anthos to the cluster.

   ```sh
   kubectl apply -f ./extras/jwt/jwt-secret.yaml
   kubectl apply -f ./kubernetes-manifests
   ```

6. Wait for the pods to be ready.

   ```sh
   kubectl get pods
   ```

   After a few minutes, you should see the Pods in a `Running` state:

   ```
   NAME                                  READY   STATUS    RESTARTS   AGE
   accounts-db-6f589464bc-6r7b7          1/1     Running   0          99s
   balancereader-797bf6d7c5-8xvp6        1/1     Running   0          99s
   contacts-769c4fb556-25pg2             1/1     Running   0          98s
   frontend-7c96b54f6b-zkdbz             1/1     Running   0          98s
   ledger-db-5b78474d4f-p6xcb            1/1     Running   0          98s
   ledgerwriter-84bf44b95d-65mqf         1/1     Running   0          97s
   loadgenerator-559667b6ff-4zsvb        1/1     Running   0          97s
   transactionhistory-5569754896-z94cn   1/1     Running   0          97s
   userservice-78dc876bff-pdhtl          1/1     Running   0          96s
   ```

7. Access the web frontend in a browser using the frontend's external IP.

   ```sh
   kubectl get service frontend | awk '{print $4}'
   ```

   Visit `http://EXTERNAL_IP` in a web browser to access your instance of Bank of Anthos.

8. Once you are done with it, delete the GKE cluster.

   ```sh
   gcloud container clusters delete bank-of-anthos \
     --project=${PROJECT_ID} --region=${REGION}
   ```

   Deleting the cluster may take a few minutes.

## Additional deployment options

- **Workload Identity**: [See these instructions.](/docs/workload-identity.md)
- **Cloud SQL**: [See these instructions](/extras/cloudsql) to replace the in-cluster databases with hosted Google Cloud SQL.
- **Multi Cluster with Cloud SQL**: [See these instructions](/extras/cloudsql-multicluster) to replicate the app across two regions using GKE, Multi Cluster Ingress, and Google Cloud SQL.
- **Istio**: [See these instructions](/extras/istio) to configure an IngressGateway.
- **Anthos Service Mesh**: ASM requires Workload Identity to be enabled in your GKE cluster. [See the workload identity instructions](/docs/workload-identity.md) to configure and deploy the app. Then, apply `extras/istio/` to your cluster to configure frontend ingress.
- **Java Monolith (VM)**: We provide a version of this app where the three Java microservices are coupled together into one monolithic service, which you can deploy inside a VM (eg. Google Compute Engine). See the [ledgermonolith](/src/ledgermonolith) directory.

## Documentation

<!-- This section is duplicated in the docs/ README: https://github.com/GoogleCloudPlatform/bank-of-anthos/blob/main/docs/README.md -->

- [Development](/docs/development.md) to learn how to run and develop this app locally.
- [Environments](/docs/environments.md) to learn how to deploy on non-GKE clusters.
- [Workload Identity](/docs/workload-identity.md) to learn how to set-up Workload Identity.
- [CI/CD pipeline](/docs/ci-cd-pipeline.md) to learn details about and how to set-up the CI/CD pipeline.
- [Troubleshooting](/docs/troubleshooting.md) to learn how to resolve common problems.

## Demos featuring Bank of Anthos
- [Tutorial: Explore Anthos (Google Cloud docs)](https://cloud.google.com/anthos/docs/tutorials/explore-anthos)
- [Tutorial: Migrating a monolith VM to GKE](https://cloud.google.com/migrate/containers/docs/migrating-monolith-vm-overview-setup)
- [Tutorial: Running distributed services on GKE private clusters using ASM](https://cloud.google.com/service-mesh/docs/distributed-services-private-clusters)
- [Tutorial: Run full-stack workloads at scale on GKE](https://cloud.google.com/kubernetes-engine/docs/tutorials/full-stack-scale)
- [Architecture: Anthos on bare metal](https://cloud.google.com/architecture/ara-anthos-on-bare-metal)
- [Architecture: Creating and deploying secured applications](https://cloud.google.com/architecture/security-foundations/creating-deploying-secured-apps)
- [Keynote @ Google Cloud Next '20: Building trust for speedy innovation](https://www.youtube.com/watch?v=7QR1z35h_yc)
- [Workshop @ IstioCon '22: Manage and secure distributed services with ASM](https://www.youtube.com/watch?v=--mPdAxovfE)
