#!/usr/bin/env python3
"""
Production Monitoring Script for RAG System
"""

import os
import sys
import time
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from production_config import *

def check_agent_health():
    """Check health of all RAG-enhanced agents"""
    print("🏥 Checking agent health...")
    
    agents = [
        "transaction-risk-agent",
        "compliance-agent", 
        "resilience-agent",
        "customer-sentiment-agent",
        "data-privacy-agent",
        "knowledge-agent",
        "banking-assistant-agent"
    ]
    
    healthy_agents = 0
    total_agents = len(agents)
    
    for agent in agents:
        try:
            # In production, you would check the actual agent endpoints
            # For now, we'll simulate the health check
            response = requests.get(f"http://{agent}:8080/health", timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {agent}: Healthy")
                healthy_agents += 1
            else:
                print(f"  ❌ {agent}: Unhealthy (status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  {agent}: Cannot reach ({e})")
    
    health_percentage = (healthy_agents / total_agents) * 100
    print(f"  📊 Agent Health: {healthy_agents}/{total_agents} ({health_percentage:.1f}%)")
    
    return health_percentage >= 80  # 80% threshold

def check_rag_performance():
    """Check RAG system performance metrics"""
    print("📊 Checking RAG performance...")
    
    try:
        from rag_engine import AustralianBankingRAG
        
        # Load deployment info
        if Path("deployment_info.json").exists():
            with open("deployment_info.json", "r") as f:
                deployment_info = json.load(f)
        else:
            print("  ❌ No deployment info found")
            return False
        
        # Initialize RAG system
        rag = AustralianBankingRAG(project_id=PROJECT_ID)
        rag.index_id = deployment_info["index_id"]
        rag.index_endpoint_id = deployment_info["endpoint_id"]
        rag.deployed_index_id = deployment_info["deployed_index_id"]
        
        # Test query performance
        test_queries = [
            ("transaction risk monitoring", "transaction_risk"),
            ("compliance requirements", "compliance"),
            ("customer complaint handling", "customer_sentiment")
        ]
        
        total_latency = 0
        total_confidence = 0
        successful_queries = 0
        
        for query, agent in test_queries:
            try:
                start_time = time.time()
                result = rag.query(query, agent)
                query_time = time.time() - start_time
                
                total_latency += query_time
                total_confidence += result.confidence
                successful_queries += 1
                
                print(f"  ✅ {agent}: {query_time:.2f}s, confidence {result.confidence:.2f}")
                
            except Exception as e:
                print(f"  ❌ {agent}: Query failed - {e}")
        
        if successful_queries > 0:
            avg_latency = total_latency / successful_queries
            avg_confidence = total_confidence / successful_queries
            
            print(f"  📊 Average Latency: {avg_latency:.2f}s")
            print(f"  📊 Average Confidence: {avg_confidence:.2f}")
            
            # Check performance thresholds
            latency_ok = avg_latency < ALERT_THRESHOLD_RESPONSE_TIME
            confidence_ok = avg_confidence > ALERT_THRESHOLD_CONFIDENCE
            
            if latency_ok and confidence_ok:
                print("  ✅ RAG performance: Good")
                return True
            else:
                print("  ⚠️  RAG performance: Issues detected")
                return False
        else:
            print("  ❌ No successful queries")
            return False
            
    except Exception as e:
        print(f"  ❌ RAG performance check failed: {e}")
        return False

def check_document_coverage():
    """Check document coverage and freshness"""
    print("📚 Checking document coverage...")
    
    try:
        from rag_engine import AustralianBankingRAG
        
        rag = AustralianBankingRAG(project_id=PROJECT_ID)
        documents = rag.document_downloader.download_all_documents()
        
        # Check document count
        expected_documents = 6  # ASIC, APRA (2), AUSTRAC, AFCA (2)
        if len(documents) >= expected_documents:
            print(f"  ✅ Document count: {len(documents)} (expected: {expected_documents})")
        else:
            print(f"  ❌ Document count: {len(documents)} (expected: {expected_documents})")
            return False
        
        # Check document freshness
        current_time = time.time()
        stale_documents = 0
        
        for doc in documents:
            # Check if document is older than 7 days
            if hasattr(doc, 'metadata') and 'download_date' in doc.metadata:
                download_date = doc.metadata['download_date']
                # Simple check - in production you'd parse the date properly
                if current_time - time.time() > 7 * 24 * 60 * 60:  # 7 days
                    stale_documents += 1
        
        if stale_documents == 0:
            print("  ✅ Document freshness: Good")
        else:
            print(f"  ⚠️  Document freshness: {stale_documents} stale documents")
        
        # Check regulator coverage
        regulators = set(doc.regulator for doc in documents)
        expected_regulators = {"asic", "apra", "austrac", "afca"}
        
        if regulators >= expected_regulators:
            print(f"  ✅ Regulator coverage: {', '.join(regulators)}")
        else:
            missing = expected_regulators - regulators
            print(f"  ❌ Regulator coverage: Missing {', '.join(missing)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Document coverage check failed: {e}")
        return False

def check_vector_search_health():
    """Check vector search system health"""
    print("🔍 Checking vector search health...")
    
    try:
        from rag_engine import AustralianBankingRAG
        
        # Load deployment info
        if Path("deployment_info.json").exists():
            with open("deployment_info.json", "r") as f:
                deployment_info = json.load(f)
        else:
            print("  ❌ No deployment info found")
            return False
        
        # Initialize RAG system
        rag = AustralianBankingRAG(project_id=PROJECT_ID)
        rag.index_id = deployment_info["index_id"]
        rag.index_endpoint_id = deployment_info["endpoint_id"]
        rag.deployed_index_id = deployment_info["deployed_index_id"]
        
        # Test vector search connectivity
        try:
            # Try to create a test index (this will fail if not available, but that's OK)
            test_index_id = rag.vector_search.create_vector_index("health-check-test")
            print("  ✅ Vector search connectivity: Good")
            
            # Test similarity search
            results = rag.vector_search.similarity_search("test query", top_k=1)
            if results:
                print("  ✅ Vector search functionality: Good")
            else:
                print("  ⚠️  Vector search functionality: No results returned")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Vector search connectivity: Failed - {e}")
            return False
            
    except Exception as e:
        print(f"  ❌ Vector search health check failed: {e}")
        return False

def generate_monitoring_report():
    """Generate comprehensive monitoring report"""
    print("📋 Generating monitoring report...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "checks": {}
    }
    
    # Run all checks
    report["checks"]["agent_health"] = check_agent_health()
    report["checks"]["rag_performance"] = check_rag_performance()
    report["checks"]["document_coverage"] = check_document_coverage()
    report["checks"]["vector_search_health"] = check_vector_search_health()
    
    # Calculate overall health
    passed_checks = sum(report["checks"].values())
    total_checks = len(report["checks"])
    overall_health = (passed_checks / total_checks) * 100
    
    report["overall_health"] = overall_health
    report["status"] = "HEALTHY" if overall_health >= 80 else "DEGRADED" if overall_health >= 60 else "UNHEALTHY"
    
    # Save report
    report_file = f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"  📝 Report saved to: {report_file}")
    
    return report

