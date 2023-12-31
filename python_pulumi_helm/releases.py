import time
from pulumi_kubernetes.helm.v3 import Release
from .helpers.resources import release
import pulumi
import yaml

def cilium(
    provider,
    eks_cluster_name: str = "",
    name: str = "cilium",
    chart: str = "cilium",
    version: str = "1.14.1",
    repo: str = "https://helm.cilium.io",
    namespace: str = "kube-system",
    skip_await: bool = False,
    depends_on: list = [] )->Release:

    cilium_release = release(
        name=name,
        chart=chart,
        version=version,
        repo=repo,
        namespace=namespace,
        skip_await=skip_await,
        depends_on=depends_on,
        provider=provider,
        values={
            "cluster": {
                "name": eks_cluster_name,
                "id": 0,
            },
            "eni": {
                "enabled": True,
            },
            "ipam": {
                "mode": "eni",
            },
            "egressMasqueradeInterfaces": "eth0",
            "routingMode": "native",
            "hubble": {
                "enabled": True,
                "ui": {
                    "enabled": True
                },
                "relay": {
                    "enabled": True
                },
                "metrics": {
                    "enabled": "{dns,drop,tcp,flow,icmp,http}"
                }
            }
        },
    )

    return cilium_release

def metrics_server(
    provider,
    name: str = "metrics-server",
    chart: str = "metrics-server",
    version: str = "3.11.0",
    repo: str = "https://kubernetes-sigs.github.io/metrics-server",
    namespace: str = "kube-system",
    skip_await: bool = False,
    depends_on: list = [] )->Release:

    metrics_server_release = release(
        name=name,
        chart=chart,
        version=version,
        repo=repo,
        namespace=namespace,
        skip_await=skip_await,
        depends_on=depends_on,
        provider=provider,
        values={
            "resources": {
                "limits": {
                    "cpu": "200m",
                    "memory": "200Mi"
                },
                "requests": {
                    "cpu": "200m",
                    "memory": "200Mi"
                }
            }
        },
    )

    return metrics_server_release

def cluster_autoscaler(
    provider,
    aws_region,
    eks_sa_role_arn,
    eks_cluster_name,
    name: str = "cluster-autoscaler",
    chart: str = "cluster-autoscaler",
    version: str = "9.29.3",
    repo: str = "https://kubernetes.github.io/autoscaler",
    namespace: str = "default",
    skip_await: bool = False,
    depends_on: list = [] )->Release:

    cluster_autoscaler_release = release(
        name=name,
        chart=chart,
        version=version,
        repo=repo,
        namespace=namespace,
        skip_await=skip_await,
        depends_on=depends_on,
        provider=provider,
        values={
            "cloudProvider": "aws",
            "awsRegion": aws_region,
            "autoDiscovery": {
                "clusterName": eks_cluster_name,
                "tags": [
                    "k8s.io/cluster-autoscaler/enabled"
                ],
                "roles": ["worker"],
            },
            "rbac": {
                "create": True,
                "serviceAccount": {
                    "create": True,
                    "name": "cluster-autoscaler",
                    "automountServiceAccountToken": True,
                    "annotations": {
                        "eks.amazonaws.com/role-arn": eks_sa_role_arn,
                    }
                }
            },
            "resources": {
                "limits": {
                    "cpu": "200m",
                    "memory": "200Mi"
                },
                "requests": {
                    "cpu": "200m",
                    "memory": "200Mi"
                }
            },
        },
    )

    return cluster_autoscaler_release

def aws_load_balancer_controller(
    provider,
    aws_region,
    aws_vpc_id,
    eks_sa_role_arn,
    eks_cluster_name,
    name: str = "aws-load-balancer-controller",
    chart: str = "aws-load-balancer-controller",
    version: str = "1.6.0",
    repo: str = "https://aws.github.io/eks-charts",
    namespace: str = "default",
    skip_await: bool = False,
    depends_on: list = [] )->Release:

    aws_load_balancer_controller_release = release(
        name=name,
        chart=chart,
        version=version,
        repo=repo,
        namespace=namespace,
        skip_await=skip_await,
        depends_on=depends_on,
        provider=provider,
        #transformations=[tools.ignore_changes],
        values={
            "clusterName": eks_cluster_name,
            "region": aws_region,
            "vpcId": aws_vpc_id,
            "serviceAccount": {
                "create": True,
                "annotations": {
                    "eks.amazonaws.com/role-arn": eks_sa_role_arn,
                },
            }
        },
    )

    return aws_load_balancer_controller_release

def external_dns(
    provider,
    eks_sa_role_arn,
    name: str = "external-dns",
    chart: str = "external-dns",
    version: str = "1.13.0",
    repo: str = "https://kubernetes-sigs.github.io/external-dns",
    namespace: str = "default",
    skip_await: bool = False,
    depends_on: list = [] )->Release:

    external_dns_release = release(
        name=name,
        chart=chart,
        version=version,
        repo=repo,
        namespace=namespace,
        skip_await=skip_await,
        depends_on=depends_on,
        provider=provider,
        values={
            "provider": "aws",
            "sources": ["service", "ingress"],
            "policy": "sync",
            "deploymentStrategy": {
                "type": "Recreate",
            },
            "serviceAccount": {
                "create": True,
                "annotations": {
                    "eks.amazonaws.com/role-arn": eks_sa_role_arn,
                },
            }
        },
    )

    return external_dns_release

def aws_ebs_csi_driver(
    provider,
    eks_sa_role_arn,
    default_storage_class_name: str = "ebs",
    name: str = "aws-ebs-csi-driver",
    chart: str = "aws-ebs-csi-driver",
    version: str = "2.9.0",
    repo: str = "https://kubernetes-sigs.github.io/aws-ebs-csi-driver",
    namespace: str = "default",
    skip_await: bool = False,
    depends_on: list = [] )->Release:

    aws_ebs_csi_driver_release = release(
        name=name,
        chart=chart,
        version=version,
        repo=repo,
        namespace=namespace,
        skip_await=skip_await,
        depends_on=depends_on,
        provider=provider,
        values={
            "storageClasses": [
                {
                    "name": default_storage_class_name,
                    "annotations": {
                        "storageclass.kubernetes.io/is-default-class": "true",
                    },
                    "labels": {},
                    "volumeBindingMode": "WaitForFirstConsumer",
                    "reclaimPolicy": "Retain",
                    "allowVolumeExpansion": True,
                    "parameters": {
                        "encrypted": "true",
                    },
                }
            ],
            "controller": {
                "serviceAccount": {
                    "create": True,
                    "annotations": {
                        "eks.amazonaws.com/role-arn": eks_sa_role_arn,
                    },
                }
            },
            "node": {
                "serviceAccount": {
                    "create": True,
                    "annotations": {
                        "eks.amazonaws.com/role-arn": eks_sa_role_arn,
                    },
                }
            },
        },
    )

    return aws_ebs_csi_driver_release

def karpenter(
    provider,
    eks_sa_role_arn,
    eks_cluster_name,
    eks_cluster_endpoint,
    default_instance_profile_name,
    name: str = "karpenter",
    chart: str = "karpenter",
    version: str = "0.16.3",
    repo: str = "https://charts.karpenter.sh",
    namespace: str = "default",
    skip_await: bool = False,
    depends_on: list = [] )->Release:

    karpenter_release = release(
        name=name,
        chart=chart,
        version=version,
        repo=repo,
        namespace=namespace,
        skip_await=skip_await,
        depends_on=depends_on,
        provider=provider,
        #transformations=[tools.ignore_changes],
        values={
            "serviceAccount": {
                "annotations": {
                    "eks.amazonaws.com/role-arn": eks_sa_role_arn,
                },
            },
            "clusterName": eks_cluster_name,
            "clusterEndpoint": eks_cluster_endpoint,
            "aws": {
                "defaultInstanceProfile": default_instance_profile_name,
            },
        },
    )

    return karpenter_release

