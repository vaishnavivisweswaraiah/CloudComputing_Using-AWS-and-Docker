import paramiko
import boto3
import time,sys
import aws_boto_createInstances

def cpu_usuage_container():
    ec2_client=boto3.client("ec2")

    instances_details=ec2_client.describe_instances()
    #print(instances_details)

    username="ubuntu"
    #connect SSH_client
    ssh_client=paramiko.SSHClient()

    #Policy for automatically adding the hostname and new host key to the local HostKeys object
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    #load key
    key=paramiko.RSAKey.from_private_key_file("/Users/vaishnaviv/vaishnavi_ec2_key.pem")

    #installing docker on instances running
    error=[]
    for reservation in instances_details['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            if instance['State']['Name']=='running':
                try:
                    # connection to SSH server on instances at given publicdns id
                    ssh_client.connect(hostname=instance['PublicDnsName'], username=username, pkey=key)
                    stdin, stdout, stderror = ssh_client.exec_command("sudo apt-get -y update ")
                    stdout.channel.recv_exit_status()
                    stdin, stdout, stderror = ssh_client.exec_command("sudo apt-get install -y apt-utils")
                    stdout.channel.recv_exit_status()
                    stdin, stdout, stderror = ssh_client.exec_command("sudo apt autoremove docker docker-engine docker.io")
                    stdout.channel.recv_exit_status()
                    print("Docker installation in progress")
                    D_stdin, D_stdout, D_stderror = ssh_client.exec_command("sudo apt-get install -y docker.io")
                    D_stdout.channel.recv_exit_status()
                    # #print(stderror.readlines())
                    stdin, stdout, stderror = ssh_client.exec_command("sudo chmod 666 /var/run/docker.sock")
                    # print(stdout.readlines())
                    # print(stderror.readlines())
                    print("docker service start in progress")
                    stdin, stdout, stderror = ssh_client.exec_command('sudo systemctl start docker && sudo systemctl enable docker',get_pty=True)
                    print(stdout.readlines())
                    print("executing docker")
                    run_stdin, run_stdout, run_stderror = ssh_client.exec_command("sudo docker run -d -t ubuntu sh")
                    #print(run_stdout.readline())
                    container_id=run_stdout.readline().rstrip()
                    #print(container_id)
                    #print(run_stderror.readline())
                    print("succesfully ran docker whose created container id is {} on instance {}".format(container_id,instance_id))

                except Exception as e:
                    print(e)


    #fetch instance details and display cpu utilization
    #press contol+c to exit the while loop
    while(True):
            container_list=[]
            try:
                for reservation in instances_details['Reservations']:
                    for instance in reservation['Instances']:
                        instance_id=instance['InstanceId']
                        if instance['State']['Name']=='running':
                            #connection to SSH server
                            ssh_client.connect(hostname=instance['PublicDnsName'],username=username,pkey=key)
                            stdin, stdout, stderror = ssh_client.exec_command("sudo docker ps | grep ubuntu")
                            for output in stdout.readlines():
                                container_id=output.split()[0]
                                container_list.append(container_id)
                                stdin,stdout,stderror=ssh_client.exec_command("sudo docker exec {} top -bn1 | grep Cpu".format(container_id))
                                cpu_info=stdout.readline()
                                print("{} \t {} \t {}".format(instance_id,container_id,cpu_info))
                #sleep for 5 sec and run the loop again
                time.sleep(5)
                print("Press control+c to terminate the loop which executes every 5 seconds")

            except KeyboardInterrupt as e:
                print("Docker kill is in progress")
                for container_id in container_list:
                    ssh_client.exec_command("sudo docker kill {}".format(container_id))
                print("dockers killed sucessfully")
                _in,_out,_error=ssh_client.exec_command("sudo docker ps")
                #print(_out.readlines())
                # terminate all running instances .
                for i in aws_boto_createInstances.ec2.instances.all():
                    i.terminate()
                print("instances killed succesfully")

                sys.exit()
if __name__=="__main__":
    num_instances=2
    instances_created=aws_boto_createInstances.create_ec2_instances(int(num_instances))
    print("Creating {} EC2 instances".format(int(num_instances)))
    instance_running=[]
    #iteratively check status of the instance created
    for i in instances_created:
        print("Instances with {} id has startup status {} ".format(i.id, i.state))
        instance_running.append(aws_boto_createInstances.check_Instance_status(i.id))
    #print list of instances with running status
    print("list of instance id's with status code as running are \n",instance_running)
    #call to cpu utilization function
    time.sleep(20)
    cpu_usuage_container()

