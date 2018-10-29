'''
This script is for changing security groups.
Please note that this script identify eni via only private address
Command: python -f <input_file> --profile=<profile>
'''

import boto3
import csv
import sys, getopt

try:
    opts, args = getopt.getopt(sys.argv[1:], 'f:', 'profile=')
except:
    print('Syntax Error! python -f <input_file> --profile=<profile>')

try:
    profile = opts[1][1]
except:
    profile = 'default'


def get_eni(ip):
    return eni_dict.get(ip, '')


boto3.setup_default_session(profile_name=profile)
client = boto3.client('ec2')
ec2 = boto3.resource('ec2')
sg_name_dict = {}
eni_dict = {}

# dict {'sg_name': 'sg_id'} on aws
response_sg = client.describe_security_groups()
for sg in response_sg['SecurityGroups']:
    sg_name = sg['GroupName']
    try:
        sg_id = sg['GroupId']
    except:
        sg_id = ""
    sg_name_dict[sg_name] = sg_id

# dict {'ip_address': 'eni_id'} on aws
response_eni = client.describe_network_interfaces()
for eni in response_eni['NetworkInterfaces']:
    eni_id = eni['NetworkInterfaceId']
    for each_ip in eni['PrivateIpAddresses']:
        ip_address = each_ip['PrivateIpAddress']
        eni_dict[ip_address] = eni_id

# read csv file
with open(opts[0][1], 'r') as input_file:
    reader = csv.reader(input_file)
    rows = [row for row in reader]

for each_eni in rows[1:]:
    ip = each_eni[0]
    each_eni_id = get_eni(ip)
    if not each_eni_id:
        print(ip + ' does not exist!')
        continue
    else:
        all_sg_ids = []
        sg_list = []
        for sg in each_eni[1:]:
            if sg:
                sg_list.append(sg)
                all_sg_ids.append(sg_name_dict.get(sg, ''))

        # modify sg
        try:
            ec2.NetworkInterface(each_eni_id).modify_attribute(Groups=all_sg_ids)
            print(('security groups of %s were replaced successfully: ' + ', '.join(sg_list)) % ip)
        except:
            print('unable to replace security groups of %s. The security group you typed does not exist' % ip)