def ingress_nginx(
    provider,
    name_suffix: str = "default",
    ssl_enabled: bool = False,
    acm_cert_arns: list[str] = [],
    public: bool = True,
    proxy_protocol: bool = True,
    target_node_labels: list[str] = [],
    alb_resource_tags: dict = { "pulumi-provisioned" : "true" },
    metrics_enabled: bool = False,
    global_rate_limit_enabled: bool = False,
    karpenter_node_enabled: bool = False,
    karpenter_node_provider_name: str = "default",
    name: str = "ingress-nginx",
    chart: str = "ingress-nginx",
    version: str = "4.2.5",
    repo: str = "https://kubernetes.github.io/ingress-nginx",
    namespace: str = "default",
    skip_await: bool = False,
    depends_on: list = [] )->Release:

    karpenter_provisioner_obj = {
        "apiVersion": "karpenter.sh/v1alpha5",
        "kind": "Provisioner",
        "metadata": {
            "labels": {
                "app": f"mc-{name}",
                "ingress": name,
            },
            "name": f"mc-{name}",
        },
        "spec": {
            "consolidation": {
                "enabled": True,
            },
            "labels": {
                "app": f"mc-{name}",
                "ingress": name,
            },
            "taints": [],
            "providerRef": {
                "name": karpenter_node_provider_name,
            },
            "requirements": [
                { "key": "karpenter.k8s.aws/instance-category", "operator": "In", "values": [ "t" ] },
                { "key": "kubernetes.io/arch", "operator": "In", "values": [ "arm64" ] },
                { "key": "kubernetes.io/os", "operator": "In", "values": [ "linux" ] },
                { "key": "karpenter.sh/capacity-type", "operator": "In", "values": [ "spot", "on-demand" ] },
            ],
        },
    }

    karpenter_node_affinity = {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {
                        "matchExpressions": [
                            {
                                "key": "app",
                                "operator": "In",
                                "values": [ f"mc-{name}" ]
                            },
                            {
                                "key": "ingress",
                                "operator": "In",
                                "values": [ name ]
                            }
                        ]
                    }
                ]
            }
        }
    }
    
    default_affinity = {
        "podAntiAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": [
                {
                    "labelSelector": {
                        "matchLabels": {
                            "app": f"mc-{name}",
                            "ingress": name,
                        }
                    },
                    "topologyKey": "kubernetes.io/hostname"
                }
            ]
        }
    }
    
    if karpenter_node_enabled:
        default_affinity.update(karpenter_node_affinity)

    service_annotations = {
        "service.beta.kubernetes.io/aws-load-balancer-name": f"k8s-{name_suffix}",
        "service.beta.kubernetes.io/aws-load-balancer-type": "external",
        "service.beta.kubernetes.io/aws-load-balancer-scheme": "internet-facing" if public else "internal",
        "service.beta.kubernetes.io/aws-load-balancer-nlb-target-type": "instance",
        "service.beta.kubernetes.io/aws-load-balancer-backend-protocol": "tcp",
        "service.beta.kubernetes.io/load-balancer-source-ranges": "0.0.0.0/0",
        "service.beta.kubernetes.io/aws-load-balancer-manage-backend-security-group-rules": True,
        "service.beta.kubernetes.io/aws-load-balancer-connection-idle-timeout": 300,
        "service.beta.kubernetes.io/aws-load-balancer-attributes": "load_balancing.cross_zone.enabled=true",
        "service.beta.kubernetes.io/aws-load-balancer-target-group-attributes": "deregistration_delay.timeout_seconds=10,deregistration_delay.connection_termination.enabled=true",
        # Health check options
        "service.beta.kubernetes.io/aws-load-balancer-healthcheck-protocol": "tcp",
        "service.beta.kubernetes.io/aws-load-balancer-healthcheck-path": "/healthz",
        "service.beta.kubernetes.io/aws-load-balancer-healthcheck-timeout": 2,
        "service.beta.kubernetes.io/aws-load-balancer-healthcheck-healthy-threshold": 5,
        "service.beta.kubernetes.io/aws-load-balancer-healthcheck-unhealthy-threshold": 2,
        "service.beta.kubernetes.io/aws-load-balancer-healthcheck-interval": 5,
        # Proxy protocol options
        "service.beta.kubernetes.io/aws-load-balancer-proxy-protocol": "*" if proxy_protocol else "",
        # Additional AWS resource tags
        "service.beta.kubernetes.io/aws-load-balancer-additional-resource-tags": ",".join([ f"{k}={v}" for k,v in alb_resource_tags.items() ]),
    }

    ssl_enabled_service_annotations = {
        # SSL options
        "service.beta.kubernetes.io/aws-load-balancer-ssl-ports": 443,
        "service.beta.kubernetes.io/aws-load-balancer-ssl-cert": ",".join(acm_cert_arns),
        "service.beta.kubernetes.io/aws-load-balancer-ssl-negotiation-policy": "ELBSecurityPolicy-TLS13-1-2-2021-06",
    }

    target_node_labels_service_annotations = {
        "service.beta.kubernetes.io/aws-load-balancer-target-node-labels": ",".join(target_node_labels),
    }
    
    configmap_settings = {
        "ssl-redirect": False,
        "redirect-to-https": True,
        "use-forwarded-headers": True,
        "use-proxy-protocol": True,
        "skip-access-log-urls": "/healthz,/healthz/",
        "no-tls-redirect-locations": "/healthz,/healthz/",
        "log-format-upstream": '$remote_addr - $host [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" $request_length $request_time [$proxy_upstream_name] [$proxy_alternative_upstream_name] $upstream_addr $upstream_response_length $upstream_response_time $upstream_status $req_id',
        "server-snippet": "if ($proxy_protocol_server_port != '443'){ return 301 https://$host$request_uri; }",
    }
    
    global_rate_limit_configmap_settings = {
        #"http-snippet": "limit_req_zone ${request_method}-${request_uri}-${http_x_custom_header} zone=default:10m rate=50r/s;",
        "global-rate-limit-status-code": 429,
        "global-rate-limit-memcached-host": f"mc-{name}",
        "global-rate-limit-memcached-port": 11211,
    }

    if ssl_enabled:
        service_annotations.update(ssl_enabled_service_annotations)

    if len(target_node_labels) > 0:
        service_annotations.update(target_node_labels_service_annotations)

    if global_rate_limit_enabled:
        configmap_settings.update(global_rate_limit_configmap_settings)
        memcached_release = release(
            name=f"mc-{name}",
            chart="memcached",
            version="6.6.2",
            repo="https://charts.bitnami.com/bitnami",
            namespace=namespace,
            skip_await=skip_await,
            depends_on=depends_on,
            provider=provider,
            timeout=600,
            values={
                "extraDeploy": [] + [karpenter_provisioner_obj] if karpenter_node_enabled else [],
                "fullnameOverride": f"mc-{name}",
                "commonLabels": {
                    "app": f"mc-{name}",
                    "ingress": name,
                },
                "metrics": {
                    "enabled": metrics_enabled,
                    "serviceMonitor": {
                        "enabled": metrics_enabled,
                    }
                },
                "service": {
                    "sessionAffinity": "ClientIP"
                },
                "persistence": {
                    "enabled": False
                },
                "resources": {
                    "limits": {},
                    "requests": {
                        "memory": "256Mi",
                        "cpu": "250m"
                    }
                },
                "architecture": "high-availability",
                "replicaCount": 3,
                "autoscaling": {
                    "enabled": False,
                    "minReplicas": 2,
                    "maxReplicas": 6,
                    "targetCPU": 50,
                    "targetMemory": 50
                },
                "affinity": default_affinity,
                "topologySpreadConstraints": [
                    {
                        "labelSelector": {
                            "matchLabels": {
                                "app": f"mc-{name}",
                                "ingress": name,
                            }
                        },
                        "maxSkew": 1,
                        "topologyKey": "topology.kubernetes.io/zone",
                        "whenUnsatisfiable": "DoNotSchedule"
                    },
                    {
                        "labelSelector": {
                            "matchLabels": {
                                "app": f"mc-{name}",
                                "ingress": name,
                            }
                        },
                        "maxSkew": 1,
                        "topologyKey": "kubernetes.io/hostname",
                        "whenUnsatisfiable": "DoNotSchedule"
                    }
                ]
            }
        )

    ingress_nginx_release = release(
        name=name,
        chart=chart,
        version=version,
        repo=repo,
        namespace=namespace,
        skip_await=skip_await,
        depends_on=depends_on,
        provider=provider,
        timeout=600,
        values={
            "admissionWebhooks": {
                "enabled": True
            },
            "controller": {
                "kind": "DaemonSet",
                "healthCheckPath": "/healthz",
                "lifecycle": {
                    "preStop": {
                        "exec": {
                            "command": [
                                "/wait-shutdown",
                            ]
                        }
                    }
                },
                "priorityClassName": "system-node-critical",
                "ingressClassByName": True,
                "ingressClass": f"nginx-{name_suffix}",
                "ingressClassResource": {
                    "name": f"nginx-{name_suffix}",
                    "enabled": True,
                    "default": False,
                    "controllerValue": f"k8s.io/ingress-nginx-{name_suffix}"
                },
                "electionID": f"ingress-controller-{name_suffix}-leader",
                "config": configmap_settings,
                "containerPort": {
                    "http": 80,
                    "https": 443,
                },
                "service": {
                    "enabled": True,
                    "type": "LoadBalancer",
                    "enableHttp": True,  # Enables the HTTP port (80) on the load balancer
                    "enableHttps": ssl_enabled, # Enables the HTTPS port (443) on the load balancer
                    "ports": {
                        "http": 80,      # Port to open in the load balancer for HTTP traffic
                        "https": 443     # Port to open in the load balancer for HTTPS traffic
                    },
                    "targetPorts": {
                        "http": "http", # Service port 80 is forwarded to DaemonSet port 2443 ( tohttps)
                        "https": "http"    # Service port 443 is forwarded to DaemonSet port 80 (http)
                    },
                    "httpPort": {
                        "enable": True,
                        "targetPort": "http"
                    },
                    "httpsPort": {
                        "enable": ssl_enabled,
                        "targetPort": "http"
                    },
                    # https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.6/guide/service/annotations/
                    "annotations": service_annotations,
                },
                "metrics": {
                    "enabled": metrics_enabled,
                    "serviceMonitor": {
                    "enabled": metrics_enabled,
                    },
                    "prometheusRule": {
                    "enabled": False,
                    "additionalLabels": {},
                    "rules": [],
                    },
                }
            },
        }
    )

    return ingress_nginx_release

