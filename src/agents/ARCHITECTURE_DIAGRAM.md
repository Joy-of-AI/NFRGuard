# 🏗️ NFRGuard AI Agents - Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           NFRGuard AI Banking Security System                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Bank of       │    │   Google        │    │   AI Agents     │    │   Monitoring    │
│   Anthos        │    │   Cloud         │    │   (ADK)         │    │   & Logging     │
│   Frontend      │    │   Platform      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI        │    │   GKE Cluster   │    │   Event Bus     │    │   Google Cloud  │
│   (Flask)       │    │   (Kubernetes)  │    │   (Pub/Sub)     │    │   Monitoring    │
│                 │    │                 │    │                 │    │                 │
│   • Login       │    │   • Auto-scaling│    │   • transaction │    │   • Metrics     │
│   • Dashboard   │    │   • Load Balancer│    │   • risk.flagged│    │   • Alerts      │
│   • Transactions│    │   • Service Mesh│    │   • compliance  │    │   • Logs        │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Microservices │    │   PostgreSQL    │    │   AI Agent      │    │   Custom        │
│   Architecture  │    │   Databases     │    │   Processing    │    │   Metrics       │
│                 │    │                 │    │                 │    │                 │
│   • User Service│    │   • accounts-db │    │   • Risk Analysis│    │   • Risk Scores │
│   • Ledger      │    │   • ledger-db   │    │   • Compliance  │    │   • Processing  │
│   • Frontend    │    │   • Persistent  │    │   • Sentiment   │    │   • Success     │
│   • Contacts    │    │   • ACID        │    │   • Privacy     │    │   • Business    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack

### **Frontend Layer**
- **Bank of Anthos Web UI** (Flask/Python)
- **Real-time Transaction Interface**
- **User Authentication & Dashboard**

### **Infrastructure Layer**
- **Google Kubernetes Engine (GKE)**
- **Auto-scaling Cluster**
- **Load Balancer & Service Mesh**
- **Persistent Storage**

### **Data Layer**
- **PostgreSQL Databases**
- **ACID Compliance**
- **Real-time Transaction Logs**

### **AI Agent Layer**
- **Google Agent Development Kit (ADK)**
- **7 Specialized AI Agents**
- **Event-driven Architecture**

### **Monitoring Layer**
- **Google Cloud Monitoring**
- **Custom AI Metrics**
- **Real-time Alerts**

## AI Agent Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AI Agent Communication Flow                        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Transaction   │    │   Event Bus     │    │   AI Agents     │    │   Actions       │
│   Created       │    │   (Pub/Sub)     │    │   (ADK)         │    │   Taken         │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User makes    │    │   transaction.  │    │   1. Risk       │    │   Block         │
│   transaction   │    │   created       │    │      Agent      │    │   Transaction   │
│                 │    │                 │    │                 │    │                 │
│   • Amount      │    │   • risk.flagged│    │   2. Compliance │    │   Freeze        │
│   • Time        │    │   • compliance  │    │      Agent      │    │   Account       │
│   • Destination │    │   • sentiment   │    │                 │    │                 │
│                 │    │   • privacy     │    │   3. Resilience │    │   Notify        │
│                 │    │                 │    │      Agent      │    │   Customer      │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Real-time     │    │   Agent         │    │   4. Sentiment  │    │   Generate      │
│   Processing    │    │   Coordination  │    │      Agent      │    │   Reports       │
│                 │    │                 │    │                 │    │                 │
│   • < 1 second  │    │   • Parallel    │    │   5. Privacy    │    │   • Human       │
│   • 24/7        │    │   • Decoupled   │    │      Agent      │    │   • Machine     │
│   • Scalable    │    │   • Reliable    │    │                 │    │                 │
│                 │    │                 │    │   6. Knowledge  │    │   • Compliance  │
│                 │    │                 │    │      Agent      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Data Flow & Processing                             │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User          │    │   Bank of       │    │   Database      │    │   AI Agents     │
│   Interaction   │    │   Anthos        │    │   Layer         │    │   Processing    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Microservices │    │   PostgreSQL    │    │   Event Bus     │
│   (Flask)       │    │   (Java/Python) │    │   Databases     │    │   (Pub/Sub)     │
│                 │    │                 │    │                 │    │                 │
│   • Login       │    │   • User Service│    │   • accounts-db │    │   • Real-time   │
│   • Dashboard   │    │   • Ledger      │    │   • ledger-db   │    │   • Scalable    │
│   • Transactions│    │   • Contacts    │    │   • ACID        │    │   • Reliable    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HTTP/HTTPS    │    │   REST APIs     │    │   SQL Queries   │    │   Event         │
│   Requests      │    │   Communication │    │   & Updates     │    │   Messages      │
│                 │    │                 │    │                 │    │                 │
│   • JSON        │    │   • Microservice│    │   • Transactions│    │   • Risk Events │
│   • RESTful     │    │   • Communication│    │   • User Data   │    │   • Compliance  │
│   • Stateless   │    │   • Load        │    │   • Audit Logs  │    │   • Sentiment   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technologies Used

### **Core Technologies**
- **Google Kubernetes Engine (GKE)** - Container orchestration
- **Google Agent Development Kit (ADK)** - AI agent framework
- **Google Cloud Pub/Sub** - Event-driven agent communication
- **Custom Messaging System** - Decoupled inter-agent messaging

### **Data Sources**
- **Bank of Anthos Transaction Data** - Real banking transactions
- **PostgreSQL Databases** - User accounts and transaction history
- **Real-time Logs** - System and application logs
- **Customer Messages** - Sentiment analysis data

### **Monitoring & Observability**
- **Google Cloud Monitoring** - Infrastructure metrics
- **Custom AI Metrics** - Agent performance tracking
- **Real-time Alerts** - Automated incident response
- **Business Metrics** - Fraud prevention and compliance

## Key Findings & Learnings

### **Technical Insights**
1. **Event-driven architecture** enables scalable, decoupled agent communication
2. **Real-time processing** requires careful resource management and monitoring
3. **Microservices integration** provides flexibility but requires robust error handling
4. **AI agent coordination** needs clear communication protocols and fallback mechanisms

### **Business Impact**
1. **Fraud prevention** can be automated with high accuracy using AI agents
2. **Compliance monitoring** reduces regulatory risk and manual oversight
3. **Customer sentiment analysis** enables proactive customer service
4. **Privacy protection** can be automated to prevent data breaches

### **Operational Learnings**
1. **Monitoring is critical** for AI agent performance and system health
2. **Human oversight** remains important for complex decision-making
3. **Gradual rollout** reduces risk when deploying AI systems
4. **Documentation and training** are essential for system adoption

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Production Deployment                              │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Internet      │    │   Google Cloud  │    │   GKE Cluster   │    │   AI Agents     │
│   Users         │    │   Load Balancer │    │   (Australia)   │    │   (ADK)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HTTPS/SSL     │    │   Auto-scaling  │    │   Pods          │    │   Event Bus     │
│   Encryption    │    │   & Health      │    │   Management    │    │   (Pub/Sub)     │
│                 │    │   Checks        │    │                 │    │                 │
│   • Security    │    │   • High        │    │   • Frontend    │    │   • Real-time   │
│   • Performance │    │   • Availability│    │   • Services    │    │   • Scalable    │
│   • Reliability │    │   • Load        │    │   • Databases   │    │   • Reliable    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

This architecture demonstrates a production-ready AI-powered banking security system that combines modern cloud infrastructure with advanced AI agent technology to provide real-time fraud detection, compliance monitoring, and customer protection.
