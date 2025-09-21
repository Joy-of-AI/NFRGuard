#!/usr/bin/env python3
"""
Test script for enhanced messaging functionality
Tests publish/subscribe pattern and agent communication
"""

import sys
import os
import time
import threading
from typing import Dict

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))
from shared.messaging import publish, subscribe, unsubscribe, list_topics, clear_subscriptions

def test_basic_publish_subscribe():
    """Test basic publish/subscribe functionality"""
    print("\n=== Testing Basic Publish/Subscribe ===")
    
    # Clear any existing subscriptions
    clear_subscriptions()
    
    # Test data
    test_events = []
    
    def test_handler(event: Dict):
        test_events.append(event)
        print(f"[TEST HANDLER] Received: {event}")
    
    # Subscribe to test topic
    subscribe("test.topic", test_handler)
    
    # Publish test events
    test_message1 = {"type": "test", "id": 1, "message": "Hello World"}
    test_message2 = {"type": "test", "id": 2, "message": "Agent Communication"}
    
    publish("test.topic", test_message1)
    publish("test.topic", test_message2)
    
    # Wait for async processing
    time.sleep(0.1)
    
    # Verify results
    assert len(test_events) == 2, f"Expected 2 events, got {len(test_events)}"
    assert test_events[0]["id"] == 1, "First event ID mismatch"
    assert test_events[1]["id"] == 2, "Second event ID mismatch"
    
    print("✅ Basic publish/subscribe test passed!")
    return True

def test_multiple_subscribers():
    """Test multiple subscribers on same topic"""
    print("\n=== Testing Multiple Subscribers ===")
    
    clear_subscriptions()
    
    handler1_events = []
    handler2_events = []
    
    def handler1(event: Dict):
        handler1_events.append(event)
        print(f"[HANDLER1] Received: {event}")
    
    def handler2(event: Dict):
        handler2_events.append(event)
        print(f"[HANDLER2] Received: {event}")
    
    # Subscribe both handlers
    subscribe("multi.topic", handler1)
    subscribe("multi.topic", handler2)
    
    # Publish event
    test_message = {"type": "multi", "id": 1, "message": "Multiple handlers"}
    publish("multi.topic", test_message)
    
    time.sleep(0.1)
    
    # Verify both handlers received the event
    assert len(handler1_events) == 1, f"Handler1 expected 1 event, got {len(handler1_events)}"
    assert len(handler2_events) == 1, f"Handler2 expected 1 event, got {len(handler2_events)}"
    
    print("✅ Multiple subscribers test passed!")
    return True

def test_unsubscribe():
    """Test unsubscribe functionality"""
    print("\n=== Testing Unsubscribe ===")
    
    clear_subscriptions()
    
    handler_events = []
    
    def test_handler(event: Dict):
        handler_events.append(event)
        print(f"[UNSUB TEST HANDLER] Received: {event}")
    
    # Subscribe
    subscribe("unsub.topic", test_handler)
    
    # Publish first event (should be received)
    publish("unsub.topic", {"id": 1, "message": "Before unsubscribe"})
    time.sleep(0.1)
    
    # Unsubscribe
    unsubscribe("unsub.topic", test_handler)
    
    # Publish second event (should NOT be received)
    publish("unsub.topic", {"id": 2, "message": "After unsubscribe"})
    time.sleep(0.1)
    
    # Verify only first event was received
    assert len(handler_events) == 1, f"Expected 1 event, got {len(handler_events)}"
    assert handler_events[0]["id"] == 1, "Wrong event received"
    
    print("✅ Unsubscribe test passed!")
    return True

def test_agent_communication_flow():
    """Test the complete agent communication flow"""
    print("\n=== Testing Agent Communication Flow ===")
    
    clear_subscriptions()
    
    # Simulate agent event handlers
    risk_events = []
    compliance_events = []
    resilience_events = []
    knowledge_events = []
    
    def risk_handler(event: Dict):
        risk_events.append(event)
        print(f"[RISK AGENT] Processing transaction: {event['transaction_id']}")
        # Simulate risk detection
        if event.get("amount", 0) > 10000:
            publish("risk.flagged", {
                "event_type": "risk.flagged",
                "transaction_id": event["transaction_id"],
                "score": 0.95,
                "reason": "high_amount",
                "detected_by": "transaction_risk_agent_v1"
            })
    
    def compliance_handler(event: Dict):
        compliance_events.append(event)
        print(f"[COMPLIANCE AGENT] Received risk event: {event['transaction_id']}")
        # Simulate compliance check
        action = "hold_and_report" if event.get("score", 0) > 0.8 else "monitor"
        publish("compliance.action", {
            "event_type": "compliance.action",
            "transaction_id": event["transaction_id"],
            "action": action,
            "rule": "AUSTRAC_threshold"
        })
    
    def resilience_handler(event: Dict):
        resilience_events.append(event)
        print(f"[RESILIENCE AGENT] Received compliance action: {event['action']}")
        # Simulate action execution
        if event["action"] == "hold_and_report":
            print(f"[RESILIENCE AGENT] Placing hold on transaction {event['transaction_id']}")
    
    def knowledge_handler(event: Dict):
        knowledge_events.append(event)
        print(f"[KNOWLEDGE AGENT] Creating alert for: {event}")
    
    # Set up subscriptions
    subscribe("transaction.created", risk_handler)
    subscribe("risk.flagged", compliance_handler)
    subscribe("compliance.action", resilience_handler)
    subscribe("risk.flagged", knowledge_handler)
    subscribe("compliance.action", knowledge_handler)
    
    # Simulate transaction flow
    print("\n--- Simulating Transaction Flow ---")
    
    # 1. Transaction created
    publish("transaction.created", {
        "transaction_id": "txn_12345",
        "amount": 15000,
        "from_account": "acc_001",
        "to_account": "acc_002",
        "timestamp": "2025-01-14T10:30:00Z"
    })
    
    time.sleep(0.2)  # Allow event propagation
    
    # Verify event flow
    assert len(risk_events) == 1, f"Risk agent should receive 1 event, got {len(risk_events)}"
    assert len(compliance_events) == 1, f"Compliance agent should receive 1 event, got {len(compliance_events)}"
    assert len(resilience_events) == 1, f"Resilience agent should receive 1 event, got {len(resilience_events)}"
    assert len(knowledge_events) == 2, f"Knowledge agent should receive 2 events, got {len(knowledge_events)}"
    
    print("✅ Agent communication flow test passed!")
    return True

