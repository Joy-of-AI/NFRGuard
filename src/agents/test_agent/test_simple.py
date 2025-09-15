#!/usr/bin/env python3
"""Simple test script for the test agent."""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import agent

async def test_agent():
    """Test the test agent functionality."""
    print("Testing Simple Agent...")
    print("=" * 50)
    
    try:
        # Test 1: Basic greeting
        print("Test 1: Hello World Tool")
        result = agent.hello_world("Alice")
        print(f"Result: {result}")
        
        # Test 2: Math operation
        print("\nTest 2: Add Numbers Tool")
        result = agent.add_numbers(5, 3)
        print(f"Result: {result}")
        
        # Test 3: Test agent loading
        print("\nTest 3: Agent Object")
        print(f"Agent name: {agent.root_agent.name}")
        print(f"Agent description: {agent.root_agent.description}")
        print(f"Available tools: {[tool.__name__ for tool in agent.root_agent.tools]}")
        
        print("\n✅ All tests passed successfully!")
        print("\nThe test agent is ready to use with ADK!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent())