def argocd(
    provider,
    ingress_hostname: str,
    ingress_protocol: str,
    ingress_class_name: str,
    argocd_redis_ha_enabled: bool = False,
    argocd_redis_ha_haproxy_enabled: bool = False,
    argocd_redis_ha_storage_class: str = "ebs",
    argocd_redis_ha_storage_size: str = "10Gi",
    argocd_application_controller_replicas: int = 2,
    argocd_applicationset_controller_replicas: int = 2,
    argocd_iam_role_arn: str = "",
    argocd_crds_keep: bool = True,
    argocd_plugins_enabled: bool = False,
    karpenter_node_enabled: bool = False,
    karpenter_node_provider_name: str = "default",
    karpenter_provisioner_controller_instance_category: list[str] = ["t"],
    karpenter_provisioner_controller_instance_arch: list[str] = ["amd64"],
    karpenter_provisioner_controller_instance_capacity_type: list[str] = ["spot"],
    karpenter_provisioner_redis_instance_category: list[str] = ["t"],
    karpenter_provisioner_redis_instance_arch: list[str] = ["arm64"],
    karpenter_provisioner_redis_instance_capacity_type: list[str] = ["spot"],
    controller_resources: dict = {},
    repo_server_resources: dict = {},
    name: str = "argo-cd",
    chart: str = "argo-cd",
    version: str = "5.46.0",
    repo: str = "https://argoproj.github.io/argo-helm",
    namespace: str = "default",
    skip_await: bool = False,
    depends_on: list = [] )->Release:

    plugin_objs = [
        {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "cmp-kustomize-aws-secretsmanager"
            },
            "data": {
                "plugin.yaml": "apiVersion: argoproj.io/v1alpha1\nkind: ConfigManagementPlugin\nmetadata:\n  name: cmp-kustomize-aws-secretsmanager\nspec:\n  version: v1.0\n  init:\n    command: [sh, -c]\n    args:\n      - |\n        find . -type f -name kustomization.yaml\n  generate:\n    command: [sh, -c]\n    args:\n      - |\n        kustomize build . | argocd-vault-plugin generate --verbose-sensitive-output -\n  discover:\n    find:\n      glob: \"./**/kustomization.yaml\"\n"
            }
        }
    ]

    karpenter_provisioner_objs = [
        {
            "apiVersion": "karpenter.sh/v1alpha5",
            "kind": "Provisioner",
            "metadata": {
                "labels": {
                    "app": "argo-cd",
                },
                "name": "argo-cd",
            },
            "spec": {
                "consolidation": {
                    "enabled": True,
                },
                "labels": {
                    "app": "argo-cd",
                },
                "taints": [],
                "providerRef": {
                    "name": karpenter_node_provider_name,
                },
                "requirements": [
                    { "key": "karpenter.k8s.aws/instance-category", "operator": "In", "values": karpenter_provisioner_controller_instance_category },
                    { "key": "kubernetes.io/arch", "operator": "In", "values": karpenter_provisioner_controller_instance_arch },
                    { "key": "kubernetes.io/os", "operator": "In", "values": [ "linux" ] },
                    { "key": "karpenter.sh/capacity-type", "operator": "In", "values": karpenter_provisioner_controller_instance_capacity_type },
                ],
            },
        },
        {
            "apiVersion": "karpenter.sh/v1alpha5",
            "kind": "Provisioner",
            "metadata": {
                "labels": {
                    "app": "redis",
                },
                "name": "redis",
            },
            "spec": {
                "consolidation": {
                    "enabled": True,
                },
                "labels": {
                    "app": "redis",
                },
                "taints": [],
                "providerRef": {
                    "name": karpenter_node_provider_name,
                },
                "requirements": [
                    { "key": "karpenter.k8s.aws/instance-category", "operator": "In", "values": karpenter_provisioner_redis_instance_category },
                    { "key": "kubernetes.io/arch", "operator": "In", "values": karpenter_provisioner_redis_instance_arch },
                    { "key": "kubernetes.io/os", "operator": "In", "values": [ "linux" ] },
                    { "key": "karpenter.sh/capacity-type", "operator": "In", "values": karpenter_provisioner_redis_instance_capacity_type },
                ],
            },
        },
    ]

    extra_objects = []
    if argocd_plugins_enabled:
        extra_objects = extra_objects + plugin_objs
    if karpenter_node_enabled:
        extra_objects = extra_objects + karpenter_provisioner_objs

    karpenter_provisioner_affinity_global = {
        "podAntiAffinity": "soft",
        "nodeAffinity": {
            "type": "hard",
            "matchExpressions": [
                {
                    "key": "app",
                    "operator": "In",
                    "values": ["argo-cd"]
                },
            ],
        },
    }

    karpenter_provisioner_topology_spread_constraints = [
        {
            "maxSkew": 1,
            "topologyKey": "topology.kubernetes.io/zone",
            "whenUnsatisfiable": "DoNotSchedule"
        }
    ]

    karpenter_provisioner_affinity_redis = {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {
                        "matchExpressions": [
                            {
                                "key": "app",
                                "operator": "In",
                                "values": ["redis"]
                            }
                        ],
                    },
                ],
            },
        },
    }

    argocd_release = release(
        name=name,
        chart=chart,
        version=version,
        repo=repo,
        namespace=namespace,
        timeout=600,
        skip_await=skip_await,
        depends_on=depends_on,
        provider=provider,
        values=      {
            "crds": {
                "install": True,
                "keep": argocd_crds_keep,
                "annotations": {},
                "additionalLabels": {},
            },
            "global": {
                "additionalLabels": {
                    "app": "argo-cd"
                },
                "revisionHistoryLimit": 3,
                "affinity": karpenter_provisioner_affinity_global if karpenter_node_enabled else {},
                "topologySpreadConstraints": karpenter_provisioner_topology_spread_constraints if karpenter_node_enabled else [],
            },
            "configs": {
                "cm": {
                    "url": f"{ingress_protocol}://{ingress_hostname}",
                    "exec.enabled": "true",
                    "admin.enabled": "true",
                    "timeout.reconciliation": "180s",
                },
                "params": {
                    # Server
                    "server.insecure": "true",
                    "server.disable.auth": "false",
                    # Application controller
                    "controller.status.processors": 20,
                    "controller.operation.processors": 10,
                    "controller.self.heal.timeout.seconds": 5,
                    "controller.repo.server.timeout.seconds": 60,
                    # ApplicationSet
                    "applicationsetcontroller.policy": "sync",
                    "applicationsetcontroller.enable.progressive.syncs": "false",
                    # Repo server
                    "reposerver.parallelism.limit": 0,
                },
            },
            "redis": {
                "enabled": True,
                "name": "redis",
                "podLabels": {
                    "app": "redis",
                },
                "resources": {
                    "requests": {
                        "cpu": "500m",
                        "memory": "256Mi"
                    },
                    "limits": {
                        "cpu": "1000m",
                        "memory": "512Mi"
                    }
                },
                "affinity": karpenter_provisioner_affinity_redis if karpenter_node_enabled else {},
            },
            "redis-ha": {
                "enabled": argocd_redis_ha_enabled,
                "persistentVolume": {
                    "enabled": "false",
                    "storageClass": argocd_redis_ha_storage_class,
                    "size": argocd_redis_ha_storage_size,
                },
                "redis": {
                    "config": {
                        "save": '"900 1"'
                    }
                },
                "haproxy": {
                    "enabled": argocd_redis_ha_haproxy_enabled,
                    "hardAntiAffinity": True,
                    "affinity": "",
                    "additionalAffinities": karpenter_provisioner_affinity_redis if karpenter_node_enabled else {},
                },
                "topologySpreadConstraints": {
                    "enabled": "true",
                    "maxSkew": 1,
                    "topologyKey": "topology.kubernetes.io/zone",
                    "whenUnsatisfiable": "DoNotSchedule",
                },
                "hardAntiAffinity": True,
                "additionalAffinities": karpenter_provisioner_affinity_redis if karpenter_node_enabled else {},
            },
            "controller": {
                "replicas": argocd_application_controller_replicas,
                "affinity": {},
                "resources": controller_resources,
            },
            "server": {
                "autoscaling": {
                    "enabled": "true",
                    "minReplicas": 2,
                    "maxReplicas": 4,
                },
                "ingress": {
                    "enabled": "true",
                    "ingressClassName": ingress_class_name,
                    "hosts": [ ingress_hostname ],
                    "paths": [ "/" ],
                    "pathType": "Prefix",
                    "extraPaths": [],
                    "tls": [],
                },
            },
            "repoServer": {
                "serviceAccount": {
                    "create": "true",
                    "annotations": {
                        "eks.amazonaws.com/role-arn": argocd_iam_role_arn,
                        "automountServiceAccountToken": "true",
                    },
                },
                # CMP BEGIN
                "volumes": [
                    {
                        "name": "cmp-kustomize-aws-secretsmanager",
                        "configMap": {
                            "name": "cmp-kustomize-aws-secretsmanager"
                        }
                    },
                    {
                        "name": "cmp-tmp",
                        "emptyDir": {}
                    }
                ] if argocd_plugins_enabled else [],
                "extraContainers": [
                    {
                        "name": "cmp-kustomize-aws-secretsmanager",
                        "command": [
                            "/var/run/argocd/argocd-cmp-server"
                        ],
                        "args": [
                            "--loglevel",
                            "debug",
                            "--logformat",
                            "json"
                        ],
                        "image": "luismiguelsaez/argocd-cmp-default:v0.0.2",
                        "securityContext": {
                            "runAsNonRoot": True,
                            "runAsUser": 999,
                            "runAsGroup": 999
                        },
                        "volumeMounts": [
                            {
                                "mountPath": "/var/run/argocd",
                                "name": "var-files"
                            },
                            {
                                "mountPath": "/home/argocd/cmp-server/plugins",
                                "name": "plugins"
                            },
                            {
                                "mountPath": "/home/argocd/cmp-server/config/plugin.yaml",
                                "subPath": "plugin.yaml",
                                "name": "cmp-kustomize-aws-secretsmanager"
                            },
                            {
                                "mountPath": "/tmp",
                                "name": "cmp-tmp"
                            }
                        ],
                        "env": [
                            {
                                "name": "AVP_TYPE",
                                "value": "awssecretsmanager"
                            },
                            {
                                "name": "HOME",
                                "value": "/tmp"
                            }
                        ]
                    }
                ] if argocd_plugins_enabled else [],
                ## CMP END
                "autoscaling": {
                    "enabled": "true",
                    "minReplicas": 2,
                    "maxReplicas": 5,
                },
                "affinity": {},
                "resources": repo_server_resources,
            },
            "applicationSet": {
                "replicas": argocd_applicationset_controller_replicas,
                "resources": controller_resources,
            },
            "extraObjects": extra_objects,
        }
    )

    return argocd_release

