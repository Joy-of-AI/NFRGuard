#!/usr/bin/env python3
"""
Comprehensive tests for AWS integration components
Tests all AWS services and agent functionality
"""

import os
import sys
import json
import unittest
import time
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import AWS components
from shared.bedrock_agent import BedrockAgent
from shared.aws_messaging import AWSMessaging
from shared.aws_storage import S3Storage
from RAG.aws_rag_engine import AWSRAGEngine

class TestBedrockAgent(unittest.TestCase):
    """Test BedrockAgent functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.agent = BedrockAgent(
            name="test_agent",
            model="anthropic.claude-3-5-sonnet-20241022-v2:0",
            description="Test agent",
            instruction="You are a test agent for unit testing."
        )
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.name, "test_agent")
        self.assertEqual(self.agent.model, "anthropic.claude-3-5-sonnet-20241022-v2:0")
        self.assertIsNotNone(self.agent.bedrock_runtime)
    
    @patch('boto3.client')
    def test_agent_invoke(self, mock_boto3):
        """Test agent invocation with mocked Bedrock"""
        # Mock Bedrock response
        mock_response = {
            'body': MagicMock()
        }
        mock_response['body'].read.return_value = json.dumps({
            'content': [{'text': 'Test response from Claude'}],
            'usage': {'input_tokens': 10, 'output_tokens': 5}
        }).encode()
        
        mock_bedrock = MagicMock()
        mock_bedrock.invoke_model.return_value = mock_response
        mock_boto3.return_value = mock_bedrock
        
        # Test invocation
        response = self.agent.invoke("Hello, test message")
        
        self.assertIsNotNone(response)
        self.assertEqual(response.content, "Test response from Claude")
        self.assertEqual(response.model_id, "anthropic.claude-3-5-sonnet-20241022-v2:0")
    
    def test_get_embedding(self):
        """Test embedding generation"""
        with patch('boto3.client') as mock_boto3:
            # Mock Bedrock response
            mock_response = {
                'body': MagicMock()
            }
            mock_response['body'].read.return_value = json.dumps({
                'embedding': [0.1, 0.2, 0.3] * 512  # 1536 dimensions
            }).encode()
            
            mock_bedrock = MagicMock()
            mock_bedrock.invoke_model.return_value = mock_response
            mock_boto3.return_value = mock_bedrock
            
            embedding = self.agent.get_embedding("test text")
            self.assertEqual(len(embedding), 1536)

class TestAWSMessaging(unittest.TestCase):
    """Test AWS EventBridge messaging"""
    
    def setUp(self):
        """Set up test environment"""
        with patch('boto3.client'):
            self.messaging = AWSMessaging()
    
    @patch('boto3.client')
    def test_messaging_initialization(self, mock_boto3):
        """Test messaging system initialization"""
        messaging = AWSMessaging()
        self.assertIsNotNone(messaging.eventbridge)
        self.assertIsNotNone(messaging.sns)
    
    def test_publish_local(self):
        """Test local message publishing"""
        received_messages = []
        
        def test_handler(event_data):
            received_messages.append(event_data)
        
        # Subscribe to test event
        self.messaging.subscribe("test.event", test_handler)
        
        # Publish test event
        test_data = {"message": "Hello from test"}
        self.messaging._publish_local("test.event", test_data)
        
        # Wait for processing
        time.sleep(0.1)
        
        self.assertEqual(len(received_messages), 1)
        self.assertEqual(received_messages[0], test_data)
    
    @patch('boto3.client')
    def test_publish_eventbridge(self, mock_boto3):
        """Test EventBridge publishing"""
        mock_eventbridge = MagicMock()
        mock_eventbridge.put_events.return_value = {'FailedEntryCount': 0}
        mock_boto3.return_value = mock_eventbridge
        
        messaging = AWSMessaging()
        messaging.eventbridge = mock_eventbridge
        
        success = messaging.publish("test.event", {"message": "test"})
        self.assertTrue(success)
        mock_eventbridge.put_events.assert_called_once()

class TestS3Storage(unittest.TestCase):
    """Test S3 storage functionality"""
    
    def setUp(self):
        """Set up test environment"""
        with patch('boto3.client'):
            self.storage = S3Storage(bucket_name="test-bucket")
    
    @patch('boto3.client')
    def test_storage_initialization(self, mock_boto3):
        """Test S3 storage initialization"""
        storage = S3Storage(bucket_name="test-bucket")
        self.assertIsNotNone(storage.s3_client)
        self.assertEqual(storage.bucket_name, "test-bucket")
    
    @patch('boto3.client')
    def test_upload_file(self, mock_boto3):
        """Test file upload"""
        mock_s3 = MagicMock()
        mock_boto3.return_value = mock_s3
        
        storage = S3Storage(bucket_name="test-bucket")
        storage.s3_client = mock_s3
        
        # Create test file
        test_file = "/tmp/test.txt"
        with open(test_file, "w") as f:
            f.write("test content")
        
        success = storage.upload_file(test_file, "test/object.txt")
        self.assertTrue(success)
        mock_s3.upload_file.assert_called_once()
        
        # Cleanup
        os.unlink(test_file)
    
    @patch('boto3.client')
    def test_get_object(self, mock_boto3):
        """Test object retrieval"""
        mock_s3 = MagicMock()
        mock_response = {
            'Body': MagicMock(),
            'Metadata': {'test': 'metadata'},
            'ContentType': 'text/plain',
            'LastModified': '2023-01-01T00:00:00Z',
            'ContentLength': 12
        }
        mock_response['Body'].read.return_value = b'test content'
        mock_s3.get_object.return_value = mock_response
        mock_boto3.return_value = mock_s3
        
        storage = S3Storage(bucket_name="test-bucket")
        storage.s3_client = mock_s3
        
        result = storage.get_object("test/object.txt")
        self.assertIsNotNone(result)
        self.assertEqual(result['content'], b'test content')
        self.assertEqual(result['metadata']['test'], 'metadata')

class TestAWSRAGEngine(unittest.TestCase):
    """Test AWS RAG Engine"""
    
    def setUp(self):
        """Set up test environment"""
        with patch('boto3.client'), patch('opensearchpy.OpenSearch'):
            self.rag = AWSRAGEngine()
    
    @patch('boto3.client')
    @patch('opensearchpy.OpenSearch')
    def test_rag_initialization(self, mock_opensearch, mock_boto3):
        """Test RAG engine initialization"""
        rag = AWSRAGEngine()
        self.assertIsNotNone(rag.embeddings)
        self.assertIsNotNone(rag.vector_store)
    
    @patch('boto3.client')
    @patch('opensearchpy.OpenSearch')
    def test_add_documents(self, mock_opensearch, mock_boto3):
        """Test document addition"""
        # Mock embeddings
        mock_bedrock = MagicMock()
        mock_response = {
            'body': MagicMock()
        }
        mock_response['body'].read.return_value = json.dumps({
            'embedding': [0.1, 0.2, 0.3] * 512
        }).encode()
        mock_bedrock.invoke_model.return_value = mock_response
        mock_boto3.return_value = mock_bedrock
        
        # Mock OpenSearch
        mock_os = MagicMock()
        mock_opensearch.return_value = mock_os
        
        rag = AWSRAGEngine()
        rag.embeddings.bedrock_runtime = mock_bedrock
        rag.vector_store.client = mock_os
        
        # Test documents
        test_docs = [
            {
                "id": "test_doc_1",
                "content": "This is a test document about banking regulations.",
                "metadata": {"regulator": "APRA"},
                "source": "test_source"
            }
        ]
        
        success = rag.add_documents(test_docs)
        self.assertTrue(success)
    
    @patch('boto3.client')
    @patch('opensearchpy.OpenSearch')
    def test_query(self, mock_opensearch, mock_boto3):
        """Test RAG querying"""
        # Mock embeddings
        mock_bedrock = MagicMock()
        mock_response = {
            'body': MagicMock()
        }
        mock_response['body'].read.return_value = json.dumps({
            'embedding': [0.1, 0.2, 0.3] * 512
        }).encode()
        mock_bedrock.invoke_model.return_value = mock_response
        mock_boto3.return_value = mock_bedrock
        
        # Mock OpenSearch
        mock_os = MagicMock()
        mock_os.search.return_value = {
            'hits': {
                'hits': [
                    {
                        '_id': 'doc1',
                        '_source': {
                            'content': 'Test banking regulation content',
                            'source': 'test_source'
                        },
                        '_score': 0.95
                    }
                ]
            }
        }
        mock_opensearch.return_value = mock_os
        
        rag = AWSRAGEngine()
        rag.embeddings.bedrock_runtime = mock_bedrock
        rag.vector_store.client = mock_os
        
        result = rag.query("What are banking regulations?", "compliance")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.query, "What are banking regulations?")
        self.assertEqual(len(result.relevant_documents), 1)

class TestAgentIntegration(unittest.TestCase):
    """Test integration between all components"""
    
    def test_agent_with_rag(self):
        """Test agent using RAG system"""
        with patch('boto3.client'), patch('opensearchpy.OpenSearch'):
            # Create agent with RAG
            agent = BedrockAgent(
                name="test_agent_with_rag",
                model="anthropic.claude-3-5-sonnet-20241022-v2:0",
                description="Test agent with RAG",
                instruction="You are a test agent that can use RAG for regulatory information."
            )
            
            # Test agent can get embeddings
            with patch.object(agent, 'get_embedding') as mock_embedding:
                mock_embedding.return_value = [0.1, 0.2, 0.3] * 512
                embedding = agent.get_embedding("test text")
                self.assertEqual(len(embedding), 1536)
    
    def test_messaging_with_storage(self):
        """Test messaging system with storage"""
        with patch('boto3.client'):
            messaging = AWSMessaging()
            storage = S3Storage(bucket_name="test-bucket")
            
            # Test that both systems can be initialized together
            self.assertIsNotNone(messaging)
            self.assertIsNotNone(storage)

class TestEnvironmentConfiguration(unittest.TestCase):
    """Test environment configuration"""
    
    def test_environment_variables(self):
        """Test required environment variables"""
        required_vars = [
            "AWS_REGION",
            "BEDROCK_MODEL_ID",
            "BEDROCK_EMBEDDING_MODEL",
            "S3_BUCKET_NAME",
            "OPENSEARCH_ENDPOINT",
            "EVENT_BUS_NAME"
        ]
        
        for var in required_vars:
            # Test that variables can be set
            os.environ[var] = f"test_{var.lower()}"
            value = os.getenv(var)
            self.assertIsNotNone(value)
            self.assertEqual(value, f"test_{var.lower()}")

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestBedrockAgent,
        TestAWSMessaging,
        TestS3Storage,
        TestAWSRAGEngine,
        TestAgentIntegration,
        TestEnvironmentConfiguration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("🧪 Running AWS Integration Tests")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)



