import math
import netaddr
from troposphere import Base64, FindInMap, GetAtt, Join, Output, Sub, Select, GetAZs
from troposphere import Parameter, Ref, Tags, Template
from troposphere.ec2 import Route, VPCGatewayAttachment, SubnetRouteTableAssociation, Subnet, RouteTable, VPC,  EIP, NatGateway, InternetGateway, SecurityGroup

# Subnet calculation code taken from https://github.com/tomelliff/vpc-subnet-calculator/blob/master/vpc_subnet_calculator.py

def getNextBinary(integer):
  next_binary = int(math.pow(2, math.ceil(math.log(integer) / math.log(2))))
  if next_binary == integer:
    next_binary = getNextBinary(integer + 1)
  return int(next_binary)

def subtractSubnetsFromRange(cidr_range, subnets):
  full_range = netaddr.IPNetwork(cidr_range)
  subnet_mask_bits = netaddr.IPNetwork(subnets[0]).prefixlen
  remaining_subnets = [str(subnet) for subnet in full_range.subnet(subnet_mask_bits) if str(subnet) not in subnets]
  return str(netaddr.cidr_merge(remaining_subnets)[0])

def maximizeSubnets(cidr_range, num_subnets):
  MAX_AWS_VPC_SUBNET_BIT_MASK = 28
  MIN_AWS_VPC_SUBNET_BIT_MASK = 16
  full_range = netaddr.IPNetwork(cidr_range)
  full_range_mask_bits = full_range.prefixlen
  subnet_mask_bits = (full_range_mask_bits + int(math.log(getNextBinary(num_subnets), 2)))
  if subnet_mask_bits > MAX_AWS_VPC_SUBNET_BIT_MASK:
    raise ValueError('Minimum subnet size is /{}'.format(MAX_AWS_VPC_SUBNET_BIT_MASK))
  elif subnet_mask_bits < MIN_AWS_VPC_SUBNET_BIT_MASK:
    raise ValueError('Maximum subnet size is /{}'.format(MIN_AWS_VPC_SUBNET_BIT_MASK))
  subnets = []
  for subnet in full_range.subnet(subnet_mask_bits):
    if len(subnets) < num_subnets:
      subnets.append(str(subnet))
  return subnets

def calculateSubnets(vpc_cidr_range, num_azs, subnet_type):
  private_subnets = maximizeSubnets(vpc_cidr_range, num_azs)
  remaining_space = subtractSubnetsFromRange(vpc_cidr_range, private_subnets)
  public_subnets = maximizeSubnets(remaining_space, num_azs)
  if subnet_type == 'private':
    return private_subnets
  elif subnet_type == 'public':
    return public_subnets

def createVPC(template, vpc_name, cidr_block):
  vpc_parameter = template.add_parameter(Parameter(vpc_name + "CIDR", Description="Name of VPC. Set to " + cidr_block + " by default.", Type="String", Default=cidr_block, AllowedPattern='((\d{1,3})\.){3}\d{1,3}/\d{1,2}'))
  vpc_resource = template.add_resource(VPC(vpc_name, CidrBlock=Ref(vpc_parameter), EnableDnsHostnames=True, EnableDnsSupport=True, Tags=Tags(Name=Sub("${AWS::StackName}" + '-' + vpc_name))))
  return vpc_parameter, vpc_resource

def createSubnet(template, subnet_name, vpc_id , cidr_block, availability_zone):
  subnet_parameter = template.add_parameter(Parameter(subnet_name + "CIDR", Description="Name of VPC. Set to " + cidr_block + " by default.", Type="String", Default=cidr_block, AllowedPattern='((\d{1,3})\.){3}\d{1,3}/\d{1,2}'))
  subnet_resource = template.add_resource(Subnet(subnet_name, CidrBlock=Ref(subnet_parameter), VpcId=Ref(vpc_id), AvailabilityZone=Select(availability_zone, GetAZs('')), Tags=Tags(Name=Sub("${AWS::StackName}" + "-" + subnet_name))))
  return subnet_parameter, subnet_resource

