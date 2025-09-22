
#!/usr/bin/env python3
"""
Scaling Monitor for RAG System
"""

import subprocess
import json
import time
import logging
from datetime import datetime

class ScalingMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.namespace = "nfrguard-agents"
        
    def get_hpa_status(self):
        """Get HPA status for all agents"""
        try:
            result = subprocess.run([
                "kubectl", "get", "hpa", "-n", self.namespace, "-o", "json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                hpa_data = json.loads(result.stdout)
                return hpa_data.get("items", [])
            else:
                self.logger.error(f"Failed to get HPA status: {result.stderr}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting HPA status: {e}")
            return []
    
    def get_pod_status(self):
        """Get pod status for all agents"""
        try:
            result = subprocess.run([
                "kubectl", "get", "pods", "-n", self.namespace, "-o", "json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                pod_data = json.loads(result.stdout)
                return pod_data.get("items", [])
            else:
                self.logger.error(f"Failed to get pod status: {result.stderr}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting pod status: {e}")
            return []
    
    def get_node_status(self):
        """Get node status"""
        try:
            result = subprocess.run([
                "kubectl", "get", "nodes", "-o", "json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                node_data = json.loads(result.stdout)
                return node_data.get("items", [])
            else:
                self.logger.error(f"Failed to get node status: {result.stderr}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting node status: {e}")
            return []
    
    def monitor_scaling(self):
        """Monitor scaling status"""
        print(f"🔍 Scaling Monitor - {datetime.now().isoformat()}")
        print("=" * 60)
        
        # HPA Status
        hpa_items = self.get_hpa_status()
        print("📊 Horizontal Pod Autoscaler Status:")
        for hpa in hpa_items:
            name = hpa["metadata"]["name"]
            spec = hpa["spec"]
            status = hpa["status"]
            
            current_replicas = status.get("currentReplicas", 0)
            desired_replicas = status.get("desiredReplicas", 0)
            min_replicas = spec.get("minReplicas", 0)
            max_replicas = spec.get("maxReplicas", 0)
            
            print(f"  {name}:")
            print(f"    Current: {current_replicas}, Desired: {desired_replicas}")
            print(f"    Range: {min_replicas} - {max_replicas}")
            
            # Check if scaling is needed
            if current_replicas < desired_replicas:
                print(f"    ⬆️  Scaling up to {desired_replicas}")
            elif current_replicas > desired_replicas:
                print(f"    ⬇️  Scaling down to {desired_replicas}")
            else:
                print(f"    ✅ Stable at {current_replicas}")
        
        # Pod Status
        pod_items = self.get_pod_status()
        print("\n📦 Pod Status:")
        agent_pods = {}
        for pod in pod_items:
            name = pod["metadata"]["name"]
            if "-agent-" in name:
                agent_name = name.split("-agent-")[0] + "-agent"
                if agent_name not in agent_pods:
                    agent_pods[agent_name] = []
                agent_pods[agent_name].append(pod)
        
        for agent_name, pods in agent_pods.items():
            running_pods = sum(1 for pod in pods if pod["status"]["phase"] == "Running")
            total_pods = len(pods)
            print(f"  {agent_name}: {running_pods}/{total_pods} running")
        
        # Node Status
        node_items = self.get_node_status()
        print("\n🖥️  Node Status:")
        ready_nodes = sum(1 for node in node_items if node["status"]["conditions"][0]["status"] == "True")
        total_nodes = len(node_items)
        print(f"  Ready nodes: {ready_nodes}/{total_nodes}")
        
        # Resource usage
        print("\n💾 Resource Usage:")
        for node in node_items:
            name = node["metadata"]["name"]
            capacity = node["status"]["capacity"]
            allocatable = node["status"]["allocatable"]
            
            cpu_capacity = capacity.get("cpu", "0")
            memory_capacity = capacity.get("memory", "0")
            cpu_allocatable = allocatable.get("cpu", "0")
            memory_allocatable = allocatable.get("memory", "0")
            
            print(f"  {name}:")
            print(f"    CPU: {cpu_allocatable}/{cpu_capacity}")
            print(f"    Memory: {memory_allocatable}/{memory_capacity}")
    
    def run_continuous_monitoring(self, interval=60):
        """Run continuous monitoring"""
        print(f"🔄 Starting continuous scaling monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.monitor_scaling()
                print("\n" + "=" * 60)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")

if __name__ == "__main__":
    monitor = ScalingMonitor()
    monitor.monitor_scaling()
