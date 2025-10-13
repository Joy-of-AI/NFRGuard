#!/usr/bin/env python3
"""
Script to add HTTP server functionality to all agent files
"""
import os
import re

def add_http_server_to_agent(agent_file_path):
    """Add HTTP server code to an agent file"""
    
    # Read the current file
    with open(agent_file_path, 'r') as f:
        content = f.read()
    
    # Check if HTTP server code already exists
    if 'HTTPServer' in content:
        print(f"HTTP server already exists in {agent_file_path}")
        return
    
    # Extract agent name from file path
    agent_name = os.path.basename(os.path.dirname(agent_file_path))
    
    # Create the HTTP server code
    http_server_code = f'''

# Simple HTTP server to keep the agent running
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class AgentHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {{"status": "healthy", "agent": "{agent_name}"}}
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
                result = {{"response": response}}
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error = {{"error": str(e)}}
                self.wfile.write(json.dumps(error).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8080), AgentHandler)
    print("{agent_name} Agent running on port 8080...")
    server.serve_forever()
'''
    
    # Add the HTTP server code to the end of the file
    new_content = content + http_server_code
    
    # Write the updated content back to the file
    with open(agent_file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Added HTTP server to {agent_file_path}")

def main():
    """Main function to update all agent files"""
    agents_dir = "."
    agent_dirs = [
        "compliance_agent",
        "customer_sentiment_agent", 
        "data_privacy_agent",
        "knowledge_agent",
        "resilience_agent",
        "transaction_risk_agent"
    ]
    
    for agent_dir in agent_dirs:
        agent_file = os.path.join(agent_dir, "agent.py")
        if os.path.exists(agent_file):
            add_http_server_to_agent(agent_file)
        else:
            print(f"Agent file not found: {agent_file}")

if __name__ == "__main__":
    main()

