# 🏗️ NFRGuard AI Banking Security System - Complete Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           NFRGuard AI Banking Security System                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Bank of       │    │   Google        │    │   AI Agents     │    │   Monitoring    │
│   Anthos        │    │   Cloud         │    │   (ADK)         │    │   & Logging     │
│   Frontend      │    │   Platform      │    │                 │    │                 │
│   (Flask)       │    │   (GKE)         │    │                 │    │                 │
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

## AI Agent Communication Flow with Pub/Sub

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AI Agent Communication Flow                        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Transaction   │    │   Google Cloud  │    │   AI Agents     │    │   Actions       │
│   Created       │    │   Pub/Sub       │    │   (ADK)         │    │   Taken         │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User makes    │    │   Topics:       │    │   1. Risk       │    │   Block         │
│   transaction   │    │   • transaction │    │      Agent      │    │   Transaction   │
│                 │    │   • risk.flagged│    │                 │    │                 │
│   • Amount      │    │   • compliance  │    │   2. Compliance │    │   Freeze        │
│   • Time        │    │   • sentiment   │    │      Agent      │    │   Account       │
│   • Destination │    │   • privacy     │    │                 │    │                 │
│                 │    │   • ops.alert   │    │   3. Resilience │    │   Notify        │
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

## Technology Stack & Interactions

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

### **Communication Layer**
- **Google Cloud Pub/Sub** - Event messaging
- **Custom Messaging System** - Local event handling
- **Event Persistence** - Audit trail and replay

### **Monitoring Layer**
- **Google Cloud Monitoring**
- **Custom AI Metrics**
- **Real-time Alerts**

## AI Agent Architecture with Pub/Sub

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AI Agent Communication Flow                        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Transaction   │    │   Google Cloud  │    │   AI Agents     │    │   Actions       │
│   Created       │    │   Pub/Sub       │    │   (ADK)         │    │   Taken         │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User makes    │    │   Topics:       │    │   1. Risk       │    │   Block         │
│   transaction   │    │   • transaction │    │      Agent      │    │   Transaction   │
│                 │    │   • risk.flagged│    │                 │    │                 │
│   • Amount      │    │   • compliance  │    │   2. Compliance │    │   Freeze        │
│   • Time        │    │   • sentiment   │    │      Agent      │    │   Account       │
│   • Destination │    │   • privacy     │    │                 │    │                 │
│                 │    │   • ops.alert   │    │   3. Resilience │    │   Notify        │
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
│   Frontend      │    │   Microservices │    │   PostgreSQL    │    │   Pub/Sub       │
│   (Flask)       │    │   (Java/Python) │    │   Databases     │    │   Event Bus     │
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
- **Google Cloud Pub/Sub** - Event messaging and agent communication
- **Custom Messaging System** - Local event handling and persistence

### **AI & Machine Learning**
- **Gemini 2.5 Flash** - All 7 AI agents (Risk, Compliance, Resilience, Sentiment, Privacy, Knowledge, Banking Assistant)
- **Event-driven Architecture** - Asynchronous agent communication

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
│   HTTPS/SSL     │    │   Auto-scaling  │    │   Pods          │    │   Pub/Sub       │
│   Encryption    │    │   & Health      │    │   Management    │    │   Event Bus     │
│                 │    │   Checks        │    │                 │    │                 │
│   • Security    │    │   • High        │    │   • Frontend    │    │   • Real-time   │
│   • Performance │    │   • Availability│    │   • Services    │    │   • Scalable    │
│   • Reliability │    │   • Load        │    │   • Databases   │    │   • Reliable    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Key Technology Interactions

### **1. User Transaction Flow**
1. **User** → **Frontend (Flask)** → **Microservices (Java/Python)**
2. **Microservices** → **PostgreSQL Database** → **Transaction Stored**
3. **Database Change** → **Pub/Sub Event** → **AI Agents (ADK)**
4. **AI Agents** → **Risk Analysis** → **Compliance Check** → **Action Taken**

### **2. AI Agent Communication**
1. **Transaction Risk Agent** → **Pub/Sub Topic: risk.flagged**
2. **Compliance Agent** → **Pub/Sub Topic: compliance.action**
3. **Resilience Agent** → **Pub/Sub Topic: ops.alert**
4. **Customer Sentiment Agent** → **Pub/Sub Topic: sentiment.analyzed**
5. **Data Privacy Agent** → **Pub/Sub Topic: privacy.violation**
6. **Knowledge Agent** → **Pub/Sub Topic: report.generated**
7. **Banking Assistant** → **Pub/Sub Topic: customer.response**

### **3. Monitoring & Observability**
1. **AI Agents** → **Custom Metrics** → **Google Cloud Monitoring**
2. **System Logs** → **Google Cloud Logging** → **Real-time Alerts**
3. **Business Metrics** → **Dashboard** → **Stakeholder Reports**

### **4. Data Persistence**
1. **Transaction Data** → **PostgreSQL** → **ACID Compliance**
2. **Event Data** → **Pub/Sub** → **Event Replay Capability**
3. **Audit Logs** → **Google Cloud Logging** → **Compliance Reports**

This architecture demonstrates a production-ready AI-powered banking security system that combines modern cloud infrastructure with advanced AI agent technology to provide real-time fraud detection, compliance monitoring, and customer protection using Google Cloud Pub/Sub for scalable, reliable event-driven communication.
