from troposphere import Base64, FindInMap, GetAtt, Join, Output, Export, Sub
from troposphere import Parameter, Ref, Template
import troposphere.ec2 as ec2
from troposphere.cloudwatch import Alarm, MetricDimension
import troposphere.elasticloadbalancingv2 as alb

app_tg = Template()
app_tg.add_version("2010-09-09")
app_tg.add_description("ALB stack. Contains ALB, ALB rules, Target Groups, Alarms.")

app_tg_name_parameter = app_tg.add_parameter(
  Parameter(
    'TargetGroupName',
    Default="Production-EDX-TargetGroup",
    Description="The amount time for Elastic Load Balancing to wait before changing the state of a deregistering target from draining to unused.",
    Type="String"
  )
)

app_tg_vpc_id_parameter = app_tg.add_parameter(
  Parameter(
    'VPCID',
    Description="VPC in which the targets are located.",
    Type="AWS::EC2::VPC::Id"
  )
)

app_tg_delay_timeout_parameter = app_tg.add_parameter(
  Parameter(
    'DelayTimeout',
    Default="30",
    MinValue="0",
    MaxValue="3600",
    Description="The amount time for Elastic Load Balancing to wait before changing the state of a deregistering target from draining to unused.",
    Type="Number"
  )
)

app_tg_health_check_interval_parameter = app_tg.add_parameter(
  Parameter(
    'HealthCheckInterval',
    Default="30",
    MinValue="5",
    MaxValue="300",
    Description="The approximate number of seconds between health checks for an individual target.",
    Type="Number"
  )
)

app_tg_health_check_path_parameter = app_tg.add_parameter(
  Parameter(
    'HealthCheckPath',
    Default="/",
    MaxLength="1024",
    Description="The ping path destination where Elastic Load Balancing sends health check requests.",
    Type="String"
  )
)

app_tg_health_check_port_parameter = app_tg.add_parameter(
  Parameter(
    'HealthCheckPort',
    Default="80",
    Description="HTTP port for health check requests.",
    Type="String"
  )
)

app_tg_target_group_port_parameter = app_tg.add_parameter(
  Parameter(
    'TargetGroupPort',
    Default="80",
    MinValue="1",
    MaxValue="65535",
    Description="The port on which the targets receive traffic.",
    Type="Number"
  )
)

app_tg_target_group_protocol_parameter = app_tg.add_parameter(
  Parameter(
    'TargetGroupProtocol',
    Default="HTTP",
    Description="The protocol to use for routing traffic to the targets.",
    Type="String",
    AllowedValues=[ "HTTP", "HTTPS" ]
  )
)

app_tg_health_check_protocol_parameter = app_tg.add_parameter(
  Parameter(
    'HealthCheckProtocol',
    Default="HTTP",
    Description="Health check protocol.",
    Type="String",
    AllowedValues=[ "HTTP", "HTTPS" ]
  )
)

app_tg_health_check_timeout_parameter = app_tg.add_parameter(
  Parameter(
    'HealthCheckTimeout',
    Default="10",
    MinValue="5",
    MaxValue="120",
    Description="Seconds to wait for a response before considering that a health check has failed.",
    Type="Number"
  )
)

app_tg_max_health_check_count_parameter = app_tg.add_parameter(
  Parameter(
    'SuccessMaxHealthCheckCount',
    Default="5",
    MinValue="2",
    MaxValue="10",
    Description="The number of consecutive successful health checks that are required before an unhealthy target is considered healthy.",
    Type="Number"
  )
)

app_tg_health_check_unhealthy_count_parameter = app_tg.add_parameter(
  Parameter(
    'FailedMaxHealthCheckCount',
    Default="2",
    MinValue="2",
    MaxValue="10",
    Description="The number of consecutive failed health checks that are required before a target is considered unhealthy.",
    Type="Number"
  )
)



app_tg_resource = app_tg.add_resource(
  alb.TargetGroup(
    "TargetGroup",
    VpcId=Ref(app_tg_vpc_id_parameter),
    HealthCheckIntervalSeconds=Ref(app_tg_health_check_interval_parameter),
    HealthCheckPath=Ref(app_tg_health_check_path_parameter),
    HealthCheckPort=Ref(app_tg_health_check_port_parameter),
    HealthCheckProtocol=Ref(app_tg_health_check_protocol_parameter),
    HealthCheckTimeoutSeconds=Ref(app_tg_health_check_timeout_parameter),
    HealthyThresholdCount=Ref(app_tg_health_check_unhealthy_count_parameter),
    Name=Ref(app_tg_name_parameter),
    Port=Ref(app_tg_target_group_port_parameter),
    Protocol=Ref(app_tg_target_group_protocol_parameter),
    UnhealthyThresholdCount=Ref(app_tg_health_check_unhealthy_count_parameter)
  )
)

app_tg_alarm_resource = app_tg.add_resource(
  Alarm(
    "TargetGroupUnhealthyAlarm",
    AlarmDescription="Target group unhealthy host alarm.",
    Namespace="AWS/ApplicationELB",
    Dimensions=[ MetricDimension(Name="LoadBalancer", Value=GetAtt(app_tg_resource, "LoadBalancerFullName")) ],
    ComparisonOperator="GreaterThanOrEqualToThreshold",
    MetricName="UnHealthyHostCount",
    EvaluationPeriods="10",
    Period="60",
    Statistic="Maximum",
    Threshold="1",
    Unit="Count",
  )
)

app_tg_url_output = app_tg.add_output(
  Output(
    app_tg_resource.title,
    Value=Ref(app_tg_resource),
    Export=Export(Sub("${AWS::StackName}-" + app_tg_resource.title))
  )
)

with open("TargetGroup.yaml", "w") as file:
  file.write(app_tg.to_yaml())