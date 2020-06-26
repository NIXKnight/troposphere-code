from troposphere.elasticache import SubnetGroup as ECSubnetGroup
from troposphere import Parameter, Ref, Tags, Template, Output, Export, Sub

def createElastiCacheSubnetGroup(template, subnet_resources):
  subnets = [Ref(x) for x in subnet_resources]
  subnet_group_resource_name = "ElastiCacheSubnetGroup"
  subnet_group_resource = template.add_resource(ECSubnetGroup(subnet_group_resource_name, SubnetIds=subnets, Description="ElastiCache subnet group."))
  subnet_group_output = template.add_output(Output(subnet_group_resource_name, Value=Ref(subnet_group_resource_name), Export=Export(Sub("${AWS::StackName}-" + subnet_group_resource_name))))
  return subnet_group_resource, subnet_group_output