#!/usr/bin/env python3
"""
AWS Bedrock Agent Wrapper
Replaces google.adk.agents.Agent with AWS Bedrock Runtime integration
"""

import os
import json
import logging
import boto3
from typing import List, Callable, Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    """Response from agent invocation"""
    content: str
    usage: Dict[str, Any]
    model_id: str
    timestamp: datetime

class BedrockAgent:
    """AWS Bedrock agent wrapper (replaces Google ADK Agent)"""
    
    def __init__(
        self,
        name: str,
        model: str = None,
        description: str = "",
        instruction: str = "",
        tools: List[Callable] = None,
        region: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        self.name = name
        self.model = model or os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
        self.description = description
        self.instruction = instruction
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tools = {tool.__name__: tool for tool in (tools or [])}
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        
        # Initialize Bedrock client
        try:
            self.bedrock_runtime = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.region
            )
            logger.info(f"Bedrock client initialized for {self.name} in {self.region}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
    
    def invoke(self, user_message: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Invoke the agent with a user message"""
        try:
            # Build the system prompt with instruction and available tools
            system_prompt = self._build_system_prompt(context)
            
            # Prepare request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": self.temperature,
            }
            
            # Add tools if available
            if self.tools:
                request_body["tools"] = self._format_tools_for_claude()
            
            # Call Bedrock
            logger.info(f"Invoking {self.name} with model {self.model}")
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract usage information
            usage = response_body.get('usage', {})
            
            return AgentResponse(
                content=response_body['content'][0]['text'],
                usage=usage,
                model_id=self.model,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error invoking {self.name}: {e}")
            raise
    
    def invoke_with_tools(self, user_message: str, max_iterations: int = 5) -> AgentResponse:
        """Invoke agent with tool calling capability"""
        try:
            # Build the system prompt
            system_prompt = self._build_system_prompt()
            
            # Prepare request with tools
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": self.temperature,
                "tools": self._format_tools_for_claude()
            }
            
            # Call Bedrock
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Handle tool calls if present
            if 'content' in response_body and len(response_body['content']) > 0:
                content = response_body['content'][0]
                if content.get('type') == 'tool_use':
                    # Execute the tool and return result
                    tool_result = self._execute_tool(content)
                    return self._handle_tool_result(tool_result, response_body)
            
            return AgentResponse(
                content=response_body['content'][0]['text'],
                usage=response_body.get('usage', {}),
                model_id=self.model,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error in tool invocation for {self.name}: {e}")
            raise
    
    def _build_system_prompt(self, context: Dict[str, Any] = None) -> str:
        """Build system prompt with instruction and tools"""
        prompt = f"{self.instruction}\n\n"
        
        if self.description:
            prompt += f"Description: {self.description}\n\n"
        
        if self.tools:
            prompt += "You have access to these tools:\n"
            for tool_name, tool_func in self.tools.items():
                prompt += f"- {tool_name}: {tool_func.__doc__ or 'No description available'}\n"
        
        if context:
            prompt += f"\nContext: {json.dumps(context, indent=2)}\n"
        
        return prompt
    
    def _format_tools_for_claude(self) -> List[Dict[str, Any]]:
        """Format tools for Claude's tool calling format"""
        tools = []
        for tool_name, tool_func in self.tools.items():
            # Get function signature and docstring
            import inspect
            sig = inspect.signature(tool_func)
            
            # Build parameters schema
            properties = {}
            required = []
            
            for param_name, param in sig.parameters.items():
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation == str:
                        param_type = "string"
                    elif param.annotation == int:
                        param_type = "integer"
                    elif param.annotation == float:
                        param_type = "number"
                    elif param.annotation == bool:
                        param_type = "boolean"
                    elif param.annotation == dict:
                        param_type = "object"
                    elif param.annotation == list:
                        param_type = "array"
                    else:
                        param_type = "string"
                else:
                    param_type = "string"
                
                properties[param_name] = {
                    "type": param_type,
                    "description": f"Parameter {param_name}"
                }
                
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)
            
            tool_def = {
                "name": tool_name,
                "description": tool_func.__doc__ or f"Tool: {tool_name}",
                "input_schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
            
            tools.append(tool_def)
        
        return tools
    
    def _execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call"""
        tool_name = tool_call['name']
        tool_input = tool_call['input']
        
        if tool_name not in self.tools:
            return {
                "error": f"Tool {tool_name} not found",
                "tool_call_id": tool_call['id']
            }
        
        try:
            tool_func = self.tools[tool_name]
            result = tool_func(**tool_input)
            return {
                "result": result,
                "tool_call_id": tool_call['id']
            }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "error": str(e),
                "tool_call_id": tool_call['id']
            }
    
    def _handle_tool_result(self, tool_result: Dict[str, Any], original_response: Dict[str, Any]) -> AgentResponse:
        """Handle tool execution result"""
        # For now, return the tool result as content
        # In a more sophisticated implementation, you might want to continue the conversation
        content = json.dumps(tool_result, indent=2)
        
        return AgentResponse(
            content=content,
            usage=original_response.get('usage', {}),
            model_id=self.model,
            timestamp=datetime.now()
        )
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using Bedrock Titan Embeddings"""
        try:
            embedding_model = os.getenv("BEDROCK_EMBEDDING_MODEL", "amazon.titan-embed-text-v2:0")
            
            body = json.dumps({"inputText": text})
            response = self.bedrock_runtime.invoke_model(
                modelId=embedding_model,
                body=body
            )
            response_body = json.loads(response['body'].read())
            return response_body['embedding']
            
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise

# Backward compatibility alias
Agent = BedrockAgent

# Factory function for creating agents
def create_agent(
    name: str,
    model: str = None,
    description: str = "",
    instruction: str = "",
    tools: List[Callable] = None,
    **kwargs
) -> BedrockAgent:
    """Factory function to create BedrockAgent instances"""
    return BedrockAgent(
        name=name,
        model=model,
        description=description,
        instruction=instruction,
        tools=tools,
        **kwargs
    )

# Example usage and testing
if __name__ == "__main__":
    def test_tool(amount: float, description: str) -> dict:
        """Test tool for agent"""
        return {
            "status": "success",
            "amount": amount,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
    
    # Create agent
    agent = BedrockAgent(
        name="test_agent",
        description="Test agent for Bedrock integration",
        instruction="You are a helpful test agent. Use the available tools when needed.",
        tools=[test_tool]
    )
    
    # Test basic invocation
    try:
        response = agent.invoke("Hello, can you help me test a transaction for $100?")
        print(f"Agent response: {response.content}")
        print(f"Usage: {response.usage}")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure AWS credentials are configured and Bedrock model access is granted")

