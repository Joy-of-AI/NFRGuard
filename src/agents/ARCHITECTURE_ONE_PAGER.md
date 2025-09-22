# NFRGuard AI Banking Security System — One-Pager (End-to-End)

## Purpose
AI-augmented Bank of Anthos that detects fraud, ensures compliance, protects privacy, and improves customer experience using 7 agents powered by Gemini 2.5 Flash and RAG grounded in Australian regulations.

## User-to-Action Journey
1) Customer submits payment in Web UI → API Gateway → `transactions` service
2) `transactions` writes to `ledger-db` and publishes `transaction.created` (Pub/Sub)
3) Transaction Risk Agent consumes event → queries RAG (Vertex AI Vector Search) for AUSTRAC/CPS-230 context → scores risk → emits `risk.flagged`
4) Compliance Agent consumes `risk.flagged` → RAG guidance → decides action (monitor/hold/block/report) → emits `compliance.action`
5) Resilience Agent consumes `compliance.action` → calls core APIs (holds/blocks) → emits `ops.action`
6) Knowledge Agent aggregates events → RAG-backed plain-English summary for ops
7) Customer Sentiment Agent monitors `customer.messages` → escalates via `ops.alert`
8) Data Privacy Agent scans logs/requests → emits `privacy.alert` for PII risks
9) Observability: logs/metrics to Cloud Logging/Monitoring → dashboard + alerts
10) Nightly CronJob updates docs → re-embeds → updates Vertex AI Vector Search

## Components (by layer)
- Client/UI: Bank of Anthos Web UI, API Gateway
- Core Services: users, accounts, transactions, ledger (PostgreSQL `accounts-db`, `ledger-db`)
- Messaging: Google Cloud Pub/Sub (topics: `transaction.created`, `risk.events`, `compliance.events`, `ops.events`, `customer.messages`)
- AI Agents (ADK): Transaction Risk, Compliance, Resilience, Customer Sentiment, Data Privacy, Knowledge, Banking Assistant — all use Gemini 2.5 Flash
- RAG: Document downloader, chunking (LangChain), embeddings + search (Vertex AI Vector Search), ASIC/APRA/AUSTRAC/AFCA documents (daily updates)
- Observability: Cloud Logging, Cloud Monitoring (custom dashboard, alert policies)
- Platform: GKE (HPA/VPA/Cluster Autoscaler), Secret Manager, IAM, ConfigMaps, CronJobs

## GCP Services
- Compute: Google Kubernetes Engine (GKE)
- AI/ML: Gemini 2.5 Flash (via ADK), Vertex AI Vector Search
- Data: Cloud SQL (PostgreSQL) or in-cluster PG; Cloud Storage (documents)
- Messaging: Pub/Sub (topics + subscriptions + DLQs)
- Observability: Cloud Logging, Cloud Monitoring (dashboards/alerts)
- Security: IAM, Secret Manager, VPC (private GKE)

## Key Flows (ASCII)
```
UI → API GW → Core Services → Postgres
                 │                │
                 └─ Pub/Sub: transaction.created ──→ Transaction Risk Agent
                                             │           │
                                             │      RAG (Vertex AI Vector Search) ← GCS (docs)
                                             │           │
                                             └─ risk.flagged → Compliance Agent → compliance.action
                                                                    │
                                                                    └→ Resilience Agent → Core APIs
All agents/services → Cloud Logging/Monitoring → Dashboard + Alerts (Slack/Email)
Cron (daily) → Download docs → Embed → Update Vertex AI Vector Search
```

## Non-Functional
- Performance: <500ms end-to-end typical flow; agents scale independently (HPA/VPA)
- Reliability: 99.9% target; DLQs for Pub/Sub; readiness/liveness probes
- Security: Least-privilege IAM; TLS; Secret Manager; private GKE; audit logs
- Compliance: AUSTRAC/APRA/ASIC/AFCA covered via RAG; daily updates

## Run & Operate
- Deploy: `k8s/*.yaml` to `nfrguard-agents` namespace (GKE)
- Monitor: Cloud Monitoring dashboard (system health, agent/RAG KPIs), alerts
- Update Regs: CronJob (K8s) or Scheduler to refresh docs and index
- Extend: Add agents or documents; update filters/queries in RAG engine

---
Owner: NFRGuard Team · Region: australia-southeast1 · Model: Gemini 2.5 Flash
