from troposphere import Template, Ref, Sub, ImportValue, Parameter, Select, GetAZs
from troposphere.rds import DBCluster, DBInstance

aurora = Template()
aurora.add_version('2010-09-09')
aurora.add_description('Aurora stack.')

aurora_identifier_parameter = aurora.add_parameter(
  Parameter(
    'ClusterIdentifier',
    Default="ucsd-edx-prod",
    Description="Name that is unique for all DB instances owned by your AWS account in the current region.",
    Type="String"
  )
)
aurora_type_parameter = aurora.add_parameter(
  Parameter(
    'ClusterType',
    Default="db.t2.medium",
    AllowedValues=[
      "db.r4.16xlarge", "db.r4.8xlarge", "db.r4.4xlarge", "db.r4.2xlarge", "db.r4.xlarge", "db.r4.large", "db.r3.8xlarge", "db.r3.4xlarge",
      "db.r3.2xlarge", "db.r3.xlarge", "db.r3.large", "db.t2.medium", "db.t2.small"
    ],
    Type="String"
  )
)

aurora_db_engine_parameter = aurora.add_parameter(
  Parameter(
    'DBEngine',
    Default="aurora",
    Description="Default RDS database engine.",
    Type="String"
  )
)

aurora_db_engine_version_parameter = aurora.add_parameter(
  Parameter(
    'DBEngineVersion',
    Default="5.6.10a",
    Description="RDS engine version.",
    Type="String",
    AllowedValues=[ "5.6.10a", "5.7.12" ]
  )
)

aurora_storage_encryption_parameter = aurora.add_parameter(
  Parameter(
    'EncryptionAtRest',
    Default="False",
    Description="Encrypt database storage.",
    Type="String",
    AllowedValues=[ "True", "False" ]
  )
)

aurora_public_parameter = aurora.add_parameter(
  Parameter(
    'PublicAccessibility',
    Default="False",
    Description="Make Aurora publically accessible.",
    Type="String",
    AllowedValues=[ "True", "False" ]
  )
)

aurora_db_master_user_parameter = aurora.add_parameter(
  Parameter(
    'DBMasterUser',
    Default="dbadmin",
    Description="Default master username for RDS instance.",
    Type="String"
  )
)

aurora_db_master_password_parameter = aurora.add_parameter(
  Parameter(
    'DBMasterPassword',
    Default="",
    Description="Default master password for RDS instance.",
    NoEcho=True,
    Type="String"
  )
)

aurora_multiaz_parameter = aurora.add_parameter(
  Parameter(
    'MultiAZ',
    Default="True",
    AllowedValues=[ "True", "False" ],
    Description="Setup RDS with Multi-AZ deployment.",
    Type="String"
  )
)

aurora_sec_group_parameter = aurora.add_parameter(
  Parameter(
    'SecurityGroups',
    Description="RDS security group.",
    Type="List<AWS::EC2::SecurityGroup::Id>"
  )
)

aurora_subnet_group_stack_parameter = aurora.add_parameter(
  Parameter(
    'NetworkStackName',
    Default="",
    Description="Stack name containing exported RDS subnet group.",
    Type="String"
  )
)

aurora_subnet_group_name = "${" + aurora_subnet_group_stack_parameter.title + "}"+ "-" + "RDSSubnetGroup"

aurora_cluster_resource = aurora.add_resource(
  DBCluster(
    "AuroraCluster",
    AvailabilityZones=[ Select(0, GetAZs()), Select(1, GetAZs()), Select(2, GetAZs()) ],
    DeletionPolicy="Snapshot",
    Engine=Ref(aurora_db_engine_parameter),
    EngineVersion=Ref(aurora_db_engine_version_parameter),
    DBClusterIdentifier=Ref(aurora_identifier_parameter),
    MasterUsername=Ref(aurora_db_master_user_parameter),
    MasterUserPassword=Ref(aurora_db_master_password_parameter),
    StorageEncrypted=Ref(aurora_storage_encryption_parameter),
    DBSubnetGroupName=ImportValue(Sub(aurora_subnet_group_name)),
    VpcSecurityGroupIds=Ref(aurora_sec_group_parameter)
  )
)

aurora_cluster_rds01_resource = aurora.add_resource(
  DBInstance(
    "AuroraClusterRDS01",
    DependsOn=aurora_cluster_resource,
    DBInstanceClass=Ref(aurora_type_parameter),
    Engine=Ref(aurora_db_engine_parameter),
    EngineVersion=Ref(aurora_db_engine_version_parameter),
    StorageEncrypted=Ref(aurora_storage_encryption_parameter),
    PubliclyAccessible=Ref(aurora_public_parameter),
    DBClusterIdentifier=Ref(aurora_identifier_parameter)
  )
)

aurora_cluster_rds02_resource = aurora.add_resource(
  DBInstance(
    "AuroraClusterRDS02",
    DependsOn=aurora_cluster_resource,
    DBInstanceClass=Ref(aurora_type_parameter),
    Engine=Ref(aurora_db_engine_parameter),
    EngineVersion=Ref(aurora_db_engine_version_parameter),
    StorageEncrypted=Ref(aurora_storage_encryption_parameter),
    PubliclyAccessible=Ref(aurora_public_parameter),
    DBClusterIdentifier=Ref(aurora_identifier_parameter)
  )
)

with open("aurora.yaml", "w") as file:
  file.write(aurora.to_yaml())