def createRouteTable(template, route_table_name, vpc_id):
  route_table = template.add_resource(RouteTable(route_table_name, VpcId=Ref(vpc_id), Tags=Tags(Name=Sub("${AWS::StackName}" + "-" + route_table_name))))
  return route_table

def associateRouteTable(template, association_name, route_table, subnet):
  route_association = template.add_resource(SubnetRouteTableAssociation(association_name, SubnetId=Ref(subnet), RouteTableId=Ref(route_table)))
  return route_association

def createPublicNetworks(template, vpc_parameter, vpc_resource, regions_count):
  subnet_parameters = []
  subnet_resources = []
  vpc_cidr_block = vpc_parameter.properties['Default']
  internet_cidr_block = '0.0.0.0/0'
  igw_name = "PublicInternetGateway"
  public_subnets = calculateSubnets(vpc_cidr_block, regions_count, 'public')
  public_route_table = createRouteTable(template, 'PublicRouteTable', vpc_resource)
  public_igw = template.add_resource(InternetGateway(igw_name, Tags=Tags(Name=Sub("${AWS::StackName}" + "-" + igw_name))))
  public_igw_attachment = template.add_resource(VPCGatewayAttachment('PublicRouteTableAttachment', VpcId=Ref(vpc_resource), InternetGatewayId=Ref(public_igw)))
  for az, subnet in enumerate(public_subnets):
    subnet_name = "PublicNet" + str("%02d" % (az + 1))
    route_table_association_name = subnet_name + "RouteAssociation"
    subnet_parameter, subnet_resource = createSubnet(template, subnet_name, vpc_resource, subnet, az)
    subnet_parameters.append(subnet_parameter)
    subnet_resources.append(subnet_resource)
    associateRouteTable(template, route_table_association_name, public_route_table, subnet_name)
  public_igw_route = template.add_resource(Route('PublicInternetRoute', DependsOn=public_igw_attachment, GatewayId=Ref(public_igw), DestinationCidrBlock=internet_cidr_block, RouteTableId=Ref(public_route_table)))
  return subnet_parameters, subnet_resources

def createPrivateNetworks(template, vpc_parameter, vpc_resource, regions_count):
  subnet_parameters = []
  subnet_resources = []
  vpc_cidr_block = vpc_parameter.properties['Default']
  internet_cidr_block = '0.0.0.0/0'
  private_subnets = calculateSubnets(vpc_cidr_block, regions_count, 'private')
  for az, subnet in enumerate(private_subnets):
    subnet_name = "PrivateNet" + str("%02d" % (az + 1))
    route_table_name = subnet_name + "RouteTable"
    eip_name = subnet_name + "ElasticIP"
    nat_gw_name = subnet_name + "NATGateway"
    nat_gw_route_name = subnet_name + "NATGatewayRoute"
    private_route_table = createRouteTable(template, route_table_name, vpc_resource)
    route_table_association_name = subnet_name + "RouteAssociation"
    subnet_parameter, subnet_resource = createSubnet(template, subnet_name, vpc_resource, subnet, az)
    subnet_parameters.append(subnet_parameter)
    subnet_resources.append(subnet_resource)
    associateRouteTable(template, route_table_association_name, private_route_table, subnet_name)
    template.add_resource(EIP(eip_name, Domain="vpc"))
    template.add_resource(NatGateway(nat_gw_name, AllocationId=GetAtt(eip_name, 'AllocationId'), SubnetId=Ref(subnet_name)))
    template.add_resource(Route(nat_gw_route_name, RouteTableId=Ref(private_route_table), DestinationCidrBlock=internet_cidr_block, NatGatewayId=Ref(nat_gw_name)))
  return subnet_parameters, subnet_resources
