import boto3
import csv
profile = "default"


def get_instance(instance_name):
    ec2 = boto3.resource('ec2')
    return ec2.instances.filter(Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}])


boto3.setup_default_session(profile_name=profile)
ec2 = boto3.client('ec2')
ec2_list = []
sg_name_dict = {}

# dict all {'sg_name': 'sg_id'} on aws
response = ec2.describe_security_groups()
for sg in response['SecurityGroups']:
    sg_name = sg['GroupName']
    try:
        sg_id = sg['GroupId']
    except:
        sg_id = ""
    sg_name_dict[sg_name] = sg_id

# read csv file
with open('input.csv', 'r') as input_file:
    reader = csv.reader(input_file)
    rows = [row for row in reader]

for server_list in rows[1:]:
    instance_name = server_list[0]
    each_instance = get_instance(instance_name)
    all_sg_ids = []
    sg_list = []
    for sg in server_list[1:]:
        if sg:
            sg_list.append(sg)
            all_sg_ids.append(sg_name_dict.get(sg, ''))

    # modify sg
    try:
        for i in each_instance:
            i.modify_attribute(Groups=all_sg_ids)
            print(instance_name + ' replace security group successfully: ' + ', '.join(sg_list))
    except:
        print(instance_name + ': unable to replace security group. The security group you typed does not exist')

