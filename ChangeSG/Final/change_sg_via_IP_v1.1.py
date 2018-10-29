'''
This script is for changing security groups.
Please note that this script identify eni via only private address
Command: python -f <input_file> --profile=<profile>
'''

import boto3
import csv
import sys, getopt

# try:
#     opts, args = getopt.getopt(sys.argv[1:], 'f:', 'profile=')
# except:
#     print('Syntax Error! python -f <input_file> --profile=<profile>')
#
# try:
#     profile = opts[1][1]
# except:
#     profile = 'default'
# conf_file = opts[0][1]

conf_file = '1.csv'
profile = 'default'


def get_eni(ip):
    return eni_dict.get(ip, '')


# delete s_list from p_list.
# Return (post-del list, item_list in s_list that not found in p_list, deleted items in p_list).
def del_sub_list(s_list, p_list):
    not_found_item = []
    del_item = []
    for item in s_list:
        try:
            p_list.remove(item)
            del_item.append(item)
        except:
            not_found_item.append(item)
    return p_list, not_found_item, del_item


def replace_sg(input_row):
    ip = input_row[0]
    each_eni_id = get_eni(ip)
    if not each_eni_id:
        print('%s result: Error! %s does not exist.' % (ip, ip))
        return
    else:
        all_sg_ids = []
        sg_list = []
        for sg in input_row[1:]:
            if sg:
                sg_list.append(sg)
                all_sg_ids.append(sg_name_dict.get(sg, 'typo'))

        if all_sg_ids.count('typo'):
            print('Error! Unable to replace security groups of %s. Some security groups you typed does not exist.' % ip)
        elif len(all_sg_ids) > 5:
            print('Error! Security groups number limitation exceeded.')
        else:
            ec2.NetworkInterface(each_eni_id).modify_attribute(Groups=all_sg_ids)
            print(('Successfully! security groups of %s were replaced: ' + ', '.join(sg_list)) % ip)


def add_sg(input_row):
    ip = input_row[0]
    each_eni_id = get_eni(ip)
    if not each_eni_id:
        print('%s result: Error! %s does not exist.' % (ip, ip))
        return
    else:
        all_sg_ids = []
        add_sg_list = []
        for sg in input_row[1:]:
            if sg:
                add_sg_list.append(sg)
                all_sg_ids.append(sg_name_dict.get(sg, 'typo'))
        add_sg_list = list(set(add_sg_list))    # 去重
        all_sg_ids.extend(eni_sg[each_eni_id])
        all_sg_ids = list(set(all_sg_ids))       # 去重

        if all_sg_ids.count('typo'):
            print('Error! Unable to add security groups of %s. Some security groups you typed does not exist.' % ip)
        elif len(all_sg_ids) > 5:
            print('Error! Security groups number limitation exceeded.')
        else:
            ec2.NetworkInterface(each_eni_id).modify_attribute(Groups=all_sg_ids)
            print(('Successfully! ' + ', '.join(add_sg_list) + ' were added to %s') % ip)


def del_sg(input_row):
    ip = input_row[0]
    each_eni_id = get_eni(ip)
    if not each_eni_id:
        print('%s result: Error! %s does not exist.' % (ip, ip))
        return
    else:
        cur_sg_list = eni_sgname[each_eni_id]
        input_sg_list = [sg for sg in input_row[1:] if sg != '']
        del_sub_list_response = del_sub_list(input_sg_list, cur_sg_list)
        all_sg_list = del_sub_list_response[0]
        error_list = del_sub_list_response[1]
        del_list = del_sub_list_response[2]

        if not del_list:
            print('%s result: Warning! All security groups were not found.' % ip)
            return

        elif not all_sg_list:
            print('%s result: Error! You need to remain at least one security group.' % ip)

        else:
            all_sg_ids = [sg_name_dict[i] for i in all_sg_list]
            ec2.NetworkInterface(each_eni_id).modify_attribute(Groups=all_sg_ids)
            print('%s result: Successfully! ' % ip + ', '.join(del_list) + ' were removed.')
            if error_list:
                print('%s result: Warning! ' % ip + ', '.join(error_list) + ' were not found.')


boto3.setup_default_session(profile_name=profile)
client = boto3.client('ec2')
ec2 = boto3.resource('ec2')
sg_name_dict = {}
eni_dict = {}
eni_sg = {}
eni_sgname ={}

# dict {'sg_name': 'sg_id'} on aws
response_sg = client.describe_security_groups()
for sg in response_sg['SecurityGroups']:
    sg_name = sg['GroupName']
    try:
        sg_id = sg['GroupId']
    except:
        sg_id = ""
    sg_name_dict[sg_name] = sg_id

# eni_dict {'ip_address': 'eni_id'} ,
# eni_sg {'eni_id', [sg_id]}
# eni_sgname {'eni_id', [sg_name]}
response_eni = client.describe_network_interfaces()
for eni in response_eni['NetworkInterfaces']:
    eni_id = eni['NetworkInterfaceId']
    sg_id_list = []
    sg_name_list = []
    for each_ip in eni['PrivateIpAddresses']:
        ip_address = each_ip['PrivateIpAddress']
        eni_dict[ip_address] = eni_id
    for each_sg in eni['Groups']:
        sg_id_list.append(each_sg['GroupId'])
        sg_name_list.append(each_sg['GroupName'])
    eni_sg[eni_id] = sg_id_list
    eni_sgname[eni_id] = sg_name_list


# read csv file
with open(conf_file, 'r') as input_file:
    reader = csv.reader(input_file)
    rows = [row for row in reader]

# action
for each_row in rows[1:]:
    tag = each_row[0]
    if tag == 'replace':
        replace_sg(each_row[1:])
    if tag == 'add':
        add_sg(each_row[1:])
    if tag == 'del':
        del_sg(each_row[1:])