def test_error_handling():
    """Test error handling in message processing"""
    print("\n=== Testing Error Handling ===")
    
    clear_subscriptions()
    
    def error_handler(event: Dict):
        raise Exception("Simulated handler error")
    
    def good_handler(event: Dict):
        print(f"[GOOD HANDLER] Received: {event}")
    
    # Subscribe both handlers
    subscribe("error.topic", error_handler)
    subscribe("error.topic", good_handler)
    
    # Publish event (should not crash despite error in one handler)
    publish("error.topic", {"id": 1, "message": "Test error handling"})
    
    time.sleep(0.1)
    
    print("✅ Error handling test passed!")
    return True

def test_topic_listing():
    """Test topic listing functionality"""
    print("\n=== Testing Topic Listing ===")
    
    clear_subscriptions()
    
    def dummy_handler(event: Dict):
        pass
    
    # Subscribe to multiple topics
    subscribe("topic1", dummy_handler)
    subscribe("topic2", dummy_handler)
    subscribe("topic3", dummy_handler)
    
    # List topics
    topics = list_topics()
    
    assert len(topics) == 3, f"Expected 3 topics, got {len(topics)}"
    assert "topic1" in topics, "topic1 not found"
    assert "topic2" in topics, "topic2 not found"
    assert "topic3" in topics, "topic3 not found"
    
    print("✅ Topic listing test passed!")
    return True

def test_ack_retry_success():
    """Handler NACKs twice then ACKs; should not hit DLQ and should be invoked 3 times."""
    print("\n=== Testing ACK/NACK Retry Success ===")

    clear_subscriptions()

    attempts = {"count": 0}

    def flaky_handler(event: Dict):
        attempts["count"] += 1
        print(f"[FLAKY] attempt={attempts['count']} event={event}")
        if attempts["count"] < 3:
            return False  # NACK
        return True  # ACK on third attempt

    subscribe("ack.topic", flaky_handler)

    publish("ack.topic", {"id": 1, "message": "test ack/nack"})
    time.sleep(0.2)

    assert attempts["count"] == 3, f"Expected 3 attempts, got {attempts['count']}"
    print("✅ ACK/NACK retry success test passed!")
    return True


def test_persistence_and_dlq():
    """Verify events are persisted and DLQ records on repeated failure."""
    print("\n=== Testing Persistence and DLQ ===")

    clear_subscriptions()

    # Clean up old files
    persist_path = os.getenv("MSG_PERSIST_PATH", "./.msg_events.jsonl")
    dlq_path = os.getenv("MSG_DLQ_PATH", "./.msg_dlq.jsonl")
    for p in [persist_path, dlq_path]:
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass

    # Always-failing handler to trigger DLQ
    def failing_handler(event: Dict):
        raise Exception("always fails")

    subscribe("dlq.topic", failing_handler)

    publish("dlq.topic", {"id": 99, "message": "should go to DLQ"})
    time.sleep(0.3)

    # Check persistence file has at least one line
    assert os.path.exists(persist_path), "Persistence file not created"
    with open(persist_path, "r", encoding="utf-8") as f:
        lines = [ln for ln in f if ln.strip()]
        assert any('"topic": "dlq.topic"' in ln for ln in lines), "Event not persisted"

    # Check DLQ file has the failing record
    assert os.path.exists(dlq_path), "DLQ file not created"
    with open(dlq_path, "r", encoding="utf-8") as f:
        dlq_lines = [ln for ln in f if ln.strip()]
        assert len(dlq_lines) >= 1, "DLQ should contain at least one record"

    print("✅ Persistence and DLQ test passed!")
    return True


def run_all_tests():
    """Run all messaging tests"""
    print("🚀 Starting Enhanced Messaging Tests")
    print("=" * 50)

    tests = [
        test_basic_publish_subscribe,
        test_multiple_subscribers,
        test_unsubscribe,
        test_agent_communication_flow,
        test_error_handling,
        test_topic_listing,
        test_ack_retry_success,
        test_persistence_and_dlq,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! Enhanced messaging is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
