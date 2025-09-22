#!/usr/bin/env python3
"""
Setup Auto-Scaling for RAG System
"""

import os
import sys
import json
from pathlib import Path

def create_hpa_config():
    """Create Horizontal Pod Autoscaler configuration"""
    print("Creating Horizontal Pod Autoscaler configuration...")
    
    hpa_config = """
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: transaction-risk-agent-hpa
  namespace: nfrguard-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: transaction-risk-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: compliance-agent-hpa
  namespace: nfrguard-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: compliance-agent
  minReplicas: 2
  maxReplicas: 8
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: resilience-agent-hpa
  namespace: nfrguard-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: resilience-agent
  minReplicas: 2
  maxReplicas: 8
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: customer-sentiment-agent-hpa
  namespace: nfrguard-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: customer-sentiment-agent
  minReplicas: 2
  maxReplicas: 6
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: data-privacy-agent-hpa
  namespace: nfrguard-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: data-privacy-agent
  minReplicas: 2
  maxReplicas: 6
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: knowledge-agent-hpa
  namespace: nfrguard-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: knowledge-agent
  minReplicas: 2
  maxReplicas: 6
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: banking-assistant-agent-hpa
  namespace: nfrguard-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: banking-assistant-agent
  minReplicas: 2
  maxReplicas: 6
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
"""
    
    hpa_file = Path(__file__).parent / "k8s" / "hpa-config.yaml"
    hpa_file.parent.mkdir(exist_ok=True)
    
    with open(hpa_file, "w") as f:
        f.write(hpa_config)
    
    print(f"✅ HPA configuration saved to: {hpa_file}")
    return hpa_file

def create_vertical_scaling():
    """Create Vertical Pod Autoscaler configuration"""
    print("Creating Vertical Pod Autoscaler configuration...")
    
    vpa_config = """
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: transaction-risk-agent-vpa
  namespace: nfrguard-agents
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: transaction-risk-agent
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: transaction-risk-agent
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2000m
        memory: 4Gi
      controlledResources: ["cpu", "memory"]
---
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: compliance-agent-vpa
  namespace: nfrguard-agents
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: compliance-agent
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: compliance-agent
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2000m
        memory: 4Gi
      controlledResources: ["cpu", "memory"]
---
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: resilience-agent-vpa
  namespace: nfrguard-agents
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: resilience-agent
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: resilience-agent
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2000m
        memory: 4Gi
      controlledResources: ["cpu", "memory"]
---
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: customer-sentiment-agent-vpa
  namespace: nfrguard-agents
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: customer-sentiment-agent
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: customer-sentiment-agent
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2000m
        memory: 4Gi
      controlledResources: ["cpu", "memory"]
---
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: data-privacy-agent-vpa
  namespace: nfrguard-agents
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: data-privacy-agent
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: data-privacy-agent
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2000m
        memory: 4Gi
      controlledResources: ["cpu", "memory"]
---
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: knowledge-agent-vpa
  namespace: nfrguard-agents
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: knowledge-agent
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: knowledge-agent
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2000m
        memory: 4Gi
      controlledResources: ["cpu", "memory"]
---
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: banking-assistant-agent-vpa
  namespace: nfrguard-agents
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: banking-assistant-agent
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: banking-assistant-agent
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2000m
        memory: 4Gi
      controlledResources: ["cpu", "memory"]
"""
    
    vpa_file = Path(__file__).parent / "k8s" / "vpa-config.yaml"
    vpa_file.parent.mkdir(exist_ok=True)
    
    with open(vpa_file, "w") as f:
        f.write(vpa_config)
    
    print(f"✅ VPA configuration saved to: {vpa_file}")
    return vpa_file

def create_cluster_autoscaler():
    """Create cluster autoscaler configuration"""
    print("Creating cluster autoscaler configuration...")
    
    cluster_autoscaler_config = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
  labels:
    app: cluster-autoscaler
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      labels:
        app: cluster-autoscaler
    spec:
      serviceAccountName: cluster-autoscaler
      containers:
      - image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.21.0
        name: cluster-autoscaler
        resources:
          limits:
            cpu: 100m
            memory: 300Mi
          requests:
            cpu: 100m
            memory: 300Mi
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=gce
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste
        - --node-group-auto-discovery=mig:name=your-node-pool,min=1,max=10
        env:
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /var/secrets/google/key.json
        volumeMounts:
        - name: service-account
          mountPath: /var/secrets/google
          readOnly: true
      volumes:
      - name: service-account
        secret:
          secretName: google-service-account
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: cluster-autoscaler
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-autoscaler
rules:
- apiGroups: [""]
  resources: ["events", "endpoints"]
  verbs: ["create", "patch"]
