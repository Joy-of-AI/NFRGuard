# agents/common/messaging.py
import json
import os
import requests
from typing import Dict

# Placeholder publisher: replace with real Pub/Sub or NATS client.
def publish(topic: str, message: Dict):
    """Publish an event. Replace body with actual broker client call."""
    payload = json.dumps(message)
    print(f"[PUB] topic={topic} payload={payload}")
    # if you use HTTP webhook for testing, you can post to a local endpoint:
    broker_url = os.getenv("LOCAL_BROKER_URL")
    if broker_url:
        requests.post(broker_url + f"/topics/{topic}", json=message)
