#!/usr/bin/env python3
"""
AWS S3 Storage Wrapper
Replaces Google Cloud Storage (GCS) with Amazon S3 for document and artifact storage
"""

import os
import json
import logging
import boto3
from typing import Dict, List, Optional, Any, Union, BinaryIO
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class S3Storage:
    """AWS S3 storage wrapper (replaces Google Cloud Storage)"""
    
    def __init__(self, region: str = None, bucket_name: str = None):
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME", "nfrguard-documents")
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client('s3', region_name=self.region)
            logger.info(f"S3 client initialized in {self.region}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure S3 bucket exists, create if it doesn't"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"S3 bucket {self.bucket_name} already exists")
        except self.s3_client.exceptions.NoSuchBucket:
            try:
                if self.region == 'us-east-1':
                    # us-east-1 doesn't need LocationConstraint
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                else:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )
                logger.info(f"Created S3 bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to create S3 bucket {self.bucket_name}: {e}")
                raise
        except Exception as e:
            logger.error(f"Error checking S3 bucket {self.bucket_name}: {e}")
            raise
    
    def upload_file(self, file_path: str, object_key: str, metadata: Dict[str, str] = None) -> bool:
        """Upload a file to S3"""
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                object_key,
                ExtraArgs=extra_args
            )
            
            logger.info(f"Uploaded file {file_path} to s3://{self.bucket_name}/{object_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading file {file_path} to S3: {e}")
            return False
    
    def upload_fileobj(self, file_obj: BinaryIO, object_key: str, metadata: Dict[str, str] = None) -> bool:
        """Upload a file object to S3"""
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_key,
                ExtraArgs=extra_args
            )
            
            logger.info(f"Uploaded file object to s3://{self.bucket_name}/{object_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading file object to S3: {e}")
            return False
    
    def download_file(self, object_key: str, file_path: str) -> bool:
        """Download a file from S3"""
        try:
            self.s3_client.download_file(
                self.bucket_name,
                object_key,
                file_path
            )
            
            logger.info(f"Downloaded s3://{self.bucket_name}/{object_key} to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading file from S3: {e}")
            return False
    
    def download_fileobj(self, object_key: str, file_obj: BinaryIO) -> bool:
        """Download a file object from S3"""
        try:
            self.s3_client.download_fileobj(
                self.bucket_name,
                object_key,
                file_obj
            )
            
            logger.info(f"Downloaded s3://{self.bucket_name}/{object_key} to file object")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading file object from S3: {e}")
            return False
    
    def get_object(self, object_key: str) -> Optional[Dict[str, Any]]:
        """Get an object from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            return {
                'content': response['Body'].read(),
                'metadata': response.get('Metadata', {}),
                'content_type': response.get('ContentType', ''),
                'last_modified': response.get('LastModified'),
                'size': response.get('ContentLength', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting object from S3: {e}")
            return None
    
    def put_object(self, object_key: str, content: Union[str, bytes], metadata: Dict[str, str] = None) -> bool:
        """Put content directly to S3"""
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            if isinstance(content, str):
                content = content.encode('utf-8')
                extra_args['ContentType'] = 'text/plain'
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=content,
                **extra_args
            )
            
            logger.info(f"Put content to s3://{self.bucket_name}/{object_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error putting content to S3: {e}")
            return False
    
    def delete_object(self, object_key: str) -> bool:
        """Delete an object from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            logger.info(f"Deleted s3://{self.bucket_name}/{object_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting object from S3: {e}")
            return False
    
    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
        """List objects in S3 bucket with optional prefix"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            objects = []
            for obj in response.get('Contents', []):
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag']
                })
            
            logger.info(f"Listed {len(objects)} objects with prefix '{prefix}'")
            return objects
            
        except Exception as e:
            logger.error(f"Error listing objects in S3: {e}")
            return []
    
    def object_exists(self, object_key: str) -> bool:
        """Check if an object exists in S3"""
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return True
        except self.s3_client.exceptions.NoSuchKey:
            return False
        except Exception as e:
            logger.error(f"Error checking if object exists in S3: {e}")
            return False
    
    def generate_presigned_url(self, object_key: str, expiration: int = 3600) -> Optional[str]:
        """Generate a presigned URL for S3 object"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            
            logger.info(f"Generated presigned URL for s3://{self.bucket_name}/{object_key}")
            return url
            
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None
    
    def sync_directory(self, local_dir: str, s3_prefix: str = "") -> bool:
        """Sync a local directory to S3"""
        try:
            local_path = Path(local_dir)
            if not local_path.exists():
                logger.error(f"Local directory {local_dir} does not exist")
                return False
            
            uploaded_count = 0
            for file_path in local_path.rglob('*'):
                if file_path.is_file():
                    # Calculate relative path for S3 key
                    relative_path = file_path.relative_to(local_path)
                    s3_key = f"{s3_prefix}/{relative_path}".lstrip('/')
                    
                    # Upload file
                    if self.upload_file(str(file_path), s3_key):
                        uploaded_count += 1
            
            logger.info(f"Synced {uploaded_count} files from {local_dir} to S3")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing directory to S3: {e}")
            return False
    
    def download_directory(self, s3_prefix: str, local_dir: str) -> bool:
        """Download files from S3 prefix to local directory"""
        try:
            local_path = Path(local_dir)
            local_path.mkdir(parents=True, exist_ok=True)
            
            objects = self.list_objects(prefix=s3_prefix)
            downloaded_count = 0
            
            for obj in objects:
                s3_key = obj['key']
                # Calculate local file path
                relative_path = s3_key[len(s3_prefix):].lstrip('/')
                local_file = local_path / relative_path
                
                # Create parent directories
                local_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Download file
                if self.download_file(s3_key, str(local_file)):
                    downloaded_count += 1
            
            logger.info(f"Downloaded {downloaded_count} files from S3 to {local_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading directory from S3: {e}")
            return False