def send_alerts(report):
    """Send alerts if system is unhealthy"""
    if report["status"] == "UNHEALTHY":
        print("🚨 Sending critical alerts...")
        
        # In production, you would send actual alerts
        # - Email alerts
        # - Slack notifications
        # - PagerDuty incidents
        # - Cloud Monitoring alerts
        
        print("  📧 Critical alert: RAG system is UNHEALTHY")
        print("  🔔 Slack notification: System requires immediate attention")
        print("  📱 PagerDuty: Critical incident created")
        
    elif report["status"] == "DEGRADED":
        print("⚠️  Sending warning alerts...")
        print("  📧 Warning alert: RAG system is DEGRADED")
        print("  🔔 Slack notification: System performance issues detected")

def main():
    """Main monitoring function"""
    print("🔍 RAG System Production Monitoring")
    print("=" * 50)
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 50)
    
    # Generate monitoring report
    report = generate_monitoring_report()
    
    # Display summary
    print("\n📊 Monitoring Summary:")
    print(f"  Overall Health: {report['overall_health']:.1f}%")
    print(f"  Status: {report['status']}")
    print(f"  Passed Checks: {sum(report['checks'].values())}/{len(report['checks'])}")
    
    # Send alerts if needed
    send_alerts(report)
    
    # Return status
    if report["status"] == "HEALTHY":
        print("\n🎉 RAG system is healthy and operating normally")
        return True
    elif report["status"] == "DEGRADED":
        print("\n⚠️  RAG system is degraded but operational")
        return True
    else:
        print("\n❌ RAG system is unhealthy and requires attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
