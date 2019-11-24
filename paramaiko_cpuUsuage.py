import paramiko
import boto3
import time
import aws_boto_createInstances

def cpu_utilization():
    ec2_client=boto3.client("ec2")

    instances_details=ec2_client.describe_instances()

    #print(ec2_client.describe_instance_status())

    username="ubuntu"
    #connect SSH_client
    ssh_client=paramiko.SSHClient()

    #Connect to an SSH server and authenticate to it. The server’s host key is checked against the system host keys
    ssh_client.load_system_host_keys()

    #Policy for automatically adding the hostname and new host key to the local HostKeys object
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    #load key
    key=paramiko.RSAKey.from_private_key_file("your_ec2_key.pem path")


    #fetch instance details and display cpu utilization
    while(True):
        for reservation in instances_details['Reservations']:
            for instance in reservation['Instances']:
                instance_id=instance['InstanceId']
                if instance['State']['Name']=='running':
                    #connection to SSH server
                    ssh_client.connect(hostname=instance['PublicDnsName'],username=username,pkey=key)
                    stdin,stdout,stderror=ssh_client.exec_command("top -bn1 | grep Cpu")
                    cpu_info = stdout.readline()
                    print("%s \t %s"%(instance_id,cpu_info))
        time.sleep(5)


if __name__=="__main__":

    num_instances = 2
    instances_created = aws_boto_createInstances.create_ec2_instances(int(num_instances))
    print("Creating {} EC2 instances".format(int(num_instances)))
    instance_running=[]
    #iteratively check status of the instance created
    for i in instances_created:
        print("Instances with {} id has startup status {} ".format(i.id, i.state))
        instance_running.append(aws_boto_createInstances.check_Instance_status(i.id))
    #print list of instances with running status
    print("list of instance id's with status code as running are \n",instance_running)
    time.sleep(10)
    cpu_utilization()

    # terminate all running instances .
    # for i in aws_boto_createInstances.ec2.instances.all():
    #     i.terminate()

