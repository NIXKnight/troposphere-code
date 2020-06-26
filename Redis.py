from troposphere import Template, Ref, Sub, ImportValue, Parameter
from troposphere.elasticache import ReplicationGroup

redis_replication_cluster = Template()
redis_replication_cluster.add_version('2010-09-09')
redis_replication_cluster.add_description('3 Node ElastiCache Redis cluster.')

redis_cluster_group_name_parameter = redis_replication_cluster.add_parameter(
  Parameter(
    'ElastiCacheGroupName',
    Default="ucsd-prod-redis",
    Description="Number of cache nodes within the ElastiCache Redis cluster.",
    Type="String"
  )
)

redis_cluster_nodes_parameter = redis_replication_cluster.add_parameter(
  Parameter(
    'ClusterNodes',
    Default="2",
    Description="Number of cache nodes within the ElastiCache Redis cluster.",
    Type="String"
  )
)

redis_cluster_instance_type_parameter = redis_replication_cluster.add_parameter(
  Parameter(
    'InstanceType',
    Default="cache.m3.medium",
    AllowedValues=[
      "cache.m5.large", "cache.m5.xlarge", "cache.m5.2xlarge", "cache.m5.4xlarge", "cache.m5.12xlarge", "cache.m5.24xlarge",
      "cache.m4.large", "cache.m4.xlarge", "cache.m4.2xlarge", "cache.m4.4xlarge", "cache.m4.10xlarge", "cache.t2.micro",
      "cache.t2.small", "cache.t2.medium", "cache.t1.micro", "cache.m1.small", "cache.m1.medium", "cache.m1.large",
      "cache.m1.xlarge", "cache.m3.medium", "cache.m3.large", "cache.m3.xlarge", "cache.m3.2xlarge", "cache.c1.xlarge",
      "cache.r5.large", "cache.r5.xlarge", "cache.r5.2xlarge", "cache.r5.4xlarge", "cache.r5.12xlarge", "cache.r5.24xlarge",
      "cache.r4.large", "cache.r4.xlarge", "cache.r4.2xlarge", "cache.r4.4xlarge", "cache.r4.8xlarge", "cache.r4.16xlarge",
      "cache.m2.xlarge", "cache.m2.2xlarge", "cache.m2.4xlarge", "cache.r3.large", "cache.r3.xlarge", "cache.r3.2xlarge",
      "cache.r3.4xlarge", "cache.r3.8xlarge"
    ],
    Type="String"
  )
)

redis_cluster_engine_parameter = redis_replication_cluster.add_parameter(
  Parameter(
    'ElastiCacheEngine',
    Default="redis",
    Description="ElastiCache engine.",
    Type="String"
  )
)

redis_cluster_engine_version_parameter = redis_replication_cluster.add_parameter(
  Parameter(
    'ElastiCacheEngineVersion',
    Default="3.2.10",
    Description="Default RDS database engine version.",
    Type="String"
  )
)

redis_cluster_failover_parameter = redis_replication_cluster.add_parameter(
  Parameter(
    'AutoFailover',
    Default="True",
    AllowedValues=[ "True", "False" ],
    Description="Enable Multi-AZ Failover. This is not supported on cache.t2.* instances.",
    Type="String"
  )
)

redis_cluster_sec_group_parameter = redis_replication_cluster.add_parameter(
  Parameter(
    'SecurityGroups',
    Description="ElastiCache security group.",
    Type="List<AWS::EC2::SecurityGroup::Id>"
  )
)

redis_cluster_subnet_group_stack_parameter = redis_replication_cluster.add_parameter(
  Parameter(
    'DBSGDefStackName',
    Default="",
    Description="Stack name containing exported ElastiCache subnet group.",
    Type="String"
  )
)

redis_cluster_resource = redis_replication_cluster.add_resource(
  ReplicationGroup(
    "RedisReplicationGroup",
    ReplicationGroupDescription=redis_replication_cluster.description,
    ReplicationGroupId=Ref(redis_cluster_group_name_parameter),
    AutomaticFailoverEnabled=Ref(redis_cluster_failover_parameter),
    SecurityGroupIds=Ref(redis_cluster_sec_group_parameter),
    CacheNodeType=Ref(redis_cluster_instance_type_parameter),
    NumNodeGroups='1',
    ReplicasPerNodeGroup=Ref(redis_cluster_nodes_parameter),
    Engine=Ref(redis_cluster_engine_parameter),
    EngineVersion=Ref(redis_cluster_engine_version_parameter),
    CacheSubnetGroupName=ImportValue(Sub("${" + redis_cluster_subnet_group_stack_parameter.title + "}"+ "-" + "ElastiCacheSubnetGroup"))
  )
)

with open("Redis.yaml", "w") as file:
  file.write(redis_replication_cluster.to_yaml())