# Global storage instance
_storage_instance = None

def get_storage() -> S3Storage:
    """Get global storage instance"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = S3Storage()
    return _storage_instance

# Convenience functions
def upload_file(file_path: str, object_key: str, metadata: Dict[str, str] = None) -> bool:
    """Upload a file to S3 (global function)"""
    return get_storage().upload_file(file_path, object_key, metadata)

def download_file(object_key: str, file_path: str) -> bool:
    """Download a file from S3 (global function)"""
    return get_storage().download_file(object_key, file_path)

def get_object(object_key: str) -> Optional[Dict[str, Any]]:
    """Get an object from S3 (global function)"""
    return get_storage().get_object(object_key)

def put_object(object_key: str, content: Union[str, bytes], metadata: Dict[str, str] = None) -> bool:
    """Put content to S3 (global function)"""
    return get_storage().put_object(object_key, content, metadata)

def list_objects(prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
    """List objects in S3 (global function)"""
    return get_storage().list_objects(prefix, max_keys)

def object_exists(object_key: str) -> bool:
    """Check if object exists in S3 (global function)"""
    return get_storage().object_exists(object_key)

# Example usage and testing
if __name__ == "__main__":
    # Test S3 storage
    storage = S3Storage()
    
    # Test uploading a file
    test_content = "Hello from AWS S3 storage!"
    success = storage.put_object("test/hello.txt", test_content)
    print(f"Upload test: {'Success' if success else 'Failed'}")
    
    # Test downloading
    obj = storage.get_object("test/hello.txt")
    if obj:
        print(f"Download test: {obj['content'].decode('utf-8')}")
    
    # Test listing objects
    objects = storage.list_objects("test/")
    print(f"List test: Found {len(objects)} objects")
    
    # Cleanup
    storage.delete_object("test/hello.txt")
    print("Cleanup completed")