- apiGroups: [""]
  resources: ["pods/eviction"]
  verbs: ["create"]
- apiGroups: [""]
  resources: ["pods/status"]
  verbs: ["update"]
- apiGroups: [""]
  resources: ["endpoints"]
  resourceNames: ["cluster-autoscaler"]
  verbs: ["get", "update"]
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["watch", "list", "get", "update"]
- apiGroups: [""]
  resources: ["namespaces", "pods", "services", "replicationcontrollers", "persistentvolumeclaims", "persistentvolumes"]
  verbs: ["watch", "list", "get"]
- apiGroups: ["extensions"]
  resources: ["replicasets", "daemonsets"]
  verbs: ["watch", "list", "get"]
- apiGroups: ["policy"]
  resources: ["poddisruptionbudgets"]
  verbs: ["watch", "list"]
- apiGroups: ["apps"]
  resources: ["statefulsets", "replicasets", "daemonsets"]
  verbs: ["watch", "list", "get"]
- apiGroups: ["storage.k8s.io"]
  resources: ["storageclasses", "csinodes", "csidrivers", "csistoragecapacities"]
  verbs: ["watch", "list", "get"]
- apiGroups: ["batch", "extensions"]
  resources: ["jobs"]
  verbs: ["get", "list", "watch", "patch"]
- apiGroups: ["coordination.k8s.io"]
  resources: ["leases"]
  verbs: ["create"]
- apiGroups: ["coordination.k8s.io"]
  resourceNames: ["cluster-autoscaler"]
  resources: ["leases"]
  verbs: ["get", "update"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cluster-autoscaler
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-autoscaler
subjects:
- kind: ServiceAccount
  name: cluster-autoscaler
  namespace: kube-system
"""
    
    cluster_autoscaler_file = Path(__file__).parent / "k8s" / "cluster-autoscaler.yaml"
    cluster_autoscaler_file.parent.mkdir(exist_ok=True)
    
    with open(cluster_autoscaler_file, "w") as f:
        f.write(cluster_autoscaler_config)
    
    print(f"✅ Cluster autoscaler configuration saved to: {cluster_autoscaler_file}")
    return cluster_autoscaler_file

def create_scaling_monitor():
    """Create scaling monitoring script"""
    print("Creating scaling monitoring script...")
    
    scaling_monitor_code = '''
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
        print("\\n📦 Pod Status:")
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
        print("\\n🖥️  Node Status:")
        ready_nodes = sum(1 for node in node_items if node["status"]["conditions"][0]["status"] == "True")
        total_nodes = len(node_items)
        print(f"  Ready nodes: {ready_nodes}/{total_nodes}")
        
        # Resource usage
        print("\\n💾 Resource Usage:")
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
                print("\\n" + "=" * 60)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\\n🛑 Monitoring stopped")

if __name__ == "__main__":
    monitor = ScalingMonitor()
    monitor.monitor_scaling()
'''
    
    scaling_monitor_file = Path(__file__).parent / "scaling_monitor.py"
    with open(scaling_monitor_file, "w", encoding="utf-8") as f:
        f.write(scaling_monitor_code)
    
    print(f"✅ Scaling monitor created: {scaling_monitor_file}")
    return scaling_monitor_file

def main():
    """Main scaling setup function"""
    print("📈 Setting up auto-scaling for RAG system")
    print("=" * 60)
    
    # Create scaling configurations
    hpa_file = create_hpa_config()
    vpa_file = create_vertical_scaling()
    cluster_autoscaler_file = create_cluster_autoscaler()
    scaling_monitor_file = create_scaling_monitor()
    
    print("\n" + "=" * 60)
    print("✅ Auto-scaling setup complete!")
    print("\n📋 Next steps:")
    print("1. Deploy HPA (Horizontal Pod Autoscaler):")
    print("   kubectl apply -f k8s/hpa-config.yaml")
    print("\n2. Deploy VPA (Vertical Pod Autoscaler) - optional:")
    print("   kubectl apply -f k8s/vpa-config.yaml")
    print("\n3. Deploy Cluster Autoscaler - if not already deployed:")
    print("   kubectl apply -f k8s/cluster-autoscaler.yaml")
    print("\n4. Monitor scaling:")
    print("   python scaling_monitor.py")
    print("\n5. Check scaling status:")
    print("   kubectl get hpa -n nfrguard-agents")
    print("   kubectl get pods -n nfrguard-agents")
    print("\n🎯 Your RAG system now has comprehensive auto-scaling!")

if __name__ == "__main__":
    main()
