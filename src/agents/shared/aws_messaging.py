#!/usr/bin/env python3
"""
AWS EventBridge Messaging System
Provides event-driven agent communication using AWS EventBridge and SNS
Implements publish/subscribe pattern for loosely coupled agent coordination
"""

import os
import json
import logging
import boto3
from typing import Dict, Any, Callable, Optional
from datetime import datetime
import threading
from queue import Queue, Empty

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSMessaging:
    """AWS EventBridge messaging system for agent communication"""
    
    def __init__(self, region: str = None, event_bus_name: str = None):
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.event_bus_name = event_bus_name or os.getenv("EVENT_BUS_NAME", "nfrguard-event-bus")
        self.subscribers = {}
        self.local_queue = Queue()
        self.running = False
        
        # Initialize EventBridge client
        try:
            self.eventbridge = boto3.client('events', region_name=self.region)
            logger.info(f"EventBridge client initialized in {self.region}")
        except Exception as e:
            logger.error(f"Failed to initialize EventBridge client: {e}")
            raise
        
        # Initialize SNS client for fallback
        try:
            self.sns = boto3.client('sns', region_name=self.region)
            logger.info("SNS client initialized for fallback messaging")
        except Exception as e:
            logger.warning(f"SNS client initialization failed: {e}")
            self.sns = None
        
        # Start local message processor
        self.start_local_processor()
    
    def publish(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Publish an event to EventBridge"""
        try:
            # Prepare event entry
            event_entry = {
                'Source': 'nfrguard.agents',
                'DetailType': event_type,
                'Detail': json.dumps(event_data),
                'EventBusName': self.event_bus_name,
                'Time': datetime.now()
            }
            
            # Publish to EventBridge
            response = self.eventbridge.put_events(
                Entries=[event_entry]
            )
            
            if response['FailedEntryCount'] > 0:
                logger.error(f"Failed to publish event {event_type}: {response['Entries'][0].get('ErrorMessage', 'Unknown error')}")
                return False
            
            logger.info(f"Published event {event_type} to EventBridge")
            
            # Also publish locally for immediate processing
            self._publish_local(event_type, event_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error publishing event {event_type}: {e}")
            # Fallback to SNS if available
            if self.sns:
                return self._publish_sns(event_type, event_data)
            return False
    
    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], Any]) -> bool:
        """Subscribe to an event type"""
        try:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            
            self.subscribers[event_type].append(handler)
            logger.info(f"Subscribed to event type: {event_type}")
            
            # Create EventBridge rule if it doesn't exist
            self._ensure_rule_exists(event_type)
            
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to {event_type}: {e}")
            return False
    
    def _publish_local(self, event_type: str, event_data: Dict[str, Any]):
        """Publish event to local queue for immediate processing"""
        self.local_queue.put({
            'event_type': event_type,
            'event_data': event_data,
            'timestamp': datetime.now()
        })
    
    def _publish_sns(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Fallback: publish to SNS topic"""
        try:
            topic_arn = f"arn:aws:sns:{self.region}:{os.getenv('AWS_ACCOUNT_ID', '')}:{event_type}"
            
            self.sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps(event_data),
                Subject=f"NFRGuard Event: {event_type}"
            )
            
            logger.info(f"Published event {event_type} to SNS fallback")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing to SNS: {e}")
            return False
    
    def _ensure_rule_exists(self, event_type: str):
        """Ensure EventBridge rule exists for event type"""
        try:
            rule_name = f"nfrguard-{event_type.replace('.', '-')}"
            
            # Check if rule exists
            try:
                self.eventbridge.describe_rule(Name=rule_name)
                logger.info(f"EventBridge rule {rule_name} already exists")
                return
            except self.eventbridge.exceptions.ResourceNotFoundException:
                pass
            
            # Create rule
            self.eventbridge.put_rule(
                Name=rule_name,
                EventPattern=json.dumps({
                    "source": ["nfrguard.agents"],
                    "detail-type": [event_type]
                }),
                State='ENABLED',
                Description=f"Rule for {event_type} events"
            )
            
            logger.info(f"Created EventBridge rule: {rule_name}")
            
        except Exception as e:
            logger.error(f"Error ensuring rule exists for {event_type}: {e}")
    
    def start_local_processor(self):
        """Start local message processor thread"""
        self.running = True
        self.processor_thread = threading.Thread(target=self._process_local_messages, daemon=True)
        self.processor_thread.start()
        logger.info("Started local message processor")
    
    def stop_local_processor(self):
        """Stop local message processor"""
        self.running = False
        if hasattr(self, 'processor_thread'):
            self.processor_thread.join(timeout=5)
        logger.info("Stopped local message processor")
    
    def _process_local_messages(self):
        """Process messages from local queue"""
        while self.running:
            try:
                # Get message with timeout
                message = self.local_queue.get(timeout=1.0)
                
                event_type = message['event_type']
                event_data = message['event_data']
                
                # Call all subscribers for this event type
                if event_type in self.subscribers:
                    for handler in self.subscribers[event_type]:
                        try:
                            handler(event_data)
                        except Exception as e:
                            logger.error(f"Error in event handler for {event_type}: {e}")
                
                self.local_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing local message: {e}")
    
    def create_sns_topics(self):
        """Create SNS topics for all event types"""
        if not self.sns:
            logger.warning("SNS client not available, skipping topic creation")
            return
        
        event_types = [
            "transaction.created",
            "risk.flagged", 
            "compliance.action",
            "resilience.test",
            "sentiment.analysis",
            "privacy.violation",
            "knowledge.alert",
            "ops.alert"
        ]
        
        for event_type in event_types:
            try:
                topic_name = f"nfrguard-{event_type.replace('.', '-')}"
                response = self.sns.create_topic(Name=topic_name)
                logger.info(f"Created SNS topic: {topic_name}")
            except Exception as e:
                logger.error(f"Error creating SNS topic {event_type}: {e}")

# Global messaging instance
_messaging_instance = None

def get_messaging() -> AWSMessaging:
    """Get global messaging instance"""
    global _messaging_instance
    if _messaging_instance is None:
        _messaging_instance = AWSMessaging()
    return _messaging_instance

def publish(event_type: str, event_data: Dict[str, Any]) -> bool:
    """Publish an event (global function)"""
    return get_messaging().publish(event_type, event_data)

def subscribe(event_type: str, handler: Callable[[Dict[str, Any]], Any]) -> bool:
    """Subscribe to an event type (global function)"""
    return get_messaging().subscribe(event_type, handler)

# Backward compatibility aliases
def publish_local(event_type: str, event_data: Dict[str, Any]) -> bool:
    """Publish event locally only (for testing)"""
    messaging = get_messaging()
    messaging._publish_local(event_type, event_data)
    return True

def get_subscribers() -> Dict[str, list]:
    """Get all subscribers (for testing)"""
    return get_messaging().subscribers

# Example usage and testing
if __name__ == "__main__":
    def test_handler(event_data):
        print(f"Received event: {event_data}")
    
    # Test messaging system
    messaging = AWSMessaging()
    
    # Subscribe to test event
    messaging.subscribe("test.event", test_handler)
    
    # Publish test event
    messaging.publish("test.event", {
        "message": "Hello from AWS messaging!",
        "timestamp": datetime.now().isoformat()
    })
    
    # Wait for processing
    import time
    time.sleep(2)
    
    # Cleanup
    messaging.stop_local_processor()

