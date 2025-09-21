#!/bin/bash
# NFRGuard AI Agent Monitoring Setup Script
# Sets up Google Cloud Monitoring for Bank of Anthos + NFRGuard agents

echo "🛡️ Setting up NFRGuard AI Agent Monitoring..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ Error: kubectl not found. Please install kubectl."
    exit 1
fi

# Get current project
PROJECT_ID=$(gcloud config get-value project)
echo "📊 Project ID: $PROJECT_ID"

# Enable required services
echo "🔧 Enabling Google Cloud services..."
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Test the monitoring system
echo "🧪 Testing monitoring system..."
python -c "
from agent_metrics import AgentMetrics
import time

print('Testing Google Cloud Monitoring connection...')
try:
    metrics = AgentMetrics('$PROJECT_ID')
    
    # Test metrics
    metrics.track_transaction_risk_agent(0.95, 50000.0, 0.1)
    metrics.track_compliance_agent('AUSTRAC', False, 0.05)
    metrics.track_sentiment_agent('NEGATIVE', 0.8, 0.15)
    
    print('✅ Metrics sent successfully!')
    print('📊 Check your Google Cloud Monitoring dashboard:')
    print('   https://console.cloud.google.com/monitoring?project=$PROJECT_ID')
    
except Exception as e:
    print(f'❌ Error: {e}')
    print('Make sure you have the correct permissions and project ID.')
"

# Create monitoring dashboard
echo "📊 Creating monitoring dashboard..."
cat > dashboard_config.json << EOF
{
  "displayName": "NFRGuard AI Agents Dashboard",
  "mosaicLayout": {
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Transaction Risk Scores",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "metric.type=\"custom.googleapis.com/nfrguard/transaction_risk_agent/risk_assessment\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_MEAN",
                      "crossSeriesReducer": "REDUCE_MEAN"
                    }
                  }
                },
                "plotType": "LINE",
                "targetAxis": "Y1"
              }
            ]
          }
        }
      },
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Compliance Check Success Rate",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "metric.type=\"custom.googleapis.com/nfrguard/compliance_agent/compliance_check\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_RATE",
                      "crossSeriesReducer": "REDUCE_MEAN"
                    }
                  }
                },
                "plotType": "LINE",
                "targetAxis": "Y1"
              }
            ]
          }
        }
      }
    ]
  }
}
EOF

echo "✅ Monitoring setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Run the monitored demo: python demo/monitored_database_monitor.py"
echo "2. Check metrics in Google Cloud Console:"
echo "   https://console.cloud.google.com/monitoring?project=$PROJECT_ID"
echo "3. Set up alerting policies:"
echo "   gcloud alpha monitoring policies create --policy-from-file=alert_policies.yaml"
echo ""
echo "📊 Available metrics:"
echo "   - Transaction risk scores"
echo "   - Compliance check success rates"
echo "   - Agent processing times"
echo "   - Sentiment analysis results"
echo "   - Privacy violation detections"
echo "   - Knowledge agent report generation"
echo "   - Banking assistant response times"
