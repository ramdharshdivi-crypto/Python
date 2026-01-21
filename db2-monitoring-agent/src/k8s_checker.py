"""Kubernetes pod health checker."""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from kubernetes import client, config
from kubernetes.client.rest import ApiException


class KubernetesHealthChecker:
    """Check Kubernetes pod health and status."""

    def __init__(self, k8s_config: Dict[str, Any]):
        """Initialize Kubernetes health checker.
        
        Args:
            k8s_config: Kubernetes configuration dictionary
        """
        self.k8s_config = k8s_config
        self.v1 = None
        
    def _load_k8s_config(self) -> bool:
        """Load Kubernetes configuration.
        
        Returns:
            True if config loaded successfully, False otherwise
        """
        try:
            # Try to load from kubeconfig
            kubeconfig_path = self.k8s_config.get('kubeconfig_path')
            context = self.k8s_config.get('context')
            
            if kubeconfig_path:
                config.load_kube_config(config_file=kubeconfig_path, context=context)
            else:
                # Try in-cluster config first, then fall back to default kubeconfig
                try:
                    config.load_incluster_config()
                except:
                    config.load_kube_config(context=context)
            
            self.v1 = client.CoreV1Api()
            return True
            
        except Exception as e:
            print(f"Failed to load Kubernetes config: {str(e)}")
            return False
    
    def _get_pod_by_name(self, namespace: str, pod_name: str) -> Optional[Any]:
        """Get pod by exact name.
        
        Args:
            namespace: Kubernetes namespace
            pod_name: Exact pod name
            
        Returns:
            Pod object or None if not found
        """
        try:
            pod = self.v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            return pod
        except ApiException as e:
            if e.status == 404:
                return None
            raise
    
    def _get_pods_by_label(self, namespace: str, label_selector: str) -> List[Any]:
        """Get pods by label selector.
        
        Args:
            namespace: Kubernetes namespace
            label_selector: Label selector (e.g., 'app=my-app')
            
        Returns:
            List of pod objects
        """
        try:
            pods = self.v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector
            )
            return pods.items
        except ApiException:
            return []
    
    def _extract_pod_info(self, pod: Any) -> Dict[str, Any]:
        """Extract relevant information from pod object.
        
        Args:
            pod: Kubernetes pod object
            
        Returns:
            Dictionary with pod information
        """
        # Get container statuses
        container_statuses = pod.status.container_statuses or []
        
        # Calculate total restarts
        total_restarts = sum(c.restart_count for c in container_statuses)
        
        # Check if all containers are ready
        all_ready = all(c.ready for c in container_statuses) if container_statuses else False
        
        # Get container states
        container_states = []
        for container in container_statuses:
            state_info = {'name': container.name, 'ready': container.ready}
            
            if container.state.running:
                state_info['state'] = 'running'
                state_info['started_at'] = container.state.running.started_at.isoformat()
            elif container.state.waiting:
                state_info['state'] = 'waiting'
                state_info['reason'] = container.state.waiting.reason
            elif container.state.terminated:
                state_info['state'] = 'terminated'
                state_info['reason'] = container.state.terminated.reason
                state_info['exit_code'] = container.state.terminated.exit_code
            
            container_states.append(state_info)
        
        return {
            'name': pod.metadata.name,
            'namespace': pod.metadata.namespace,
            'phase': pod.status.phase,
            'ready': all_ready,
            'restart_count': total_restarts,
            'node': pod.spec.node_name,
            'created_at': pod.metadata.creation_timestamp.isoformat(),
            'containers': container_states,
            'conditions': [
                {
                    'type': c.type,
                    'status': c.status,
                    'reason': c.reason if hasattr(c, 'reason') else None
                }
                for c in (pod.status.conditions or [])
            ]
        }
    
    def check_health(self) -> Dict[str, Any]:
        """Perform Kubernetes pod health check.
        
        Returns:
            Health check result dictionary
        """
        health_status = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'status': 'unknown',
            'pods': [],
            'total_pods': 0,
            'healthy_pods': 0,
            'details': '',
            'error': None
        }
        
        # Load Kubernetes config
        if not self._load_k8s_config():
            health_status['status'] = 'unhealthy'
            health_status['error'] = 'Failed to load Kubernetes configuration'
            health_status['details'] = 'Could not connect to Kubernetes cluster'
            return health_status
        
        namespace = self.k8s_config['namespace']
        pod_name = self.k8s_config.get('pod_name')
        label_selector = self.k8s_config.get('label_selector')
        
        try:
            # Get pods
            pods = []
            if pod_name:
                pod = self._get_pod_by_name(namespace, pod_name)
                if pod:
                    pods = [pod]
            elif label_selector:
                pods = self._get_pods_by_label(namespace, label_selector)
            
            if not pods:
                health_status['status'] = 'unhealthy'
                health_status['error'] = 'No pods found'
                health_status['details'] = f"No pods found in namespace '{namespace}'"
                return health_status
            
            # Process pod information
            pod_infos = [self._extract_pod_info(pod) for pod in pods]
            health_status['pods'] = pod_infos
            health_status['total_pods'] = len(pod_infos)
            
            # Count healthy pods (Running and Ready)
            healthy_count = sum(
                1 for p in pod_infos 
                if p['phase'] == 'Running' and p['ready']
            )
            health_status['healthy_pods'] = healthy_count
            
            # Determine overall status
            if healthy_count == len(pod_infos):
                health_status['status'] = 'healthy'
                health_status['details'] = f"All {healthy_count} pod(s) are running and ready"
            elif healthy_count > 0:
                health_status['status'] = 'degraded'
                health_status['details'] = (
                    f"{healthy_count}/{len(pod_infos)} pod(s) are healthy"
                )
            else:
                health_status['status'] = 'unhealthy'
                health_status['details'] = "No pods are healthy"
            
            # Check restart thresholds
            alert_threshold = self.k8s_config.get('alert', {}).get('pod_restart_threshold', 3)
            high_restarts = [p for p in pod_infos if p['restart_count'] > alert_threshold]
            
            if high_restarts:
                health_status['warnings'] = [
                    f"Pod {p['name']} has {p['restart_count']} restarts (threshold: {alert_threshold})"
                    for p in high_restarts
                ]
            
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['error'] = str(e)
            health_status['details'] = f"Error checking Kubernetes pods: {str(e)}"
        
        return health_status


def check_k8s_health(k8s_config: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to check Kubernetes health.
    
    Args:
        k8s_config: Kubernetes configuration dictionary
        
    Returns:
        Health check result
    """
    checker = KubernetesHealthChecker(k8s_config)
    return checker.check_health()
