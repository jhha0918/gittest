import boto3



# Credentional key 직접 입력

key_id = 'AKIA3BTT3V2L4473VD6O'
access_key = 'SHKsIaGNfgQQpKU8XCpen6Yloc5F2M2CyO+7HsWf'
aws_region = 'ap-northeast-2'

# key 대화형 입력 
# key_id = input('aws_access_key_id = ')
# access_key = input('aws_secret_access_key = ')
# aws_region = input('region_name = ')



# VPC 정보 입력
vpc_cidr_block = '192.168.0.0/16'
vpc_name = 'Python_vpc'
subnet_cidr_block = '192.168.1.0/24'

#EC2 정보 입력
ec2_imageid = 'ami-0bea7fd38fabe821a'
ec2_instancetype = 't2.micro'



ec2 = boto3.resource('ec2', aws_access_key_id=key_id,
                     aws_secret_access_key=access_key,
                     region_name=aws_region)



# https://gist.github.com/nguyendv/8cfd92fc8ed32ebb78e366f44c2daea6

# create VPC
vpc = ec2.create_vpc(CidrBlock=vpc_cidr_block)
# we can assign a name to vpc, or any resource, by using tag
vpc.create_tags(Tags=[{"Key": "Name", "Value": vpc_name}])
vpc.wait_until_available()
print(vpc.id)


# create subnet
subnet = ec2.create_subnet(CidrBlock=subnet_cidr_block, VpcId=vpc.id)
print(subnet.id)


# create then attach internet gateway
ig = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=ig.id)
print(ig.id)


# create a route table and a public route
route_table = vpc.create_route_table()
route = route_table.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=ig.id
)
print(route_table.id)

# associate the route table with the subnet
route_table.associate_with_subnet(SubnetId=subnet.id)


# Create sec group
sec_group = ec2.create_security_group(
    GroupName='slice_0', Description='slice_0 sec group', VpcId=vpc.id)
sec_group.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='icmp',
    FromPort=-1,
    ToPort=-1
)
print(sec_group.id)


# Create instance
instances = ec2.create_instances(
    ImageId=ec2_imageid, InstanceType=ec2_instancetype, MaxCount=1, MinCount=1,
    NetworkInterfaces=[{'SubnetId': subnet.id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True, 'Groups': [sec_group.group_id]}])
instances[0].wait_until_running()
print(instances[0].id)



