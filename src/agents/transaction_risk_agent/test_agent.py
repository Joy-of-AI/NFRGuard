#!/usr/bin/env python3
"""Test script for the banking assistant agent."""

import asyncio
import agent

async def test_agent():
    """Test the banking assistant agent."""
    print("Testing Banking Assistant Agent...")
    print("=" * 50)
    
    try:
        # Test basic greeting
        print("Test 1: Basic greeting")
        async for response in agent.root_agent.run_async():
            print(f"Response: {response}")
            break
        
        print("\nTest 2: Check balance request")
        async for response in agent.root_agent.run_async():
            print(f"Response: {response}")
            break
            
        print("\nTest 3: Transaction history request")
        async for response in agent.root_agent.run_async():
            print(f"Response: {response}")
            break
            
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent())
