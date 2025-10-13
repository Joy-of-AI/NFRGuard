# agents/customer_sentiment_agent/agent.py
import os
from shared.bedrock_agent import BedrockAgent
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

root_agent = BedrockAgent(
    name="customer_sentiment_agent",
    model=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
    description="Analyzes customer messages for sentiment and trending issues",
    instruction="Process customer messages and flag negative sentiment for ops review",
    tools=[analyze_sentiment],
)

# Simple HTTP server to keep the agent running
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class AgentHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "agent": "customer_sentiment_agent"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                message = data.get('message', '')
                response = root_agent.invoke(message)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                result = {"response": response}
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error = {"error": str(e)}
                self.wfile.write(json.dumps(error).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8080), AgentHandler)
    print("customer_sentiment_agent Agent running on port 8080...")
    server.serve_forever()
