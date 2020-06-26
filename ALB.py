from troposphere import Base64, FindInMap, GetAtt, Join, Output, Export, Sub
from troposphere import Parameter, Ref, Template
import troposphere.ec2 as ec2
from troposphere.cloudwatch import Alarm, MetricDimension
import troposphere.elasticloadbalancingv2 as elb
from troposphere.elasticloadbalancingv2 import LoadBalancerAttributes

alb = Template()
alb.add_version("2010-09-09")
alb.add_description("ALB stack. Contains ALB, ALB rules, Target Groups, Alarms.")

alb_name_parameter = alb.add_parameter(
  Parameter(
    'ALBName',
    Default="ucsd-prod-alb",
    Description="A name for the load balancer.",
    Type="String"
  )
)

alb_type_parameter = alb.add_parameter(
  Parameter(
    'ALBType',
    Default="application",
    Description="A name for the load balancer.",
    Type="String",
    AllowedValues=[ "application", "network" ]
  )
)

alb_scheme_parameter = alb.add_parameter(
  Parameter(
    'ALBScheme',
    Default="internet-facing",
    Description="Specifies whether the load balancer is internal or Internet-facing.",
    Type="String",
    AllowedValues=[ "internet-facing", "internal" ]
  )
)

alb_subnets_parameter = alb.add_parameter(
  Parameter(
    'ALBSubnets',
    Description="The subnets to attach to the load balancer, specified as a list of subnet IDs.",
    Type="List<AWS::EC2::Subnet::Id>"
  )
)


alb_security_group_parameter = alb.add_parameter(
  Parameter(
    'ALBSecurityGroups',
    Description="The subnets to attach to the load balancer, specified as a list of subnet IDs.",
    Type="List<AWS::EC2::SecurityGroup::Id>"
  )
)

alb_attr_s3_logs_parameter = alb.add_parameter(
  Parameter(
    'ALBAttrEnableS3Logs',
    Default="true",
    Description="Indicates whether access logs are enabled.",
    Type="String",
    AllowedValues=[ "true", "false" ]
  )
)

alb_attr_s3_logs_bucket_parameter = alb.add_parameter(
  Parameter(
    'ALBAttrS3LogsBucket',
    Default="",
    Description="The name of the S3 bucket for the access logs.",
    Type="String"
  )
)

alb_attr_idle_timeout_parameter = alb.add_parameter(
  Parameter(
    'ALBAttrIdleTimeout',
    Default="60",
    MinValue="1",
    MaxValue="4000",
    Description="The idle timeout value, in seconds. The valid range is 1-4000 seconds. The default is 60 seconds.",
    Type="Number"
  )
)

alb_attr_http2_parameter = alb.add_parameter(
  Parameter(
    'ALBAttrEnableHTTP2',
    Default="true",
    Description="Indicates whether HTTP/2 is enabled.",
    Type="String",
    AllowedValues=[ "true", "false" ]
  )
)

alb_resource = alb.add_resource(
  elb.LoadBalancer(
    "ALB",
    Name=Ref(alb_name_parameter),
    Scheme=Ref(alb_scheme_parameter),
    SecurityGroups=Ref(alb_security_group_parameter),
    Subnets=Ref(alb_subnets_parameter),
    Type=Ref(alb_type_parameter),
    LoadBalancerAttributes = [
      LoadBalancerAttributes(Key='access_logs.s3.enabled', Value=Ref(alb_attr_s3_logs_parameter)),
      LoadBalancerAttributes(Key='access_logs.s3.bucket', Value=Ref(alb_attr_s3_logs_bucket_parameter)),
      LoadBalancerAttributes(Key='idle_timeout.timeout_seconds', Value=Ref(alb_attr_idle_timeout_parameter)),
      LoadBalancerAttributes(Key='routing.http2.enabled', Value=Ref(alb_attr_http2_parameter))
    ]
  )
)

alb_dns_name_output = alb.add_output(
  Output(
    "DNSName",
    Value=GetAtt(alb_resource, "DNSName"),
    Export=Export(Sub("${AWS::StackName}-DNSName"))
  )
)

alb_arn_output = alb.add_output(
  Output(
    alb_resource.title,
    Value=Ref(alb_resource),
    Export=Export(Sub("${AWS::StackName}-" + alb_resource.title))
  )
)

with open("ALB.yaml", "w") as file:
  file.write(alb.to_yaml())