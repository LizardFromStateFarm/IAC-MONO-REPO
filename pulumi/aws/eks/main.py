"""
Pulumi configuration for AWS EKS cluster
"""
import pulumi
import pulumi_aws as aws
import pulumi_kubernetes as k8s

# Configuration
config = pulumi.Config()
cluster_name = config.get("cluster_name") or "pulumi-eks"
node_count = config.get_int("node_count") or 2
instance_type = config.get("instance_type") or "t3.medium"

# VPC and networking
vpc = aws.ec2.Vpc("eks-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        "Name": f"{cluster_name}-vpc",
        "kubernetes.io/cluster/{cluster_name}": "shared",
    })

# Internet Gateway
igw = aws.ec2.InternetGateway("eks-igw",
    vpc_id=vpc.id,
    tags={"Name": f"{cluster_name}-igw"})

# Subnets
subnet1 = aws.ec2.Subnet("eks-subnet-1",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="us-west-2a",
    map_public_ip_on_launch=True,
    tags={
        "Name": f"{cluster_name}-subnet-1",
        "kubernetes.io/cluster/{cluster_name}": "shared",
        "kubernetes.io/role/elb": "1",
    })

subnet2 = aws.ec2.Subnet("eks-subnet-2",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    availability_zone="us-west-2b",
    map_public_ip_on_launch=True,
    tags={
        "Name": f"{cluster_name}-subnet-2",
        "kubernetes.io/cluster/{cluster_name}": "shared",
        "kubernetes.io/role/elb": "1",
    })

# Route table
route_table = aws.ec2.RouteTable("eks-rt",
    vpc_id=vpc.id,
    tags={"Name": f"{cluster_name}-rt"})

# Route
route = aws.ec2.Route("eks-route",
    route_table_id=route_table.id,
    destination_cidr_block="0.0.0.0/0",
    gateway_id=igw.id)

# Route table associations
rt_assoc1 = aws.ec2.RouteTableAssociation("eks-rta-1",
    subnet_id=subnet1.id,
    route_table_id=route_table.id)

rt_assoc2 = aws.ec2.RouteTableAssociation("eks-rta-2",
    subnet_id=subnet2.id,
    route_table_id=route_table.id)

# Security group for EKS cluster
cluster_sg = aws.ec2.SecurityGroup("eks-cluster-sg",
    vpc_id=vpc.id,
    description="Security group for EKS cluster",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={"Name": f"{cluster_name}-cluster-sg"})

# EKS cluster
cluster = aws.eks.Cluster("eks-cluster",
    name=cluster_name,
    role_arn=aws.iam.Role("eks-role",
        assume_role_policy="""{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "Service": "eks.amazonaws.com"
                    },
                    "Effect": "Allow"
                }
            ]
        }""",
        managed_policy_arns=[
            "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
        ]).arn,
    vpc_config=aws.eks.ClusterVpcConfigArgs(
        subnet_ids=[subnet1.id, subnet2.id],
        security_group_ids=[cluster_sg.id],
    ),
    tags={"Name": cluster_name})

# Node group
node_group = aws.eks.NodeGroup("eks-node-group",
    cluster_name=cluster.name,
    node_group_name=f"{cluster_name}-nodes",
    node_role_arn=aws.iam.Role("eks-node-role",
        assume_role_policy="""{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Effect": "Allow"
                }
            ]
        }""",
        managed_policy_arns=[
            "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
            "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
            "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
        ]).arn,
    subnet_ids=[subnet1.id, subnet2.id],
    scaling_config=aws.eks.NodeGroupScalingConfigArgs(
        desired_size=node_count,
        max_size=node_count + 1,
        min_size=1,
    ),
    instance_types=[instance_type],
    tags={"Name": f"{cluster_name}-nodes"})

# Export outputs
pulumi.export("cluster_name", cluster.name)
pulumi.export("cluster_endpoint", cluster.endpoint)
pulumi.export("cluster_version", cluster.version)
pulumi.export("vpc_id", vpc.id)
