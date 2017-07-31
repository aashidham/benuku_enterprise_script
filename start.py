import boto.ec2
import sys

print "This script will install an on-prem Benuku box inside the us-west-2 AWS zone."
print
print "First step: your AWS credentials. Both access key and secret access keyare found here: https://console.aws.amazon.com/iam/home?region=us-west-2#/security_credential"

AWS_ACCESS_KEY = raw_input("AWS access key: ")
AWS_SECRET = raw_input("AWS secret access key: ")

print
print "Second step: your Benuku license key. You should have received this in an email or at benuku.com."
ben_license = raw_input("Benuku license key: ")

user_data_script = """#!/bin/bash
echo "%s" >> /home/ubuntu/license.key""" % ben_license

conn = boto.ec2.connect_to_region("us-west-2",aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET)

sg_name = 'onprem0'
rs = conn.get_all_security_groups()
need_new_sg = True
for c in rs:
    if c.name == sg_name:
        need_new_sg = False

if(need_new_sg):
    print "making new security group, called",sg_name
    sg = conn.create_security_group(sg_name,sg_name)
    sg.authorize('tcp', 80, 80, '0.0.0.0/0')
    sg.authorize('tcp', 8000, 8000, '0.0.0.0/0')
    sg.authorize('tcp', 443, 443, '0.0.0.0/0')
    sg.authorize('tcp', 22, 22, '0.0.0.0/0')
else:
    print "using existing security group, called",sg_name



key_pairs_arr = [c.name for c in conn.get_all_key_pairs()]
if len(key_pairs_arr):
    print "using keypair",key_pairs_arr[0]
else:
    print "no keypairs in us-west-2, so I need to exit"
    sys.exit()


dev_sda1 = boto.ec2.blockdevicemapping.EBSBlockDeviceType()
dev_sda1.size = 30
bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
bdm['/dev/sda1'] = dev_sda1

o1 = conn.run_instances('ami-ba27c3c2', user_data=user_data_script,  instance_type='t2.large', security_groups=[sg_name] , key_name= key_pairs_arr[0],  block_device_map = bdm)

print o1
print "Go to your EC2 console, you should see the Benuku box loading. Happy coding!"
