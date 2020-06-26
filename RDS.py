from troposphere import Template, Ref, Sub, ImportValue, Parameter
from troposphere.rds import DBInstance

rds_instance = Template()
rds_instance.add_version('2010-09-09')
rds_instance.add_description('RDS Multi-AZ instance stack.')

rds_instance_identifier_parameter = rds_instance.add_parameter(
  Parameter(
    'InstanceIdentifier',
    Default="ucsd-edx-prod",
    Description="Name that is unique for all DB instances owned by your AWS account in the current region.",
    Type="String"
  )
)
rds_instance_type_parameter = rds_instance.add_parameter(
  Parameter(
    'InstanceType',
    Default="db.t2.medium",
    AllowedValues=[
      "db.m5.large", "db.m5.xlarge", "db.m5.2xlarge", "db.m5.4xlarge", "db.m5.12xlarge", "db.m5.24xlarge", "db.m4.large", "db.m4.xlarge",
      "db.m4.2xlarge", "db.m4.4xlarge", "db.m4.10xlarge", "db.m4.16xlarge", "db.r4.large", "db.r4.xlarge", "db.r4.2xlarge", "db.r4.4xlarge",
      "db.r4.8xlarge", "db.r4.16xlarge", "db.x1e.xlarge", "db.x1e.2xlarge", "db.x1e.4xlarge", "db.x1e.8xlarge", "db.x1e.16xlarge", "db.x1e.32xlarge",
      "db.x1.16xlarge", "db.x1.32xlarge", "db.r3.large", "db.r3.xlarge", "db.r3.2xlarge", "db.r3.4xlarge", "db.r3.8xlarge", "db.t2.micro",
      "db.t2.small", "db.t2.medium", "db.t2.large", "db.t2.xlarge", "db.t2.2xlarge"
    ],
    Type="String"
  )
)

rds_instance_size_parameter = rds_instance.add_parameter(
  Parameter(
    'InstanceSize',
    Default="10",
    Description="Select RDS size in GB.",
    Type="String"
  )
)

rds_db_engine_parameter = rds_instance.add_parameter(
  Parameter(
    'DBEngine',
    Default="MySQL",
    Description="Default RDS database engine.",
    Type="String"
  )
)

rds_db_engine_version_parameter = rds_instance.add_parameter(
  Parameter(
    'DBEngineVersion',
    Default="5.7.23",
    Description="Default RDS database engine version.",
    Type="String",
    AllowedValues=[ "5.6.41", "5.7.23" ]
  )
)

rds_storage_encryption_parameter = rds_instance.add_parameter(
  Parameter(
    'EncryptionAtRest',
    Default="false",
    Description="Encrypt database storage.",
    Type="String",
    AllowedValues=[ "true", "false" ]
  )
)

rds_db_master_user_parameter = rds_instance.add_parameter(
  Parameter(
    'DBMasterUser',
    Default="dbadmin",
    Description="Default master username for RDS instance.",
    Type="String"
  )
)

rds_db_master_password_parameter = rds_instance.add_parameter(
  Parameter(
    'DBMasterPassword',
    Default="",
    Description="Default master password for RDS instance.",
    NoEcho=True,
    Type="String"
  )
)

rds_multiaz_parameter = rds_instance.add_parameter(
  Parameter(
    'MultiAZ',
    Default="true",
    AllowedValues=[ "true", "false" ],
    Description="Setup RDS with Multi-AZ deployment.",
    Type="String"
  )
)

rds_sec_group_parameter = rds_instance.add_parameter(
  Parameter(
    'SecurityGroups',
    Description="RDS security group.",
    Type="List<AWS::EC2::SecurityGroup::Id>"
  )
)

rds_subnet_group_stack_parameter = rds_instance.add_parameter(
  Parameter(
    'NetworkStackName',
    Default="",
    Description="Stack name containing exported RDS subnet group.",
    NoEcho=True,
    Type="String"
  )
)

rds_resource = rds_instance.add_resource(
  DBInstance(
    "RDSInstance",
    DeletionPolicy="Snapshot",
    VPCSecurityGroups=Ref(rds_sec_group_parameter),
    AllocatedStorage=Ref(rds_instance_size_parameter),
    StorageEncrypted=Ref(rds_storage_encryption_parameter),
    DBInstanceClass=Ref(rds_instance_type_parameter),
    Engine=Ref(rds_db_engine_parameter),
    EngineVersion=Ref(rds_db_engine_version_parameter),
    MultiAZ=Ref(rds_multiaz_parameter),
    DBInstanceIdentifier=Ref(rds_instance_identifier_parameter),
    MasterUsername=Ref(rds_db_master_user_parameter),
    MasterUserPassword=Ref(rds_db_master_password_parameter),
    DBSubnetGroupName=ImportValue(Sub("${" + rds_subnet_group_stack_parameter.title + "}"+ "-" + "RDSSubnetGroup"))
  )
)

with open("rds.yaml", "w") as file:
  file.write(rds_instance.to_yaml())