def prometheus_stack(
    provider,
    aws_region: str,
    ingress_domain: str,
    ingress_class_name: str,
    storage_class_name: str = "ebs",
    eks_sa_role_arn: str = "",
    thanos_enabled: bool = False,
    prometheus_tsdb_retention: str = "30d",
    prometheus_external_label_env: str = "dev",
    prometheus_crds_enabled: bool = True,
    resources_prometheus: dict = { "requests": { "cpu": "1000m", "memory": "2048Mi" }, "limits": { "cpu": "1000m", "memory": "2048Mi" } },
    karpenter_node_enabled: bool = False,
    karpenter_node_provider_name: str = "default",
    obj_storage_bucket: str = "",
    name_override: str = "prom-stack",
    name: str = "kube-prometheus-stack",
    chart: str = "kube-prometheus-stack",
    version: str = "50.3.1",
    repo: str = "https://prometheus-community.github.io/helm-charts",
    namespace: str = "default",
    skip_await: bool = False,
    depends_on: list = [] )->Release:

    s3_objstore_config = {
        "type": "S3",
        "config": {
            "bucket": obj_storage_bucket,
            "endpoint": f"s3.{aws_region}.amazonaws.com",
            "aws_sdk_auth": True
        }
    }

    s3_objstore_config_str = yaml.dump(s3_objstore_config, default_flow_style=False)

    sidecar_containers = [
        {
            "name": "thanos",
            "image": "quay.io/thanos/thanos:v0.32.2",
            "args": [
                "sidecar",
                "--log.level=debug",
                "--log.format=logfmt",
                "--tsdb.path=/prometheus",
                "--prometheus.url=http://localhost:9090",
                "--http-address=0.0.0.0:10901",
                "--grpc-address=0.0.0.0:10902",
                f"--objstore.config={s3_objstore_config_str}",
            ],
            "env": [],
            "ports": [
                {
                    "name": "http",
                    "containerPort": 10901,
                    "protocol": "TCP"
                },
                {
                    "name": "grpc",
                    "containerPort": 10902,
                    "protocol": "TCP"
                }
            ],
            "volumeMounts": [
                {
                    "mountPath": "/prometheus",
                    "name": f"prometheus-{name_override}-prometheus-db",
                    "subPath": "prometheus-db"
                }
            ],
            "securityContext": {
                "runAsNonRoot": True,
                "runAsUser": 1000,
                "runAsGroup": 2000
            }
        }
    ]

    karpenter_provisioner_obj = {
        "apiVersion": "karpenter.sh/v1alpha5",
        "kind": "Provisioner",
        "metadata": {
            "labels": {
                "app": "prometheus"
            },
            "name": "prometheus"
        },
        "spec": {
            "consolidation": {
                "enabled": False
            },
            "ttlSecondsAfterEmpty": 30,
            "ttlSecondsUntilExpired": 2592000,
            "labels": {
                "karpenter": "enabled",
                "app": "prometheus"
            },
            "taints": [],
            "providerRef": {
                "name": karpenter_node_provider_name
            },
            "requirements": [
                { "key": "karpenter.k8s.aws/instance-category", "operator": "In", "values": ["t"] },
                { "key": "kubernetes.io/arch", "operator": "In", "values": ["amd64", "arm64"] },
                { "key": "kubernetes.io/os", "operator": "In", "values": ["linux"] },
                { "key": "karpenter.sh/capacity-type", "operator": "In", "values": ["on-demand"] }
            ]
        }
    }

    karpenter_provisioner_affinity = {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {
                        "matchExpressions": [
                            { "key": "app", "operator": "In", "values": ["prometheus"] }
                        ]
                    }
                ]
            }
        },
    }

    prom_server_affinity = {
        "podAntiAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": [
                {
                    "topologyKey": "kubernetes.io/hostname",
                    "labelSelector": {
                        "matchLabels": {
                            "app": "prometheus"
                        }
                    }
                }
            ]
        }
    }
    
    if karpenter_node_enabled:
        prom_server_affinity.update(karpenter_provisioner_affinity)

    prometheus_stack_release = release(
        name=name,
        chart=chart,
        version=version,
        repo=repo,
        namespace=namespace,
        timeout=600,
        skip_await=skip_await,
        depends_on=depends_on,
        provider=provider,
        values={
            "crds": {
                "enabled": prometheus_crds_enabled
            },
            # Overridding fullname to avoid name random data volume name
            "fullnameOverride": name_override,
            "prometheusOperator": {
                "enabled": True,
                "logFormat": "logfmt",
                "logLevel": "debug",
                "affinity": {},
                "tolerations": []
            },
            "prometheus": {
                "enabled": True,
                "serviceAccount": {
                    "create": True,
                    "annotations": {
                        "eks.amazonaws.com/role-arn": eks_sa_role_arn,
                    }
                },
                "thanosService": {
                    "enabled": thanos_enabled,
                    "type": "ClusterIP",
                    "clusterIP": "None",
                    "portName": "grpc",
                    "port": 10901,
                    "targetPort": "grpc",
                    "httpPortName": "http",
                    "httpPort": 10902,
                    "targetHttpPort": "http"
                },
                "thanosIngress": {
                    "enabled": thanos_enabled,
                    "ingressClassName": ingress_class_name,
                    "hosts": [
                        f"thanos-gateway.{ingress_domain}"
                    ],
                    "paths": [
                        "/"
                    ],
                    "pathType": "Prefix"
                },
                "ingress": {
                    "enabled": True,
                    "ingressClassName": ingress_class_name,
                    "hosts": [
                        f"prometheus.{ingress_domain}"
                    ],
                    "paths": [
                        "/"
                    ],
                    "pathType": "Prefix",
                    "tls": []
                },
                "prometheusSpec": {
                    "replicas": 3,
                    "replicaExternalLabelName": "prometheus_replica",
                    "prometheusExternalLabelName": "prometheus_instance",
                    "retention": prometheus_tsdb_retention,
                    "disableCompaction": thanos_enabled,
                    "enableAdminAPI": True,
                    "externalLabels": {
                        "env": "dev"
                    },
                    "scrapeInterval": "15s",
                    "scrapeTimeout": "14s",
                    "serviceMonitorSelector": {},
                    "serviceMonitorNamespaceSelector": {},
                    "serviceMonitorSelectorNilUsesHelmValues": False,
                    "podMonitorSelector": {},
                    "podMonitorNamespaceSelector": {},
                    "podMonitorSelectorNilUsesHelmValues": False,
                    "containers": sidecar_containers if thanos_enabled else [],
                    "resources": resources_prometheus,
                    "affinity": prom_server_affinity,
                    "tolerations": [],
                    "podMetadata": {
                        "labels": {
                            "app": "prometheus"
                        }
                    },
                    "topologySpreadConstraints": [
                        {
                            "maxSkew": 1,
                            "topologyKey": "topology.kubernetes.io/zone",
                            "whenUnsatisfiable": "ScheduleAnyway",
                            "labelSelector": {
                                "matchLabels": {
                                    "app": "prometheus"
                                }
                            }
                        },
                        {
                            "maxSkew": 1,
                            "topologyKey": "kubernetes.io/hostname",
                            "whenUnsatisfiable": "ScheduleAnyway",
                            "labelSelector": {
                                "matchLabels": {
                                    "app": "prometheus"
                                }
                            }
                        }
                    ],
                    "storageSpec": {
                        "volumeClaimTemplate": {
                            "spec": {
                                "storageClassName": storage_class_name,
                                "accessModes": ["ReadWriteOnce"],
                                "resources": {
                                    "requests": {
                                        "storage": "20Gi"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "alertmanager": {
                "enabled": True,
                "ingress": {
                "enabled": True,
                    "ingressClassName": ingress_class_name,
                    "hosts": [
                        f"alertmanager.{ingress_domain}"
                    ],
                    "paths": [
                        "/"
                    ],
                    "pathType": "Prefix",
                    "tls": []
                },
                "alertmanagerSpec": {
                    "replicas": 1,
                    "retention": "120h",
                    "storage": {
                        "volumeClaimTemplate": {
                            "spec": {
                                "storageClassName": storage_class_name,
                                "accessModes": ["ReadWriteOnce"],
                                "resources": {
                                    "requests": {
                                        "storage": "20Gi"
                                    }
                                }
                            }
                        }
                    },
                    "affinity": {},
                    "tolerations": []
                }
            },
            "grafana": {
                "enabled": True,
                "adminPassword": "prom-operator",
                "ingress": {
                    "enabled": True,
                    "ingressClassName": ingress_class_name,
                    "hosts": [
                        f"grafana.{ingress_domain}"
                    ],
                    "paths": [
                        "/"
                    ],
                    "pathType": "Prefix",
                    "tls": []
                },
                "sidecar": {
                    "dashboards": {
                        "enabled": True
                    },
                    "datasources": {
                        "enabled": True
                    }
                },
                "additionalDataSources": [
                    {
                        "name": "thanos",
                        "type": "prometheus",
                        "access": "proxy",
                        # Depends on the value of fullnameOverride in the Thanos Stack release
                        "url": "http://thanos-stack-query.prometheus.svc.cluster.local:9090",
                        "isDefault": False
                    }
                ]
            },
            "nodeExporter": {
                "enabled": True
            },
            "extraManifests": [] + [karpenter_provisioner_obj] if karpenter_node_enabled else [],
        }
    )

    return prometheus_stack_release

def thanos_stack(
    provider,
    aws_region: str,
    ingress_domain: str,
    ingress_class_name: str,
    storage_class_name: str,
    eks_sa_role_arn: str = "",
    obj_storage_bucket: str = "",
    compactor_enabled: bool = False,
    compactor_retention_resolution_raw: str = "30d",
    compactor_retention_resolution_5m: str = "90d",
    compactor_retention_resolution_1h: str = "1y",
    karpenter_node_enabled: bool = False,
    karpenter_node_provider_name: str = "default",
    name_override: str = "",
    name: str = "thanos",
    chart: str = "thanos",
    version: str = "12.13.1",
    repo: str = "https://charts.bitnami.com/bitnami",
    namespace: str = "default",
    skip_await: bool = False,
    depends_on: list = [] )->Release:

    karpenter_provisioner_obj = {
        "apiVersion": "karpenter.sh/v1alpha5",
        "kind": "Provisioner",
        "metadata": {
            "labels": {
                "app": "thanos"
            },
            "name": "thanos"
        },
        "spec": {
            "consolidation": {
                "enabled": True
            },
            "labels": {
                "karpenter": "enabled",
                "app": "thanos"
            },
            "taints": [],
            "providerRef": {
                "name": karpenter_node_provider_name
            },
            "requirements": [
                { "key": "karpenter.k8s.aws/instance-category", "operator": "In", "values": ["t"] },
                { "key": "kubernetes.io/arch", "operator": "In", "values": ["arm64"] },
                { "key": "kubernetes.io/os", "operator": "In", "values": ["linux"] },
                { "key": "karpenter.sh/capacity-type", "operator": "In", "values": ["on-demand"] },
            ]
        }
    }

    karpenter_provisioner_affinity = {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {
                        "matchExpressions": [
                            {
                                "key": "app",
                                "operator": "In",
                                "values": [
                                    "thanos"
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    }
    
    query_affinity = {
        "podAntiAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": [
                {
                    "topologyKey": "kubernetes.io/hostname",
                    "labelSelector": {
                        "matchLabels": {
                            "app": "thanos-query"
                        }
                    }
                }
            ]
        }
    }
    
    storegateway_affinity = {
        "podAntiAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": [
                {
                    "topologyKey": "kubernetes.io/hostname",
                    "labelSelector": {
                        "matchLabels": {
                            "app": "thanos-storegateway"
                        }
                    }
                }
            ]
        }
    }
    
    if karpenter_node_enabled:
        query_affinity.update(karpenter_provisioner_affinity)
        storegateway_affinity.update(karpenter_provisioner_affinity)

    s3_objstore_config = {
        "type": "S3",
        "config": {
            "bucket": obj_storage_bucket,
            "endpoint": f"s3.{aws_region}.amazonaws.com",
            "aws_sdk_auth": True
        }
    }

    s3_objstore_config_str = yaml.dump(s3_objstore_config, default_flow_style=False)
    
    thanos_stack_release = release(
        name=name,
        chart=chart,
        version=version,
        repo=repo,
        timeout=600,
        namespace=namespace,
        skip_await=skip_await,
        depends_on=depends_on,
        provider=provider,
        values={
            "fullnameOverride": name_override,
            "extraDeploy": [] + [karpenter_provisioner_obj] if karpenter_node_enabled else [],
            "objstoreConfig": s3_objstore_config_str,
            "query": {
                "enabled": True,
                "replicaCount": 3,
                "podLabels": {
                    "app": "thanos-query"
                },
                "logLevel": "info",
                "logFormat": "logfmt",
                "service": {
                    "type": "ClusterIP",
                    "ports": {
                        "http": 9090
                    },
                    "annotations": {}
                },
                "serviceGrpc": {
                    "type": "ClusterIP",
                    "ports": {
                        "grpc": 10901
                    },
                    "annotations": {}
                },
                "ingress": {
                    "enabled": True,
                    "ingressClassName": ingress_class_name,
                    "annotations": {},
                    "labels": {},
                    "hostname": f"thanos-query.{ingress_domain}",
                    "pathType": "Prefix",
                    "path": "/",
                    "tls": False,
                    "grpc": {
                        "enabled": False,
                        "hostname": f"thanos-query-grpc.{ingress_domain}"
                    }
                },
                "replicaLabel": [
                    "prometheus_replica"
                ],
                "stores": [
                    # Naming based on `fullNameOverride` in `prometheus-stack` release ( prom-stack )
                    "prom-stack-thanos-discovery.prometheus.svc.cluster.local:10902",
                    # Namin based on `fullNameOverride` in `thanos-stack` release ( thanos-stack )
                    "thanos-stack-storegateway.prometheus.svc.cluster.local:10901"
                ],
                "sdConfig": "",
                "resources": {
                    "requests": {
                        "memory": "512Mi",
                        "cpu": "500m"
                    },
                    "limits": {
                        "memory": "1024Mi",
                        "cpu": 1
                    }
                },
                "affinity": query_affinity,
                "topologySpreadConstraints": [
                    {
                        "maxSkew": 1,
                        "topologyKey": "topology.kubernetes.io/zone",
                        "whenUnsatisfiable": "DoNotSchedule",
                        "labelSelector": {
                            "matchLabels": {
                                "app": "thanos-query"
                            }
                        }
                    },
                    {
                        "maxSkew": 1,
                        "topologyKey": "kubernetes.io/hostname",
                        "whenUnsatisfiable": "DoNotSchedule",
                        "labelSelector": {
                            "matchLabels": {
                                "app": "thanos-query"
                            }
                        }
                    }
                ]
            },
            "queryFrontend": {
                "enabled": False,
                "recplicaCount": 1,
                "podLabels": {},
                "logLevel": "info",
                "logFormat": "logfmt"
            },
            "bucketweb": {
                "enabled": True,
                "recplicaCount": 1,
                "podLabels": {
                    "app": "thanos-bucketweb"
                },
                "logLevel": "info",
                "logFormat": "json",
                "refresh": "5m",
                "timeout": "5m",
                "extraFlags": [],
                "serviceAccount": {
                    "create": True,
                    "annotations": {
                        "eks.amazonaws.com/role-arn": eks_sa_role_arn
                    }
                },
                "ingress": {
                    "enabled": True,
                    "ingressClassName": ingress_class_name,
                    "annotations": {},
                    "labels": {},
                    "hostname": f"thanos-bucketweb.{ingress_domain}",
                    "pathType": "Prefix",
                    "path": "/",
                    "tls": False
                },
                "resources": {
                    "requests": {
                        "memory": "128Mi",
                        "cpu": "100m"
                    },
                    "limits": {
                        "memory": "128Mi",
                        "cpu": "100m"
                    }
                },
                "affinity": karpenter_provisioner_affinity if karpenter_node_enabled else {},
            },
            "compactor": {
                "enabled": compactor_enabled,
                "podLabels": {
                    "app": "thanos-compactor"
                },
                "logLevel": "info",
                "logFormat": "logfmt",
                "retentionResolutionRaw": compactor_retention_resolution_raw,
                "retentionResolution5m": compactor_retention_resolution_5m,
                "retentionResolution1h": compactor_retention_resolution_1h,
                "consistencyDelay": "30m",
                "serviceAccount": {
                    "create": True,
                    "annotations": {
                        "eks.amazonaws.com/role-arn": eks_sa_role_arn
                    }
                },
                "resources": {
                    "requests": {
                        "memory": "128Mi",
                        "cpu": "200m"
                    },
                    "limits": {
                        "memory": "256Mi",
                        "cpu": "500m"
                    }
                },
                "affinity": karpenter_provisioner_affinity if karpenter_node_enabled else {},
            },
            "storegateway": {
                "enabled": True,
                "replicaCount": 3,
                "podLabels": {
                    "app": "thanos-storegateway"
                },
                "service": {
                    "type": "ClusterIP",
                    "ports": {
                        "http": 9090,
                        "grpc": 10901
                    },
                    "annotations": {}
                },
                "extraFlags": [],
                "serviceAccount": {
                    "create": True,
                    "annotations": {
                        "eks.amazonaws.com/role-arn": eks_sa_role_arn
                    }
                },
                "ingress": {
                    "enabled": True,
                    "ingressClassName": "nginx-external",
                    "annotations": {},
                    "labels": {},
                    "hostname": f"thanos-storegateway.{ingress_domain}",
                    "pathType": "Prefix",
                    "path": "/",
                    "tls": False,
                    "grpc": {
                        "enabled": False,
                        "hostname": f"thanos-storegateway-grpc.{ingress_domain}"
                    }
                },
                "persistence": {
                    "enabled": True,
                    "storageClass": storage_class_name,
                    "accessModes": [
                        "ReadWriteOnce"
                    ],
                    "size": "8Gi"
                },
                "resources": {
                    "requests": {
                        "memory": "512Mi",
                        "cpu": "500m"
                    },
                    "limits": {
                        "memory": "1024Mi",
                        "cpu": 1
                    }
                },
                "affinity": storegateway_affinity,
                "topologySpreadConstraints": [
                    {
                        "maxSkew": 1,
                        "topologyKey": "topology.kubernetes.io/zone",
                        "whenUnsatisfiable": "DoNotSchedule",
                        "labelSelector": {
                            "matchLabels": {
                                "app": "thanos-storegateway"
                            }
                        }
                    },
                    {
                        "maxSkew": 1,
                        "topologyKey": "kubernetes.io/hostname",
                        "whenUnsatisfiable": "DoNotSchedule",
                        "labelSelector": {
                            "matchLabels": {
                                "app": "thanos-storegateway"
                            }
                        }
                    }
                ]
            },
            "ruler": {
                "enabled": False
            },
            "receive": {
                "enabled": False,
                "replicaCount": 3,
                "podLabels": {},
                "tsdbRetention": "15d",
                "replicationFactor": 2,
                "logLevel": "debug",
                "logFormat": "logfmt",
                "service": {
                    "type": "ClusterIP",
                    "ports": {
                        "http": 10902,
                        "grpc": 10901,
                        "remote": 19291
                    },
                    "annotations": {}
                },
                "replicaLabel": "replica"
            },
            "receiveDistributor": {
                "enabled": False
            },
            "metrics": {
                "enabled": False
            }
        }
    )
    
    return thanos_stack_release

"""
Opensearch cluster release
"""
def opensearch(
    provider,
    ingress_domain: str,
    ingress_class_name: str,
    storage_class_name: str,
    storage_size: str = "20Gi",
    name_override: str = "",
    karpenter_node_enabled: bool = True,
    karpenter_node_provider_name: str = "default",
    replicas: int = 3,
    resources_requests_memory_mb: str = "2000",
    resources_requests_cpu: str = "1000m",
    resources_limits_memory_mb: str = "2000",
    resources_limits_cpu: str = "1000m",
    name: str = "opensearch",
    chart: str = "opensearch",
    version: str = "2.14.1",
    repo: str = "https://opensearch-project.github.io/helm-charts",
    namespace: str = "default",
    skip_await: bool = False,
    depends_on: list = [] )->Release:

    karpenter_provisioner_obj = {
        "apiVersion": "karpenter.sh/v1alpha5",
        "kind": "Provisioner",
        "metadata": {
            "labels": {
            "app": "opensearch"
            },
            "name": "opensearch"
        },
        "spec": {
            "consolidation": {
                "enabled": True
            },
            "labels": {
                "karpenter": "enabled",
                "app": "opensearch"
            },
            "taints": [],
            "providerRef": {
                "name": karpenter_node_provider_name
            },
            "requirements": [
                { "key": "karpenter.k8s.aws/instance-category", "operator": "In", "values": ["r"] },
                { "key": "kubernetes.io/arch", "operator": "In", "values": ["arm64"] },
                { "key": "kubernetes.io/os", "operator": "In", "values": ["linux"] },
                { "key": "karpenter.sh/capacity-type", "operator": "In", "values": ["on-demand"] },
            ]
        }
    }

    karpenter_provisioner_affinity = {
        "requiredDuringSchedulingIgnoredDuringExecution": {
            "nodeSelectorTerms": [
                {
                    "matchExpressions": [
                        {
                            "key": "karpenter",
                            "operator": "In",
                            "values": [
                                "enabled"
                            ]
                        },
                        {
                            "key": "app",
                            "operator": "In",
                            "values": [
                                "opensearch"
                            ]
                        }
                    ]
                }
            ]
        }
    }

    opensearch_release = release(
        name=name,
        chart=chart,
        version=version,
        repo=repo,
        namespace=namespace,
        timeout=600,
        skip_await=skip_await,
        depends_on=depends_on,
        provider=provider,
        values={
            "fullnameOverride:": name_override,
            "singleNode": False if replicas > 1 else True,
            "roles": [
                "master",
                "ingest",
                "data",
                "remote_cluster_client"
            ],
            "replicas": replicas,
            "config": {
                "log4j2.properties": "status = error\n\nappender.console.type = Console\nappender.console.name = console\nappender.console.layout.type = PatternLayout\nappender.console.layout.pattern = [%d{ISO8601}][%-5p][%-25c{1.}] [%node_name]%marker %m%n\n\nrootLogger.level = info\nrootLogger.appenderRef.console.ref = console",
                "opensearch.yml": "cluster.name: test\nnetwork.host: 0.0.0.0\nplugins:\n  security:\n    disabled: true\n    ssl:\n      transport:\n        pemcert_filepath: esnode.pem\n        pemkey_filepath: esnode-key.pem\n        pemtrustedcas_filepath: root-ca.pem\n        enforce_hostname_verification: false\n      http:\n        enabled: false\n        pemcert_filepath: esnode.pem\n        pemkey_filepath: esnode-key.pem\n        pemtrustedcas_filepath: root-ca.pem\n    nodes_dn_dynamic_config_enabled: true\n    nodes_dn:\n      - \"CN=*.example.com, OU=node, O=node, L=test, C=de\"\n    allow_unsafe_democertificates: true\n    allow_default_init_securityindex: true\n    authcz:\n      admin_dn:\n        - CN=kirk,OU=client,O=client,L=test,C=de\n    audit.type: internal_opensearch\n    enable_snapshot_restore_privilege: true\n    check_snapshot_restore_write_privileges: true\n    restapi:\n      roles_enabled: [\"all_access\", \"security_rest_api_access\"]\n    system_indices:\n      enabled: false\n      indices:\n        [\n          \".opendistro-alerting-config\",\n          \".opendistro-alerting-alert*\",\n          \".opendistro-anomaly-results*\",\n          \".opendistro-anomaly-detector*\",\n          \".opendistro-anomaly-checkpoints\",\n          \".opendistro-anomaly-detection-state\",\n          \".opendistro-reports-*\",\n          \".opendistro-notifications-*\",\n          \".opendistro-notebooks\",\n          \".opendistro-asynchronous-search-response*\",\n        ]"
            },
            "opensearchJavaOpts": f"-Xmx{int(int(resources_requests_memory_mb) / 2)}M -Xms{int(int(resources_limits_memory_mb) / 2)}M",
            "resources": {
                "requests": {
                    "cpu": resources_requests_cpu,
                    "memory": f"{resources_requests_memory_mb}Mi"
                },
                "limits": {
                    "cpu": resources_limits_cpu,
                    "memory": f"{resources_limits_memory_mb}Mi"
                }
            },
            "persistence": {
                "enabled": True,
                "storageClass": storage_class_name,
                "accessModes": ["ReadWriteOnce"],
                "size": storage_size
            },
            "nodeSelector": {},
            "tolerations": [],
            "labels": {
                "app": "opensearch"
            },
            "topologySpreadConstraints": [
                {
                    "maxSkew": 1,
                    "topologyKey": "topology.kubernetes.io/zone",
                    "whenUnsatisfiable": "ScheduleAnyway",
                    "labelSelector": {
                        "matchLabels": {
                        "app": "opensearch"
                        }
                }
                },
                {
                    "maxSkew": 1,
                    "topologyKey": "kubernetes.io/hostname",
                    "whenUnsatisfiable": "ScheduleAnyway",
                    "labelSelector": {
                        "matchLabels": {
                        "app": "opensearch"
                        }
                    }
                }
            ],
            "antiAffinityTopologyKey": "kubernetes.io/hostname",
            "antiAffinity": "hard",
            "nodeAffinity": karpenter_provisioner_affinity if karpenter_node_enabled else {},
            "ingress": {
                "enabled": True,
                "ingressClassName": ingress_class_name,
                "hosts": [
                    f"opensearch.{ingress_domain}"
                ],
                "path": "/",
                "tls": []
            },
            "extraObjects": [] + [karpenter_provisioner_obj] if karpenter_node_enabled else []
        }
    )

    return opensearch_release

def loki(
    provider,
    aws_region: str,
    ingress_domain: str,
    ingress_class_name: str,
    storage_class_name: str,
    storage_size_read: str = "5Gi",
    storage_size_write: str = "5Gi",
    storage_size_backend: str = "5Gi",
    tablemanager_retention_period: str = "7d",
    eks_sa_role_arn: str = "",
    obj_storage_bucket: str = "",
    metrics_enabled: bool = False,
    singlebinary_enabled: bool = True,
    resources_singlebinary: dict = { "requests": { "cpu": "500m", "memory": "1024Mi" }, "limits": { "cpu": "1000m", "memory": "2048Mi" } },
    resources_read: dict = { "requests": { "cpu": "500m", "memory": "1024Mi" }, "limits": { "cpu": "1000m", "memory": "2048Mi" } },
    resources_write: dict = { "requests": { "cpu": "500m", "memory": "1024Mi" }, "limits": { "cpu": "1000m", "memory": "2048Mi" } },
    resources_backend: dict = { "requests": { "cpu": "500m", "memory": "1024Mi" }, "limits": { "cpu": "1000m", "memory": "2048Mi" } },
    resources_gateway: dict = { "requests": { "cpu": "100m", "memory": "128Mi" }, "limits": { "cpu": "250m", "memory": "256Mi" } },
    replicas_read: int = 3,
    replicas_write: int = 3,
    replicas_backend: int = 3,
    replicas_gateway: int = 3,
    replicas_single_binary: int = 3,
    autoscaling_enabled: bool = False,
    autoscaling_min_replicas: int = 2,
    autoscaling_max_replicas: int = 5,
    karpenter_node_enabled: bool = True,
    karpenter_node_provider_name: str = "default",
    name_override: str = "",
    name: str = "loki",
    chart: str = "loki",
    version: str = "5.21.0",
    repo: str = "https://grafana.github.io/helm-charts",
    namespace: str = "default",
    skip_await: bool = False,
    depends_on: list = [] )->(Release, Release):

    karpenter_provisioner_affinity = {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {
                        "matchExpressions": [
                            {
                                "key": "app",
                                "operator": "In",
                                "values": ["loki"]
                            }
                        ],
                    },
                ],
            },
        },
    }
    
    read_affinity = {
        "podAntiAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": [
                {
                    "topologyKey": "kubernetes.io/hostname",
                    "labelSelector": {
                        "matchLabels": {
                            "component": "read"
                        }
                    }
                }
            ]
        }
    }

    write_affinity = {
        "podAntiAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": [
                {
                    "topologyKey": "kubernetes.io/hostname",
                    "labelSelector": {
                        "matchLabels": {
                            "component": "write"
                        }
                    }
                }
            ]
        }
    }

    backend_affinity = {
        "podAntiAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": [
                {
                    "topologyKey": "kubernetes.io/hostname",
                    "labelSelector": {
                        "matchLabels": {
                            "component": "backend"
                        }
                    }
                }
            ]
        }
    }

    gateway_affinity = {
        "podAntiAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": [
                {
                    "topologyKey": "kubernetes.io/hostname",
                    "labelSelector": {
                        "matchLabels": {
                            "component": "gateway"
                        }
                    }
                }
            ]
        }
    }

    singlebinary_affinity = {
        "podAntiAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": [
                {
                    "topologyKey": "kubernetes.io/hostname",
                    "labelSelector": {
                        "matchLabels": {
                            "component": "singlebinary"
                        }
                    }
                }
            ]
        }
    }

    if karpenter_node_enabled:
        read_affinity.update(karpenter_provisioner_affinity)
        write_affinity.update(karpenter_provisioner_affinity)
        backend_affinity.update(karpenter_provisioner_affinity)
        gateway_affinity.update(karpenter_provisioner_affinity)
        singlebinary_affinity.update(karpenter_provisioner_affinity)

    read_affinity_str = yaml.dump(read_affinity, default_flow_style=False)
    write_affinity_str = yaml.dump(write_affinity, default_flow_style=False)
    backend_affinity_str = yaml.dump(backend_affinity, default_flow_style=False)
    gateway_affinity_str = yaml.dump(gateway_affinity, default_flow_style=False)
    singlebinary_affinity_str = yaml.dump(singlebinary_affinity, default_flow_style=False)

    karpenter_provisioner_obj = {
        "apiVersion": "karpenter.sh/v1alpha5",
        "kind": "Provisioner",
        "metadata": {
            "labels": {
                "app": "loki",
            },
            "name": "loki",
        },
        "spec": {
            "consolidation": {
                "enabled": True,
            },
            "labels": {
                "app": "loki",
            },
            "taints": [],
            "providerRef": {
                "name": karpenter_node_provider_name,
            },
            "requirements": [
                { "key": "karpenter.k8s.aws/instance-category", "operator": "In", "values": [ "t" ] },
                { "key": "kubernetes.io/arch", "operator": "In", "values": [ "arm64" ] },
                { "key": "kubernetes.io/os", "operator": "In", "values": [ "linux" ] },
                { "key": "karpenter.sh/capacity-type", "operator": "In", "values": [ "spot", "on-demand" ] },
            ],
        },
    }

    promtail_release = release(
        name="promtail",
        chart="promtail",
        version="6.15.1",
        repo=repo,
        timeout=600,
        namespace=namespace,
        skip_await=skip_await,
        depends_on=depends_on,
        provider=provider,
        values={
            "daemonset": {
                "enabled": True,
            },
            "config": {
                "clients": [
                    {
                        #"url": f"http://loki-gateway.{namespace}.svc.cluster.local/loki/api/v1/push",
                        "url": pulumi.Output.concat("http://loki-gateway.", namespace, ".svc.cluster.local/loki/api/v1/push"),
                        "tenant_id": "default",
                    }
                ]
            }
        }
    )

    loki_release = release(
        name=name,
        chart=chart,
        version=version,
        repo=repo,
        timeout=600,
        namespace=namespace,
        skip_await=skip_await,
        depends_on=depends_on,
        provider=provider,
        values={
            "fullnameOverride": name_override,
            "serviceAccount": {
                "create": True,
                "annotations": {
                    "eks.amazonaws.com/role-arn": eks_sa_role_arn,
                },
            },
            "loki": {
                "podLabels": {
                    "app": "loki",
                },
                "serviceLabels": {},
                "auth_enabled": False,
                "monitoring": {
                    "dashboards": {
                        "enabled": True,
                        "labels": {
                            "grafana_dashboard": 1,
                        },
                    },
                    "serviceMonitor": {
                        "enabled": metrics_enabled,
                    },
                    "lokiCanary": {
                        "enabled": True,
                    },
                },
                "memcached": {
                    "chunk_cache": {
                        "enabled": True,
                        "host": "",
                        "service": "memcached-client",
                        "batch_size": 256,
                        "parallelism": 10
                    },
                    "results_cache": {
                        "enabled": True,
                        "host": "",
                        "service": "memcached-client",
                        "timeout": "500ms",
                        "default_validity": "12h"
                    }
                },
                "compactor": {},
                "analytics": {},
                "querier": {},
                "ingester": {},
                "storage": {
                    "bucketNames": {
                        "chunks": obj_storage_bucket if obj_storage_bucket != "" else "chunks",
                        "ruler": obj_storage_bucket if obj_storage_bucket != "" else "ruler",
                        "admin": obj_storage_bucket if obj_storage_bucket != "" else "admin"
                    },
                    "type": "s3" if obj_storage_bucket != "" else "filesystem",
                    # https://grafana.com/docs/loki/latest/storage/#aws-deployment-s3-single-store
                    # https://github.com/grafana/loki/issues/5437
                    "s3": {
                        "s3": f"s3://{aws_region}/{obj_storage_bucket}" if obj_storage_bucket != "" else "null",
                    },
                    "filesystem": {
                        "chunks_directory": "/data/loki/chunks",
                        "rules_directory": "/data/loki/rules",
                    },
                }
            },
            "tableManager:": {
                "enabled": True,
                "retention_deletes_enabled": True,
                "retention_period": tablemanager_retention_period,
                "affinity": karpenter_provisioner_affinity if karpenter_node_enabled else {},
            },
            "ingress": {
                "enabled": True,
                "ingressClassName": ingress_class_name,
                "paths": {
                    "write": [
                        "/api/prom/push",
                        "/loki/api/v1/push"],
                    "read": [
                        "/api/prom/tail",
                        "/loki/api/v1/tail",
                    ],
                },
                "hosts": [
                    f"loki.{ingress_domain}"
                ]
            },
            # Enabling single binary mode will disable the `read`, `write` and `backend` components
            "singleBinary": {
                "replicas": replicas_single_binary if singlebinary_enabled else 0,
                "autoscaling": {
                    "enabled": autoscaling_enabled if obj_storage_bucket != "" else False,
                    "minReplicas": autoscaling_min_replicas,
                    "maxReplicas": autoscaling_max_replicas,
                    "targetCPUUtilizationPercentage": 60,
                    "behavior": {},
                },
                "podLabels": {
                    "component": "singlebinary"
                },
                "resources": resources_singlebinary,
                "affinity": singlebinary_affinity_str,
            },
            "write": {
                "replicas": replicas_write if obj_storage_bucket != "" else 1,
                "autoscaling": {
                    "enabled": autoscaling_enabled if obj_storage_bucket != "" else False,
                    "minReplicas": autoscaling_min_replicas,
                    "maxReplicas": autoscaling_max_replicas,
                    "targetCPUUtilizationPercentage": 60,
                    "behavior": {},
                },
                "persistence": {
                    "size": storage_size_write,
                    "storageClass": storage_class_name,
                },
                "podLabels": {
                    "component": "write"
                },
                "resources": resources_write,
                "affinity": write_affinity_str,
            },
            "read": {
                "replicas": replicas_read if obj_storage_bucket != "" else 1,
                "autoscaling": {
                    "enabled": autoscaling_enabled if obj_storage_bucket != "" else False,
                    "minReplicas": autoscaling_min_replicas,
                    "maxReplicas": autoscaling_max_replicas,
                    "targetCPUUtilizationPercentage": 60,
                    "behavior": {},
                },
                "persistence": {
                    "size": storage_size_read,
                    "storageClass": storage_class_name,
                },
                "podLabels": {
                    "component": "read"
                },
                "resources": resources_read,
                "affinity": read_affinity_str,
            },
            "backend": {
                "replicas": replicas_backend if obj_storage_bucket != "" else 1,
                "autoscaling": {
                    "enabled": autoscaling_enabled if obj_storage_bucket != "" else False,
                    "minReplicas": autoscaling_min_replicas,
                    "maxReplicas": autoscaling_max_replicas,
                    "targetCPUUtilizationPercentage": 60,
                    "behavior": {},
                },
                "persistence": {
                    "size": storage_size_backend,
                    "storageClass": storage_class_name,
                },
                "podLabels": {
                    "component": "backend"
                },
                "resources": resources_backend,
                "affinity": backend_affinity_str,
            },
            "gateway": {
                "enabled": True,
                "replicas": replicas_gateway,
                "autoscaling": {
                    "enabled": autoscaling_enabled,
                    "minReplicas": autoscaling_min_replicas,
                    "maxReplicas": autoscaling_max_replicas,
                    "targetCPUUtilizationPercentage": 60,
                    "behavior": {},
                },
                "podLabels": {
                    "component": "gateway"
                },
                "resources": resources_gateway,
                "affinity": gateway_affinity_str,
            },
            "test": {
                "enabled": False,
            },
            "extraObjects": [] + [karpenter_provisioner_obj] if karpenter_node_enabled else [],
        }
    )

    return loki_release, promtail_release
