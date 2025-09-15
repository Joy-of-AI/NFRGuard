"""Simple test agent for ADK."""

import os
from google.adk.agents import Agent

def hello_world(name: str = "World") -> str:
    """Say hello to someone.
    
    Args:
        name: The name to greet
        
    Returns:
        A greeting message
    """
    return f"Hello, {name}! This is a test agent response."

def add_numbers(a: float, b: float) -> float:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The sum of a and b
    """
    return a + b

# Create the root agent
root_agent = Agent(
    name="test_agent",
    model="gemini-1.5-flash",
    description="A simple test agent for ADK functionality testing",
    instruction="You are a helpful test agent. You can greet people and perform simple math operations.",
    tools=[hello_world, add_numbers],
)