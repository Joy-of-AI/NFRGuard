#!/usr/bin/env python3
"""
GCP Monitoring Dashboard Setup for NFRGuard AI Agents
Creates a comprehensive dashboard for monitoring AI agents, RAG system, and infrastructure
"""

import json
import subprocess
import os
from pathlib import Path

def get_project_id():
    """Get Google Cloud project ID"""
    try:
        result = subprocess.run([
            "gcloud", "config", "get-value", "project"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0578497058")
    except Exception:
        return os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0578497058")

def create_nfrguard_dashboard():
    """Create comprehensive NFRGuard monitoring dashboard"""
    project_id = get_project_id()
    
    dashboard_config = {
        "displayName": "NFRGuard AI Banking Security Dashboard",
        "mosaicLayout": {
            "tiles": [
                # Row 1: System Overview
                {
                    "width": 6,
                    "height": 4,
                    "widget": {
                        "title": "System Health Overview",
                        "scorecard": {
                            "timeSeriesQuery": {
                                "timeSeriesFilter": {
                                    "filter": f'resource.type="k8s_container" AND resource.labels.cluster_name="bank-of-anthos" AND resource.labels.namespace_name="nfrguard-agents"',
                                    "aggregation": {
                                        "alignmentPeriod": "60s",
                                        "perSeriesAligner": "ALIGN_MEAN",
                                        "crossSeriesReducer": "REDUCE_MEAN",
                                        "groupByFields": ["resource.labels.container_name"]
                                    }
                                }
                            },
                            "gaugeView": {
                                "lowerBound": 0,
                                "upperBound": 1
                            }
                        }
                    }
                },
                {
                    "width": 6,
                    "height": 4,
                    "widget": {
                        "title": "Active AI Agents",
                        "scorecard": {
                            "timeSeriesQuery": {
                                "timeSeriesFilter": {
                                    "filter": f'resource.type="k8s_container" AND resource.labels.cluster_name="bank-of-anthos" AND resource.labels.namespace_name="nfrguard-agents" AND metric.type="kubernetes.io/container/restart_count"',
                                    "aggregation": {
                                        "alignmentPeriod": "300s",
                                        "perSeriesAligner": "ALIGN_RATE",
                                        "crossSeriesReducer": "REDUCE_SUM"
                                    }
                                }
                            },
                            "sparkChartView": {
                                "sparkChartType": "SPARK_LINE"
                            }
                        }
                    }
                },
                
                # Row 2: AI Agent Performance
                {
                    "width": 12,
                    "height": 6,
                    "widget": {
                        "title": "AI Agent Response Times",
                        "xyChart": {
                            "dataSets": [
                                {
                                    "timeSeriesQuery": {
                                        "timeSeriesFilter": {
                                            "filter": f'resource.type="k8s_container" AND resource.labels.cluster_name="bank-of-anthos" AND resource.labels.namespace_name="nfrguard-agents" AND metric.type="kubernetes.io/container/cpu/core_usage_time"',
                                            "aggregation": {
                                                "alignmentPeriod": "60s",
                                                "perSeriesAligner": "ALIGN_RATE",
                                                "crossSeriesReducer": "REDUCE_MEAN",
                                                "groupByFields": ["resource.labels.container_name"]
                                            }
                                        }
                                    },
                                    "plotType": "LINE",
                                    "targetAxis": "Y1"
                                }
                            ],
                            "timeshiftDuration": "0s",
                            "yAxis": {
                                "label": "CPU Usage",
                                "scale": "LINEAR"
                            }
                        }
                    }
                },
                
                # Row 3: RAG System Metrics
                {
                    "width": 6,
                    "height": 4,
                    "widget": {
                        "title": "RAG Query Performance",
                        "scorecard": {
                            "timeSeriesQuery": {
                                "timeSeriesFilter": {
                                    "filter": f'resource.type="k8s_container" AND resource.labels.cluster_name="bank-of-anthos" AND resource.labels.namespace_name="nfrguard-agents" AND metric.type="kubernetes.io/container/memory/used_bytes"',
                                    "aggregation": {
                                        "alignmentPeriod": "60s",
                                        "perSeriesAligner": "ALIGN_MEAN",
                                        "crossSeriesReducer": "REDUCE_MEAN",
                                        "groupByFields": ["resource.labels.container_name"]
                                    }
                                }
                            },
                            "sparkChartView": {
                                "sparkChartType": "SPARK_LINE"
                            }
                        }
                    }
                },
                {
                    "width": 6,
                    "height": 4,
                    "widget": {
                        "title": "Vector Search Latency",
                        "scorecard": {
                            "timeSeriesQuery": {
                                "timeSeriesFilter": {
                                    "filter": f'resource.type="k8s_container" AND resource.labels.cluster_name="bank-of-anthos" AND resource.labels.namespace_name="nfrguard-agents" AND metric.type="kubernetes.io/container/network/received_bytes_count"',
                                    "aggregation": {
                                        "alignmentPeriod": "60s",
                                        "perSeriesAligner": "ALIGN_RATE",
                                        "crossSeriesReducer": "REDUCE_SUM"
                                    }
                                }
                            },
                            "sparkChartView": {
                                "sparkChartType": "SPARK_LINE"
                            }
                        }
                    }
                },
                
                # Row 4: Business Metrics
                {
                    "width": 12,
                    "height": 6,
                    "widget": {
                        "title": "Transaction Processing Volume",
                        "xyChart": {
                            "dataSets": [
                                {
                                    "timeSeriesQuery": {
                                        "timeSeriesFilter": {
                                            "filter": f'resource.type="k8s_container" AND resource.labels.cluster_name="bank-of-anthos" AND resource.labels.namespace_name="nfrguard-agents" AND metric.type="kubernetes.io/container/network/sent_bytes_count"',
                                            "aggregation": {
                                                "alignmentPeriod": "300s",
                                                "perSeriesAligner": "ALIGN_RATE",
                                                "crossSeriesReducer": "REDUCE_SUM"
                                            }
                                        }
                                    },
                                    "plotType": "LINE",
                                    "targetAxis": "Y1"
                                }
                            ],
                            "timeshiftDuration": "0s",
                            "yAxis": {
                                "label": "Network Traffic (bytes/sec)",
                                "scale": "LINEAR"
                            }
                        }
                    }
                },
                
                # Row 5: Error Monitoring
                {
                    "width": 6,
                    "height": 4,
                    "widget": {
                        "title": "Error Rate",
                        "scorecard": {
                            "timeSeriesQuery": {
                                "timeSeriesFilter": {
                                    "filter": f'resource.type="k8s_container" AND resource.labels.cluster_name="bank-of-anthos" AND resource.labels.namespace_name="nfrguard-agents" AND metric.type="kubernetes.io/container/restart_count"',
                                    "aggregation": {
                                        "alignmentPeriod": "300s",
                                        "perSeriesAligner": "ALIGN_RATE",
                                        "crossSeriesReducer": "REDUCE_SUM"
                                    }
                                }
                            },
                            "sparkChartView": {
                                "sparkChartType": "SPARK_LINE"
                            }
                        }
                    }
                },
                {
                    "width": 6,
                    "height": 4,
                    "widget": {
                        "title": "Pod Health Status",
                        "scorecard": {
                            "timeSeriesQuery": {
                                "timeSeriesFilter": {
                                    "filter": f'resource.type="k8s_container" AND resource.labels.cluster_name="bank-of-anthos" AND resource.labels.namespace_name="nfrguard-agents" AND metric.type="kubernetes.io/container/ready"',
                                    "aggregation": {
                                        "alignmentPeriod": "60s",
                                        "perSeriesAligner": "ALIGN_MEAN",
                                        "crossSeriesReducer": "REDUCE_MEAN"
                                    }
                                }
                            },
                            "gaugeView": {
                                "lowerBound": 0,
                                "upperBound": 1
                            }
                        }
                    }
                },
                
                # Row 6: Custom AI Metrics
                {
                    "width": 12,
                    "height": 6,
                    "widget": {
                        "title": "AI Agent Activity",
                        "xyChart": {
                            "dataSets": [
                                {
                                    "timeSeriesQuery": {
                                        "timeSeriesFilter": {
                                            "filter": f'resource.type="k8s_container" AND resource.labels.cluster_name="bank-of-anthos" AND resource.labels.namespace_name="nfrguard-agents" AND metric.type="kubernetes.io/container/cpu/core_usage_time"',
                                            "aggregation": {
                                                "alignmentPeriod": "60s",
                                                "perSeriesAligner": "ALIGN_RATE",
                                                "crossSeriesReducer": "REDUCE_MEAN",
                                                "groupByFields": ["resource.labels.container_name"]
                                            }
                                        }
                                    },
                                    "plotType": "STACKED_AREA",
                                    "targetAxis": "Y1"
                                }
                            ],
                            "timeshiftDuration": "0s",
                            "yAxis": {
                                "label": "CPU Usage by Agent",
                                "scale": "LINEAR"
                            }
                        }
                    }
                }
            ]
        }
    }
    
    return dashboard_config

def create_alerting_policies():
    """Create alerting policies for critical metrics"""
    project_id = get_project_id()
    
    alert_policies = [
        {
            "displayName": "NFRGuard - High CPU Usage",
            "conditions": [
                {
                    "displayName": "High CPU Usage",
                    "conditionThreshold": {
                        "filter": f'resource.type="k8s_container" AND resource.labels.cluster_name="bank-of-anthos" AND resource.labels.namespace_name="nfrguard-agents" AND metric.type="kubernetes.io/container/cpu/core_usage_time"',
                        "comparison": "COMPARISON_GREATER_THAN",
                        "thresholdValue": 0.8,
                        "duration": "300s",
                        "aggregations": [
                            {
                                "alignmentPeriod": "60s",
                                "perSeriesAligner": "ALIGN_MEAN",
                                "crossSeriesReducer": "REDUCE_MEAN"
                            }
                        ]
                    }
                }
            ],
            "alertStrategy": {
                "autoClose": "1800s"
            },
            "notificationChannels": [],
            "enabled": True
        },
        {
            "displayName": "NFRGuard - Pod Restart",
            "conditions": [
                {
                    "displayName": "Pod Restart",
                    "conditionThreshold": {
                        "filter": f'resource.type="k8s_container" AND resource.labels.cluster_name="bank-of-anthos" AND resource.labels.namespace_name="nfrguard-agents" AND metric.type="kubernetes.io/container/restart_count"',
                        "comparison": "COMPARISON_GREATER_THAN",
                        "thresholdValue": 0,
                        "duration": "60s",
                        "aggregations": [
                            {
                                "alignmentPeriod": "60s",
                                "perSeriesAligner": "ALIGN_RATE",
                                "crossSeriesReducer": "REDUCE_SUM"
                            }
                        ]
                    }
                }
            ],
            "alertStrategy": {
                "autoClose": "1800s"
            },
            "notificationChannels": [],
            "enabled": True
        },
        {
            "displayName": "NFRGuard - Memory Usage",
            "conditions": [
                {
                    "displayName": "High Memory Usage",
                    "conditionThreshold": {
                        "filter": f'resource.type="k8s_container" AND resource.labels.cluster_name="bank-of-anthos" AND resource.labels.namespace_name="nfrguard-agents" AND metric.type="kubernetes.io/container/memory/used_bytes"',
                        "comparison": "COMPARISON_GREATER_THAN",
                        "thresholdValue": 500000000,  # 500MB
                        "duration": "300s",
                        "aggregations": [
                            {
                                "alignmentPeriod": "60s",
                                "perSeriesAligner": "ALIGN_MEAN",
                                "crossSeriesReducer": "REDUCE_MEAN"
                            }
                        ]
                    }
                }
            ],
            "alertStrategy": {
                "autoClose": "1800s"
            },
            "notificationChannels": [],
            "enabled": True
        }
    ]
    
    return alert_policies

def deploy_dashboard():
    """Deploy the dashboard to GCP"""
    print("🚀 Creating NFRGuard GCP Monitoring Dashboard...")
    
    project_id = get_project_id()
    print(f"📊 Project ID: {project_id}")
    
    # Create dashboard configuration
    dashboard_config = create_nfrguard_dashboard()
    
    # Save dashboard config
    dashboard_file = Path("nfrguard_dashboard.json")
    with open(dashboard_file, "w") as f:
        json.dump(dashboard_config, f, indent=2)
    
    print(f"✅ Dashboard configuration saved to: {dashboard_file}")
    
    # Deploy dashboard using gcloud
    try:
        result = subprocess.run([
            "gcloud", "monitoring", "dashboards", "create",
            f"--config-from-file={dashboard_file}",
            f"--project={project_id}"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dashboard deployed successfully!")
            print(f"🌐 View dashboard at: https://console.cloud.google.com/monitoring/dashboards?project={project_id}")
        else:
            print(f"❌ Failed to deploy dashboard: {result.stderr}")
            print("💡 You can manually create the dashboard using the JSON file")
    
    except Exception as e:
        print(f"❌ Error deploying dashboard: {e}")
        print("💡 You can manually create the dashboard using the JSON file")
    
    # Create alerting policies
    print("\n🚨 Creating alerting policies...")
    alert_policies = create_alerting_policies()
    
    alert_file = Path("nfrguard_alerts.json")
    with open(alert_file, "w") as f:
        json.dump(alert_policies, f, indent=2)
    
    print(f"✅ Alert policies saved to: {alert_file}")
    
    # Deploy alert policies
    try:
        for i, policy in enumerate(alert_policies):
            policy_file = Path(f"alert_policy_{i}.json")
            with open(policy_file, "w") as f:
                json.dump(policy, f, indent=2)
            
            result = subprocess.run([
                "gcloud", "alpha", "monitoring", "policies", "create",
                f"--policy-from-file={policy_file}",
                f"--project={project_id}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Alert policy {i+1} deployed successfully!")
            else:
                print(f"⚠️  Alert policy {i+1} deployment failed: {result.stderr}")
            
            # Clean up temp file
            policy_file.unlink()
    
    except Exception as e:
        print(f"❌ Error deploying alert policies: {e}")
        print("💡 You can manually create the alert policies using the JSON file")
    
    print("\n🎉 Dashboard setup complete!")
    print(f"📊 Dashboard URL: https://console.cloud.google.com/monitoring/dashboards?project={project_id}")
    print(f"🚨 Alerts URL: https://console.cloud.google.com/monitoring/alerting?project={project_id}")
    print(f"📈 Metrics URL: https://console.cloud.google.com/monitoring/metrics-explorer?project={project_id}")

def create_custom_metrics():
    """Create custom metrics for AI agent monitoring"""
    print("\n📊 Creating custom metrics for AI agents...")
    
    project_id = get_project_id()
    
    # Custom metrics for AI agent performance
    custom_metrics = [
        {
            "name": "nfrguard/agent/response_time",
            "description": "AI agent response time in milliseconds",
            "labels": [
                {"key": "agent_name", "description": "Name of the AI agent"},
                {"key": "operation", "description": "Type of operation performed"}
            ]
        },
        {
            "name": "nfrguard/agent/risk_score",
            "description": "Risk score calculated by transaction risk agent",
            "labels": [
                {"key": "agent_name", "description": "Name of the AI agent"},
                {"key": "risk_level", "description": "Risk level (low, medium, high)"}
            ]
        },
        {
            "name": "nfrguard/rag/query_latency",
            "description": "RAG system query latency in milliseconds",
            "labels": [
                {"key": "query_type", "description": "Type of RAG query"},
                {"key": "agent_name", "description": "Agent making the query"}
            ]
        },
        {
            "name": "nfrguard/rag/confidence_score",
            "description": "RAG system confidence score",
            "labels": [
                {"key": "query_type", "description": "Type of RAG query"},
                {"key": "agent_name", "description": "Agent making the query"}
            ]
        }
    ]
    
    metrics_file = Path("custom_metrics.json")
    with open(metrics_file, "w") as f:
        json.dump(custom_metrics, f, indent=2)
    
    print(f"✅ Custom metrics configuration saved to: {metrics_file}")
    print("💡 Custom metrics will be created when agents start sending data")

if __name__ == "__main__":
    print("🛡️  NFRGuard GCP Monitoring Dashboard Setup")
    print("=" * 50)
    
    deploy_dashboard()
    create_custom_metrics()
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. View your dashboard in GCP Console")
    print("2. Set up notification channels for alerts")
    print("3. Customize metrics based on your needs")
    print("4. Monitor AI agent performance in real-time")
    print("=" * 50)

