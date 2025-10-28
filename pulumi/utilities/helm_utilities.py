from typing import Dict, Any, List


class HelmUtilities:
    @staticmethod
    def get_grafana_values(environment: str) -> Dict[str, Any]:
        """Get Grafana Helm values based on environment."""
        base_values = {
            "adminPassword": "prod-admin-2024!" if environment == "prod" else "admin123",
            "persistence": {
                "enabled": True,
                "size": "50Gi" if environment == "prod" else "10Gi",
            },
            "service": {
                "type": "NodePort",
                "port": 80,
            },
        }
        
        if environment == "prod":
            return {
                **base_values,
                "replicas": 2,
                "resources": {
                    "requests": {
                        "memory": "512Mi",
                        "cpu": "500m",
                    },
                    "limits": {
                        "memory": "1Gi",
                        "cpu": "1000m",
                    },
                },
            }
        
        return base_values
    
    @staticmethod
    def get_metrics_server_values(environment: str) -> Dict[str, Any]:
        """Get metrics server Helm values based on environment."""
        return {
            "args": [
                "--cert-dir=/tmp",
                "--secure-port=4443",
                "--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname",
                "--kubelet-use-node-status-port",
                "--metric-resolution=15s"
            ],
            "hostNetwork": False,
            "replicas": 2 if environment == "prod" else 1,
        }
