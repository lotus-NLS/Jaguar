import boto3

# Create a session
session = boto3.Session(
    region_name='eu-north-1'  # e.g., 'us-west-2'
)

ideal_instance_count = 5


# Create an EC2 resource
ec2 = session.resource('ec2')
with open(file='setup.sh') as f:
    user_data_script = f.read()

response = ec2.describe_instances(
    Filters=[
        {
            'Name': 'instance-state-name',
            'Values': ['running']
        }
    ]
)

running_instances = sum([len(reservation['Instances']) for reservation in response['Reservations']])

# instance.create_tags(
#     Tags=[{
#             'Key': 'Name',
#             'Value': 'LotusInstance'
#         }
#     ]
# )



instances_to_launch = ideal_instance_count - running_instances

# Launch additional instances if needed
if instances_to_launch > 0:
    new_instances = ec2.launch_instances(
        ImageId='ami-0fe8bec493a81c7da',
        MinCount=instances_to_launch,
        MaxCount=instances_to_launch,
        InstanceType='t3.micro',
        KeyName='your_key_name'
        # Add other parameters as needed
    )
    # instance.wait_until_running()
    # print("Instance is now running. IP Address:", instance.public_ip_address)
    print(f"Launched {instances_to_launch} new instances.")

else:
    print("No new instances needed.")
