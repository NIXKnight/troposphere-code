#!/usr/bin/env python
# -*- coding: utf-8 -*-

from troposphere import Base64, FindInMap, GetAtt, Join, Output, Sub, Select, GetAZs
from troposphere import Parameter, Ref, Tags, Template
from troposphere.ec2 import Route, VPCGatewayAttachment, SubnetRouteTableAssociation, Subnet, RouteTable, VPC,  EIP, NatGateway, InternetGateway, SecurityGroupRule, SecurityGroup

def create_vpc(template_name, vpc_name, cidr_block, environment):
  AWS_VPC = template_name.add_resource(VPC(vpc_name, CidrBlock=cidr_block, EnableDnsHostnames=True, EnableDnsSupport=True, Tags=Tags(Name=Sub("${AWS::StackName}" + "VPC"), Environment=environment)))
  return AWS_VPC

def create_subnet(template_name, subnet_name, vpc_id , cidr_block, availability_zone, environment):
  AWS_SUBNET = template_name.add_resource(Subnet(subnet_name, CidrBlock=cidr_block, VpcId=Ref(vpc_id), AvailabilityZone=Select(availability_zone, GetAZs('')), Tags=Tags(Name=Sub("${AWS::StackName}" + "-" + subnet_name), Environment=environment)))
  return AWS_SUBNET

def create_route_table(template_name, route_table_name, vpc_id , environment):
  AWS_ROUTE_TABLE = template_name.add_resource(RouteTable(route_table_name, VpcId=Ref(vpc_id), Tags=Tags(Name=Sub("${AWS::StackName}" + "-" + route_table_name), Environment=environment)))
  return AWS_ROUTE_TABLE

def associate_route_table(template_name, association_name, route_table, subnet):
  ROUTE_ASSOCIATION = template_name.add_resource(SubnetRouteTableAssociation(association_name, SubnetId=Ref(subnet), RouteTableId=Ref(route_table)))
  return ROUTE_ASSOCIATION

def create_internet_gateway(template_name, gateway_name):
  INTERNET_GATEWAY = template_name.add_resource(InternetGateway(gateway_name, Tags=Tags(Name=Sub("${AWS::StackName}" + "-" + gateway_name))))
  return INTERNET_GATEWAY

def create_internet_gateway_route(template_name, route_name, depends_gateway, gateway_id, route_table, destination_cidr_block):
  IGW_ROUTE = template_name.add_resource(Route(route_name, DependsOn=depends_gateway, GatewayId=Ref(gateway_id), DestinationCidrBlock=destination_cidr_block, RouteTableId=Ref(route_table)))
  return IGW_ROUTE

def attach_internet_gateway(template_name, attachment_name, gateway, vpc_id):
  ATTACHMENT = template_name.add_resource(VPCGatewayAttachment(attachment_name, VpcId=Ref(vpc_id), InternetGatewayId=Ref(gateway)))
  return ATTACHMENT

def create_eip(template_name, eip_name):
  NAT_EIP = template_name.add_resource(EIP(eip_name, Domain="vpc"))
  return NAT_EIP

def create_nat_gateway(template_name, nat_gateway_name, nat_eip, subnet):
  NAT_GATEWAY = template_name.add_resource(NatGateway(nat_gateway_name, AllocationId=GetAtt(nat_eip, 'AllocationId'), SubnetId=Ref(subnet)))
  return NAT_GATEWAY

def create_nat_gateway_route(template_name, nat_gateway_route_name, destination_cidr_block, nat_gateway, route_table):
  NGW_ROUTE = template_name.add_resource(Route(nat_gateway_route_name, RouteTableId=Ref(route_table), DestinationCidrBlock=destination_cidr_block, NatGatewayId=Ref(nat_gateway)))

baseNetwork = Template()
baseNetwork.add_version('2010-09-09')
baseNetwork.add_description('Base network template. VPC, networks, Security Groups, Subnet Groups and NAT gateways.')

## Create a VPC
VPC = create_vpc(baseNetwork, 'VPC', '10.0.0.0/20', 'Production') # Create VPC

