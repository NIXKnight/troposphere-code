from troposphere import Template, Ref, Sub, ImportValue, Parameter
from troposphere.elasticache import CacheCluster

memcached_cluster = Template()
memcached_cluster.add_version('2010-09-09')
memcached_cluster.add_description('3 Node ElastiCache Redis cluster.')

memcached_group_name_parameter = memcached_cluster.add_parameter(
  Parameter(
    'ElastiCacheGroupName',
    Default="ucsd-prod-memcached",
    Description="Number of cache nodes within the ElastiCache Memcached cluster.",
    Type="String"
  )
)

memcached_nodes_parameter = memcached_cluster.add_parameter(
  Parameter(
    'ClusterNodes',
    Default="2",
    Description="Number of cache nodes within the ElastiCache Memcached cluster.",
    Type="String"
  )
)

memcached_instance_type_parameter = memcached_cluster.add_parameter(
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

memcached_engine_parameter = memcached_cluster.add_parameter(
  Parameter(
    'ElastiCacheEngine',
    Default=" memcached",
    Description="ElastiCache engine.",
    Type="String"
  )
)

memcached_engine_version_parameter = memcached_cluster.add_parameter(
  Parameter(
    'ElastiCacheEngineVersion',
    Default="1.5.10",
    Description="Default RDS database engine version.",
    Type="String"
  )
)

memcached_sec_group_parameter = memcached_cluster.add_parameter(
  Parameter(
    'SecurityGroups',
    Description="ElastiCache security group.",
    Type="List<AWS::EC2::SecurityGroup::Id>"
  )
)

memcached_subnet_group_stack_parameter = memcached_cluster.add_parameter(
  Parameter(
    'DBSGDefStackName',
    Default="",
    Description="Stack name containing exported ElastiCache subnet group.",
    Type="String"
  )
)

memcached_multiaz_parameter = memcached_cluster.add_parameter(
  Parameter(
    'DBEngineVersion',
    Default="cross-az",
    Description="Default RDS database engine version.",
    Type="String",
    AllowedValues=[ "single-az", "cross-az" ]
  )
)

memcached_resource = memcached_cluster.add_resource(
  CacheCluster(
    "MemcachedCluster",
    ClusterName=Ref(memcached_group_name_parameter),
    AZMode=Ref(memcached_multiaz_parameter),
    VpcSecurityGroupIds=Ref(memcached_sec_group_parameter),
    CacheNodeType=Ref(memcached_instance_type_parameter),
    NumCacheNodes=Ref(memcached_nodes_parameter),
    Engine=Ref(memcached_engine_parameter),
    EngineVersion=Ref(memcached_engine_version_parameter),
    CacheSubnetGroupName=ImportValue(Sub("${" + memcached_subnet_group_stack_parameter.title + "}"+ "-" + "ElastiCacheSubnetGroup"))
  )
)

with open("Memcached.yaml", "w") as file:
  file.write(memcached_cluster.to_yaml())
