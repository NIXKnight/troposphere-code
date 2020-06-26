from troposphere.rds import DBSubnetGroup, DBInstance
from troposphere import Parameter, Ref, Tags, Template, Output, Export, Sub

def createRDSSubnetGroup(template, subnet_resources):
  subnets = [Ref(x) for x in subnet_resources]
  subnet_group_resource_name = "RDSSubnetGroup"
  subnet_group_resource = template.add_resource(DBSubnetGroup(subnet_group_resource_name, SubnetIds=subnets, DBSubnetGroupDescription="RDS subnet group."))
  subnet_group_output = template.add_output(Output(subnet_group_resource_name, Value=Ref(subnet_group_resource_name), Export=Export(Sub("${AWS::StackName}-" + subnet_group_resource_name))))
  return subnet_group_resource, subnet_group_output