## Create subnets, route table(s), gateway(s) in public
# Create subnets
PUBLIC_SUBNET_01 = create_subnet(baseNetwork, 'PublicNet01', VPC , '10.0.0.0/24', 0, 'Production')
PUBLIC_SUBNET_02 = create_subnet(baseNetwork, 'PublicNet02', VPC , '10.0.1.0/24', 1, 'Production')
PUBLIC_SUBNET_03 = create_subnet(baseNetwork, 'PublicNet03', VPC , '10.0.2.0/24', 2, 'Production')
# Create route table and associate subnets with route tables
PUBLIC_ROUTE_TABLE = create_route_table(baseNetwork, 'PublicNetRouteTable', VPC, 'Production')
PUBLIC_SUBNET_01_ROUTE_TABLE_ASSOCIATION = associate_route_table(baseNetwork, 'PublicNet01RouteAssociation', PUBLIC_ROUTE_TABLE, PUBLIC_SUBNET_01)
PUBLIC_SUBNET_02_ROUTE_TABLE_ASSOCIATION = associate_route_table(baseNetwork, 'PublicNet02RouteAssociation', PUBLIC_ROUTE_TABLE, PUBLIC_SUBNET_02)
PUBLIC_SUBNET_03_ROUTE_TABLE_ASSOCIATION = associate_route_table(baseNetwork, 'PublicNet03RouteAssociation', PUBLIC_ROUTE_TABLE, PUBLIC_SUBNET_03)
# Create an internet gateway, attach the internet gateway to VPC and create internet gateway route
PUBLIC_IGW = create_internet_gateway(baseNetwork, 'PublicNetIGW')
PUBLIC_IGW_ATTACHMENT = attach_internet_gateway(baseNetwork, 'PublicIGWAttachment', PUBLIC_IGW, VPC)
PIBLIC_IGW_ROUTE = create_internet_gateway_route(baseNetwork, "PublicIGWRoute", PUBLIC_IGW_ATTACHMENT, PUBLIC_IGW, PUBLIC_ROUTE_TABLE, '0.0.0.0')

## Create subnets, route table(s), NAT gateway(s) for EDX apps and workers
# Create subnets
EDX_SUBNET_01 = create_subnet(baseNetwork, 'EDXNet01', VPC , '10.0.3.0/24', 0, 'Production') # Create private subnet for edX apps and workers
EDX_SUBNET_02 = create_subnet(baseNetwork, 'EDXNet02', VPC , '10.0.4.0/24', 1, 'Production') # Create private subnet for edX apps and workers
EDX_SUBNET_03 = create_subnet(baseNetwork, 'EDXNet03', VPC , '10.0.5.0/24', 2, 'Production') # Create private subnet for edX apps and workers
# Create route tables
EDX_ROUTE_TABLE_01 = create_route_table(baseNetwork, 'EDXRouteTable01', VPC, 'Production')
EDX_ROUTE_TABLE_02 = create_route_table(baseNetwork, 'EDXRouteTable02', VPC, 'Production')
EDX_ROUTE_TABLE_03 = create_route_table(baseNetwork, 'EDXRouteTable03', VPC, 'Production')
# Associate Route tables with subnets
EDX_SUBNET_01_ROUTE_TABLE_ASSOCIATION = associate_route_table(baseNetwork, 'EDXNet01RouteAssociation', EDX_ROUTE_TABLE_01, EDX_SUBNET_01)
EDX_SUBNET_02_ROUTE_TABLE_ASSOCIATION = associate_route_table(baseNetwork, 'EDXNet02RouteAssociation', EDX_ROUTE_TABLE_02, EDX_SUBNET_02)
EDX_SUBNET_03_ROUTE_TABLE_ASSOCIATION = associate_route_table(baseNetwork, 'EDXNet03RouteAssociation', EDX_ROUTE_TABLE_03, EDX_SUBNET_03)
# Allocate elastic IP addresses for NAT gateways
EDX_EIP_01 = create_eip(baseNetwork, 'EDXEIP01')
EDX_EIP_02 = create_eip(baseNetwork, 'EDXEIP02')
EDX_EIP_03 = create_eip(baseNetwork, 'EDXEIP03')
# Create NAT gateways, associate subnets and elastic IP addresses
EDX_NGW_01 = create_nat_gateway(baseNetwork, 'EDXNGW01', EDX_EIP_01, EDX_SUBNET_01)
EDX_NGW_02 = create_nat_gateway(baseNetwork, 'EDXNGW02', EDX_EIP_02, EDX_SUBNET_02)
EDX_NGW_03 = create_nat_gateway(baseNetwork, 'EDXNGW03', EDX_EIP_03, EDX_SUBNET_03)
# Create a route to internet via NAT gateway
EDX_NGW_ROUTE_01 = create_nat_gateway_route(baseNetwork, 'EDXNGWRoute01', '0.0.0.0', EDX_NGW_01, EDX_ROUTE_TABLE_01)
EDX_NGW_ROUTE_02 = create_nat_gateway_route(baseNetwork, 'EDXNGWRoute02', '0.0.0.0', EDX_NGW_02, EDX_ROUTE_TABLE_02)
EDX_NGW_ROUTE_03 = create_nat_gateway_route(baseNetwork, 'EDXNGWRoute03', '0.0.0.0', EDX_NGW_03, EDX_ROUTE_TABLE_03)

