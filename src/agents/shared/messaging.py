# agents/shared/messaging.py
import json
import os
import requests
import threading
import time
from typing import Dict, Callable, List, Optional
from collections import defaultdict

# -----------------------------
# Configuration (env-driven)
# -----------------------------
PERSIST_PATH = os.getenv("MSG_PERSIST_PATH", "./.msg_events.jsonl")
DLQ_PATH = os.getenv("MSG_DLQ_PATH", "./.msg_dlq.jsonl")
MAX_RETRIES = int(os.getenv("MSG_MAX_RETRIES", "3"))
RETRY_DELAY_SEC = float(os.getenv("MSG_RETRY_DELAY_SEC", "0.05"))

# Back-compat var for simple HTTP broker
HTTP_BROKER_URL = os.getenv("LOCAL_BROKER_URL") or os.getenv("PUBSUB_BROKER_URL")

# Global subscription registry
_subscribers: Dict[str, List[Callable]] = defaultdict(list)
_lock = threading.Lock()

# -----------------------------
# Persistence helpers
# -----------------------------

def _append_jsonl(path: str, record: Dict) -> None:
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        print(f"[ERROR] Failed to write to {path}: {e}")


def _persist_event(topic: str, message: Dict) -> None:
    _append_jsonl(PERSIST_PATH, {
        "ts": time.time(),
        "topic": topic,
        "message": message,
    })


def _send_to_dlq(topic: str, message: Dict, last_error: Optional[str]) -> None:
    _append_jsonl(DLQ_PATH, {
        "ts": time.time(),
        "topic": topic,
        "message": message,
        "error": last_error,
    })

# -----------------------------
# External broker adapter (minimal HTTP)
# -----------------------------

def _publish_external(topic: str, message: Dict) -> None:
    if not HTTP_BROKER_URL:
        return
    try:
        requests.post(HTTP_BROKER_URL + f"/topics/{topic}", json=message, timeout=2)
    except Exception as e:
        print(f"[ERROR] Failed to publish to external broker: {e}")

# -----------------------------
# Core API
# -----------------------------

def publish(topic: str, message: Dict) -> None:
    """Publish an event with persistence, local fan-out, and optional external broker.

    Handlers may optionally return True (ACK) or False (NACK). Exceptions are treated as NACK.
    On NACK, the handler is retried up to MAX_RETRIES, then the message is sent to DLQ.
    """
    payload = json.dumps(message)
    print(f"[PUB] topic={topic} payload={payload}")

    # Persist for audit/replay
    _persist_event(topic, message)

    # Notify local subscribers with ACK/NACK and retries
    with _lock:
        handlers = list(_subscribers[topic])

    for handler in handlers:
        attempts = 0
        last_error: Optional[str] = None
        while attempts <= MAX_RETRIES:
            try:
                result = handler(message)
                # If handler explicitly returns False, treat as NACK
                if result is False:
                    attempts += 1
                    if attempts <= MAX_RETRIES:
                        time.sleep(RETRY_DELAY_SEC)
                        continue
                    last_error = "handler returned NACK"
                # ACK on True or None (backward compatible)
                break
            except Exception as e:
                last_error = str(e)
                attempts += 1
                if attempts <= MAX_RETRIES:
                    time.sleep(RETRY_DELAY_SEC)
                    continue
        # Exhausted retries
        if attempts > MAX_RETRIES and last_error:
            print(f"[DLQ] topic={topic} reason={last_error}")
            _send_to_dlq(topic, message, last_error)

    # External broker (if configured)
    _publish_external(topic, message)


def subscribe(topic: str, handler_func: Callable[[Dict], Optional[bool]]):
    """Subscribe to events on a topic.

    Handler signature: handler(dict) -> Optional[bool]
      - return True/None for ACK (processed)
      - return False for NACK (will be retried)
      - raise Exception to signal failure (will be retried)
    """
    with _lock:
        _subscribers[topic].append(handler_func)
    print(f"[SUB] Subscribed to topic: {topic}")


def unsubscribe(topic: str, handler_func: Callable[[Dict], Optional[bool]]):
    """Unsubscribe from events on a topic."""
    with _lock:
        if handler_func in _subscribers[topic]:
            _subscribers[topic].remove(handler_func)
    print(f"[UNSUB] Unsubscribed from topic: {topic}")


def get_subscribers(topic: str) -> List[Callable]:
    """Get list of subscribers for a topic."""
    with _lock:
        return _subscribers[topic].copy()


def list_topics() -> List[str]:
    """List all active topics."""
    with _lock:
        return list(_subscribers.keys())


def clear_subscriptions():
    """Clear all subscriptions (useful for testing)."""
    with _lock:
        _subscribers.clear()
    print("[CLEAR] All subscriptions cleared")
