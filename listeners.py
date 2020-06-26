from troposphere import Base64, FindInMap, GetAtt, Join, Output, Sub, Export
from troposphere import Parameter, Ref, Template
import troposphere.ec2 as ec2
import troposphere.elasticloadbalancingv2 as elb

alb_listener = Template()
alb_listener.add_version("2010-09-09")
alb_listener.add_description("ALB listeners stack. Contains ALB listeners and listener rules.")

# alb_listener_alb_arn_parameter = alb_listener.add_parameter(
#   Parameter(
#     'ALBArn',
#     Default="",
#     Description="ARN for ALB.",
#     Type="String"
#   )
# )

# alb_listener_tg_arn_parameter = alb_listener.add_parameter(
#   Parameter(
#     'TGArn',
#     Default="",
#     Description="ARN for ALB.",
#     Type="String"
#   )
# )

alb_listener_http_resource = alb_listener.add_resource(
  elb.Listener(
    "HTTPListener",
    Port=80,
    Protocol="HTTP",
    LoadBalancerArn="arn:aws:elasticloadbalancing:us-west-2:486807960363:loadbalancer/app/ucsd-prod-alb/018c81eaca819d8b",
    DefaultActions=[
      elb.Action(
        Type="forward",
        TargetGroupArn="arn:aws:elasticloadbalancing:us-west-2:486807960363:targetgroup/UCSD-Prod-edX-Platform-TG/96de5fa2f23209c5",
      )
    ]
  )
)

# alb_listener_https_resource = alb_listener.add_resource(
#   elb.Listener(
#     "HTTPSListener",
#     Port=443,
#     Protocol="HTTPS",
#     LoadBalancerArn=Sub("${" + alb_listener_alb_arn_parameter.title + "}-ALB"),
#     DefaultActions=[
#       elb.Action(
#         Type="forward",
#         TargetGroupArn=Sub("${" + alb_listener_tg_arn_parameter.title + "}-TargetGroup"),
#       )
#     ]
#   )
# )

alb_listener_http_rule_resource = alb_listener.add_resource(
  elb.ListenerRule(
    "HTTPListenerRule",
    ListenerArn=Ref(alb_listener_http_resource),
    Conditions=[
      elb.Condition(
        Field="host-header",
        Values=[ "discuss.courses.ucsd.edu" ]
      )
    ],
    Actions=[
      elb.Action(
        Type="forward",
        TargetGroupArn="arn:aws:elasticloadbalancing:us-west-2:486807960363:targetgroup/UCSD-Prod-edX-Platform-TG/96de5fa2f23209c5"
      )
    ],
    Priority=1
  )
)

# alb_listener_https_rule_resource = alb_listener.add_resource(
#   elb.ListenerRule(
#     "HTTPSListenerRule",
#     ListenerArn=Ref(alb_listener_https_resource),
#     Conditions=[
#       elb.Condition(
#         Field="host-header",
#         Values=[ "discuss.courses.ucsd.edu" ]
#       )
#     ],
#     Actions=[
#       elb.Action(
#         Type="forward",
#         TargetGroupArn=Ref(alb_listener_tg_arn_parameter)
#       )
#     ],
#     Priority=1
#   )
# )

alb_listener_http_resource_output = alb_listener.add_output(
  Output(
    alb_listener_http_resource.title,
    Value=Ref(alb_listener_http_resource),
    Export=Export(Sub("${AWS::StackName}-" + alb_listener_http_resource.title))
  )
)

# alb_listener_https_resource_output = alb_listener.add_output(
#   Output(
#     alb_listener_https_resource.title,
#     Value=Ref(alb_listener_https_resource),
#     Export=Export(Sub("${AWS::StackName}-" + alb_listener_https_resource.title))
#   )
# )

with open("Listeners.yaml", "w") as file:
  file.write(alb_listener.to_yaml())