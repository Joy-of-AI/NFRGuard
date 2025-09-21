#!/usr/bin/env python3
"""
NFRGuard AI Agent Metrics: Custom metrics for monitoring AI agent performance
Tracks agent-specific metrics and sends them to Google Cloud Monitoring
"""

import time
import json
from typing import Dict, Any, Optional
from google.cloud import monitoring_v3
from google.cloud.monitoring_v3 import query

class AgentMetrics:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"
        
    def track_transaction_risk_agent(self, risk_score: float, amount: float, processing_time: float):
        """Track Transaction Risk Agent metrics"""
        metrics = {
            "risk_score": risk_score,
            "transaction_amount": amount,
            "processing_time": processing_time,
            "timestamp": time.time()
        }
        self._send_metric("transaction_risk_agent", "risk_assessment", metrics)
        
    def track_compliance_agent(self, compliance_check: str, success: bool, processing_time: float):
        """Track Compliance Agent metrics"""
        metrics = {
            "compliance_check": compliance_check,
            "success": 1 if success else 0,
            "processing_time": processing_time,
            "timestamp": time.time()
        }
        self._send_metric("compliance_agent", "compliance_check", metrics)
        
    def track_resilience_agent(self, action: str, processing_time: float):
        """Track Resilience Agent metrics"""
        metrics = {
            "action": action,
            "processing_time": processing_time,
            "timestamp": time.time()
        }
        self._send_metric("resilience_agent", "resilience_action", metrics)
        
    def track_sentiment_agent(self, sentiment: str, confidence: float, processing_time: float):
        """Track Customer Sentiment Agent metrics"""
        metrics = {
            "sentiment": sentiment,
            "confidence": confidence,
            "processing_time": processing_time,
            "timestamp": time.time()
        }
        self._send_metric("sentiment_agent", "sentiment_analysis", metrics)
        
    def track_privacy_agent(self, pii_detected: bool, violation_type: str, processing_time: float):
        """Track Data Privacy Agent metrics"""
        metrics = {
            "pii_detected": 1 if pii_detected else 0,
            "violation_type": violation_type,
            "processing_time": processing_time,
            "timestamp": time.time()
        }
        self._send_metric("privacy_agent", "privacy_check", metrics)
        
    def track_knowledge_agent(self, report_type: str, processing_time: float):
        """Track Knowledge Agent metrics"""
        metrics = {
            "report_type": report_type,
            "processing_time": processing_time,
            "timestamp": time.time()
        }
        self._send_metric("knowledge_agent", "report_generation", metrics)
        
    def track_banking_assistant(self, query_type: str, response_time: float, success: bool):
        """Track Banking Assistant metrics"""
        metrics = {
            "query_type": query_type,
            "response_time": response_time,
            "success": 1 if success else 0,
            "timestamp": time.time()
        }
        self._send_metric("banking_assistant", "customer_service", metrics)
        
    def _send_metric(self, agent_name: str, metric_name: str, data: Dict[str, Any]):
        """Send custom metric to Google Cloud Monitoring"""
        try:
            series = monitoring_v3.TimeSeries()
            series.metric.type = f"custom.googleapis.com/nfrguard/{agent_name}/{metric_name}"
            series.resource.type = "gke_container"
            series.resource.labels["cluster_name"] = "bank-of-anthos"
            series.resource.labels["namespace_name"] = "default"
            series.resource.labels["pod_name"] = f"{agent_name}-pod"
            
            # Add metric labels
            for key, value in data.items():
                if key != "timestamp":
                    series.metric.labels[key] = str(value)
            
            # Add data point
            point = monitoring_v3.Point()
            point.value.double_value = data.get("timestamp", time.time())
            
            # Set timestamp properly
            from google.protobuf.timestamp_pb2 import Timestamp
            timestamp = Timestamp()
            timestamp.GetCurrentTime()
            point.interval.end_time.CopyFrom(timestamp)
            
            series.points = [point]
            
            # Send to Cloud Monitoring
            self.client.create_time_series(name=self.project_name, time_series=[series])
            
        except Exception as e:
            print(f"Error sending metric: {e}")

# Example usage for your enhanced demo
def track_demo_metrics(agent_name: str, transaction_data: Dict[str, Any], agent_response: Dict[str, Any]):
    """Track metrics from your enhanced demo"""
    metrics = AgentMetrics("gen-lang-client-0578497058")
    
    if agent_name == "transaction_risk_agent":
        risk_score = agent_response.get("risk_score", 0.5)
        amount = transaction_data.get("amount", 0)
        metrics.track_transaction_risk_agent(risk_score, amount, 0.1)
        
    elif agent_name == "compliance_agent":
        success = "HOLD" not in str(agent_response)
        metrics.track_compliance_agent("AUSTRAC", success, 0.05)
        
    elif agent_name == "resilience_agent":
        action = "BLOCKED" if "BLOCKED" in str(agent_response) else "APPROVED"
        metrics.track_resilience_agent(action, 0.02)
        
    elif agent_name == "sentiment_agent":
        sentiment = "NEGATIVE" if "NEGATIVE" in str(agent_response) else "POSITIVE"
        confidence = 0.8 if "NEGATIVE" in str(agent_response) else 0.9
        metrics.track_sentiment_agent(sentiment, confidence, 0.15)
        
    elif agent_name == "privacy_agent":
        pii_detected = "PII VIOLATION" in str(agent_response)
        violation_type = "PII_in_log" if pii_detected else "none"
        metrics.track_privacy_agent(pii_detected, violation_type, 0.08)
        
    elif agent_name == "knowledge_agent":
        report_type = "incident_report" if "INCIDENT REPORT" in str(agent_response) else "normal"
        metrics.track_knowledge_agent(report_type, 0.12)
        
    elif agent_name == "banking_assistant":
        success = "ACTIVATED" in str(agent_response)
        metrics.track_banking_assistant("transaction_support", 0.2, success)

if __name__ == "__main__":
    # Test the metrics system
    metrics = AgentMetrics("gen-lang-client-0578497058")
    
    # Example: Track a high-risk transaction
    metrics.track_transaction_risk_agent(0.95, 50000.0, 0.1)
    metrics.track_compliance_agent("AUSTRAC", False, 0.05)
    metrics.track_resilience_agent("BLOCKED", 0.02)
    metrics.track_sentiment_agent("NEGATIVE", 0.8, 0.15)
    metrics.track_privacy_agent(True, "PII_in_log", 0.08)
    metrics.track_knowledge_agent("incident_report", 0.12)
    metrics.track_banking_assistant("transaction_support", 0.2, True)
    
    print("✅ Metrics sent to Google Cloud Monitoring!")