## Create subnets, route table(s), NAT gateway(s) for services
# Create subnets
SRV_SUBNET_01 = create_subnet(baseNetwork, 'ServicesNet01', VPC , '10.0.6.0/24', 0, 'Production') # Create private subnet for edX apps and workers
SRV_SUBNET_02 = create_subnet(baseNetwork, 'ServicesNet02', VPC , '10.0.7.0/24', 1, 'Production') # Create private subnet for edX apps and workers
SRV_SUBNET_03 = create_subnet(baseNetwork, 'ServicesNet03', VPC , '10.0.8.0/24', 2, 'Production') # Create private subnet for edX apps and workers
# Create route tables
SRV_ROUTE_TABLE_01 = create_route_table(baseNetwork, 'SRVRouteTable01', VPC, 'Production')
SRV_ROUTE_TABLE_02 = create_route_table(baseNetwork, 'SRVRouteTable02', VPC, 'Production')
SRV_ROUTE_TABLE_03 = create_route_table(baseNetwork, 'SRVRouteTable03', VPC, 'Production')
# Associate Route tables with subnets
SRV_SUBNET_01_ROUTE_TABLE_ASSOCIATION = associate_route_table(baseNetwork, 'SRVNet01RouteAssociation', SRV_ROUTE_TABLE_01, SRV_SUBNET_01)
SRV_SUBNET_02_ROUTE_TABLE_ASSOCIATION = associate_route_table(baseNetwork, 'SRVNet02RouteAssociation', SRV_ROUTE_TABLE_02, SRV_SUBNET_02)
SRV_SUBNET_03_ROUTE_TABLE_ASSOCIATION = associate_route_table(baseNetwork, 'SRVNet03RouteAssociation', SRV_ROUTE_TABLE_03, SRV_SUBNET_03)
# Allocate elastic IP addresses for NAT gateways
SRV_EIP_01 = create_eip(baseNetwork, 'SRVEIP01')
SRV_EIP_02 = create_eip(baseNetwork, 'SRVEIP02')
SRV_EIP_03 = create_eip(baseNetwork, 'SRVEIP03')
# Create NAT gateways, associate subnets and elastic IP addresses
SRV_NGW_01 = create_nat_gateway(baseNetwork, 'SRVNGW01', SRV_EIP_01, SRV_SUBNET_01)
SRV_NGW_02 = create_nat_gateway(baseNetwork, 'SRVNGW02', SRV_EIP_02, SRV_SUBNET_02)
SRV_NGW_03 = create_nat_gateway(baseNetwork, 'SRVNGW03', SRV_EIP_03, SRV_SUBNET_03)
# Create a route to internet via NAT gateway
SRV_NGW_ROUTE_01 = create_nat_gateway_route(baseNetwork, 'SRVNGWRoute01', '0.0.0.0', SRV_NGW_01, SRV_ROUTE_TABLE_01)
SRV_NGW_ROUTE_02 = create_nat_gateway_route(baseNetwork, 'SRVNGWRoute02', '0.0.0.0', SRV_NGW_02, SRV_ROUTE_TABLE_02)
SRV_NGW_ROUTE_03 = create_nat_gateway_route(baseNetwork, 'SRVNGWRoute03', '0.0.0.0', SRV_NGW_03, SRV_ROUTE_TABLE_03)

print(baseNetwork.to_yaml())
