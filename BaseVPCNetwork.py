from troposphere import Template, Ref
from troposphere.ec2 import SecurityGroup, SecurityGroupRule
from vpc_functions import createVPC, createPublicNetworks, createPrivateNetworks
from rds_functions import createRDSSubnetGroup
from elasticache_functions import createElastiCacheSubnetGroup

base_network = Template()
base_network.add_version('2010-09-09')
base_network.add_description('Base network template. VPC, networks, Security Groups, Subnet Groups and NAT gateways.')

vpc_parameter, vpc_resource = createVPC(base_network, 'VPC', '192.168.0.0/20')
public_subnet_parameters, public_subnet_resources = createPublicNetworks(base_network, vpc_parameter, vpc_resource, 3)
private_subnet_parameters, private_subnet_resources = createPrivateNetworks(base_network, vpc_parameter, vpc_resource, 3)

# rds_subnet_group_resource, rds_subnet_group_output  = createRDSSubnetGroup(base_network, private_subnet_resources)
# elasticache_subnet_group_resource, elasticache_subnet_group_output = createElastiCacheSubnetGroup(base_network, private_subnet_resources)

# bastion_security_group = base_network.add_resource(
#   SecurityGroup(
#     'UCSDBastionSecGroup', VpcId=Ref(vpc_resource), GroupDescription='Security group for Bastion instance',
#     SecurityGroupIngress=[
#       SecurityGroupRule(
#         IpProtocol='tcp', FromPort='22', ToPort='22', CidrIp='0.0.0.0/0'
#       )
#     ]
#   )
# )

# edx_alb_security_group = base_network.add_resource(
#   SecurityGroup(
#     'UCSDedXALBSecGroup', VpcId=Ref(vpc_resource), GroupDescription='Security group for Application Load Balancer standing in front of edX instances',
#     SecurityGroupIngress=[
#       SecurityGroupRule(
#         IpProtocol='tcp', FromPort='80', ToPort='80', CidrIp='0.0.0.0/0'
#       ),
#       SecurityGroupRule(
#         IpProtocol='tcp', FromPort='443', ToPort='443', CidrIp='0.0.0.0/0'
#       )
#     ]
#   )
# )

# edx_security_group = base_network.add_resource(
#   SecurityGroup(
#     'UCSDedXSecGroup', VpcId=Ref(vpc_resource), GroupDescription='Security group for all edX instances',
#     SecurityGroupIngress=[
#       SecurityGroupRule(
#         IpProtocol='tcp', FromPort='80', ToPort='80', SourceSecurityGroupId=Ref(edx_alb_security_group)
#       ),
#       SecurityGroupRule(
#         IpProtocol='tcp', FromPort='22', ToPort='22', SourceSecurityGroupId=Ref(bastion_security_group)
#       )
#     ]
#   )
# )

# mongodb_security_group = base_network.add_resource(
#   SecurityGroup(
#     'UCSDMongoDBSecGroup', VpcId=Ref(vpc_resource), GroupDescription='Security group for all MongoDB instances',
#     SecurityGroupIngress=[
#       SecurityGroupRule(
#         IpProtocol='tcp', FromPort='27017', ToPort='27017', SourceSecurityGroupId=Ref(edx_security_group)
#       ),
#       SecurityGroupRule(
#         IpProtocol='tcp', FromPort='22', ToPort='22', SourceSecurityGroupId=Ref(bastion_security_group)
#       )
#     ]
#   )
# )

# rds_security_group = base_network.add_resource(
#   SecurityGroup(
#     'UCSDRDSSecGroup', VpcId=Ref(vpc_resource), GroupDescription='Security group for all edX instances',
#     SecurityGroupIngress=[
#       SecurityGroupRule(
#         IpProtocol='tcp', FromPort='3306', ToPort='3306', SourceSecurityGroupId=Ref(edx_security_group)
#       )
#     ]
#   )
# )

# redis_security_group = base_network.add_resource(
#   SecurityGroup(
#     'UCSDRedisSecGroup', VpcId=Ref(vpc_resource), GroupDescription='Security group for all Redis instances',
#     SecurityGroupIngress=[
#       SecurityGroupRule(
#         IpProtocol='tcp', FromPort='6379', ToPort='6379', SourceSecurityGroupId=Ref(edx_security_group)
#       )
#     ]
#   )
# )

# memcached_security_group = base_network.add_resource(
#   SecurityGroup(
#     'UCSDMemcachedSecGroup', VpcId=Ref(vpc_resource), GroupDescription='Security group for all Memcached instances',
#     SecurityGroupIngress=[
#       SecurityGroupRule(
#         IpProtocol='tcp', FromPort='11211', ToPort='11211', SourceSecurityGroupId=Ref(edx_security_group)
#       )
#     ]
#   )
# )

# elasticsearch_security_group = base_network.add_resource(
#   SecurityGroup(
#     'UCSDElasticsearchSecGroup', VpcId=Ref(vpc_resource), GroupDescription='Security group for all Memcached instances',
#     SecurityGroupIngress=[
#       SecurityGroupRule(
#         IpProtocol='-1', SourceSecurityGroupId=Ref(edx_security_group)
#       )
#     ]
#   )
# ) 

with open("BaseVPCNetwork.yaml", "w") as file:
  file.write(base_network.to_yaml())
