This script is for adding, deleting and replacing security groups.Please note that this script identify ENI via only private address. Log file is "change_sg.log".
#######################################################################################
Action

del: this action will delete specific security group from specific IP. Error log will be created if you input a security group that does not exist or this IP does not have. Meanwhile, the correct one will be deleted.

add: this action will add specific security group to specific IP. Error log will be created if you input a security group that does not exist. Meanwhile, the correct one will be added in this condition.

replace: this action will replace all security groups of specific IP. Error log will be created if you input a security group that does not exist. Please note that no security groups will be replaced if this error happens.

#######################################################################################

Env requirement

python/python3, boto3

#######################################################################################
Command: python -f <input_file> --profile=<profile>

example: "python3 -f input.csv --profile=prd"
	 "python -f 1.csv"

If you do not input profile parameter, default profile will be set to "default".