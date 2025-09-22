# agents/customer_sentiment_agent/agent.py
from google.adk.agents import Agent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.messaging import publish

def analyze_sentiment(message: dict) -> dict:
    """Analyze customer message sentiment and flag trending issues."""
    content = message.get("content", "").lower()
    customer_id = message.get("customer_id", "unknown")
    
    # Simple sentiment analysis keywords
    negative_words = ["angry", "frustrated", "disappointed", "terrible", "awful", "hate", "problem", "issue", "bug", "error"]
    positive_words = ["happy", "great", "excellent", "love", "amazing", "perfect", "thank", "good", "satisfied"]
    
    negative_count = sum(1 for word in negative_words if word in content)
    positive_count = sum(1 for word in positive_words if word in content)
    
    # Determine sentiment
    if negative_count > positive_count:
        sentiment = "negative"
        severity = "high" if negative_count > 3 else "medium"
    elif positive_count > negative_count:
        sentiment = "positive"
        severity = "low"
    else:
        sentiment = "neutral"
        severity = "low"
    
    # Flag trending issues
    if sentiment == "negative" and severity in ["high", "medium"]:
        publish("ops.alert", {
            "event_type": "ops.alert",
            "customer_id": customer_id,
            "sentiment": sentiment,
            "severity": severity,
            "keywords": [word for word in negative_words if word in content],
            "detected_by": "customer_sentiment_agent_v1"
        })
    
    return {
        "customer_id": customer_id,
        "sentiment": sentiment,
        "severity": severity,
        "negative_keywords": negative_count,
        "positive_keywords": positive_count
    }

root_agent = Agent(
    name="customer_sentiment_agent",
    model="gemini-2.5-flash",
    description="Analyzes customer messages for sentiment and trending issues",
    instruction="Process customer messages and flag negative sentiment for ops review",
    tools=[analyze_sentiment],
)