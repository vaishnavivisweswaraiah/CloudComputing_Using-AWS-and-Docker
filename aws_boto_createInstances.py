import boto3
import time
import sys

ec2=boto3.resource('ec2')


#check status of created instances
def check_Instance_status(instance_id):

    status = True # not running
    while(status):
        i=ec2.Instance(instance_id)
        #print(i.state['Code'])
        #check condition for "pending" and if pending sleep for 10 secs
        if i.state['Code']==0:
            time.sleep(10)
            status=True
        #check condition  for shutting-down ,terminated,stopping and stopped,if instance status condition is met break loop with current status of instance
        elif i.state['Code']==32 or i.state['Code']==48 or i.state['Code']==64 or i.state['Code']==80 :
             if i.state['Code']==32 :
                 error_status = 'Shutting-down'
             elif i.state['Code']==48 :
                 error_status = 'Terminated'
             elif i.state['Code'] == 64:
                 error_status = 'Stopping'
             elif i.state['Code']==80:
                 error_status = 'Stopped'
             print("Instance {} has problem to start up or {}".format(instance_id,error_status))
             instance_id=None
             status=False
        #condition check for "running" status of ec2 instance
        elif i.state['Code']==16:
            print("Instance {} has sucessfully started/running".format(instance_id))
            status = False

    return instance_id

#create ec2 instance
def create_ec2_instances(count_instances):
    #creates required number of instances for given ImageId
    return ec2.create_instances(ImageId='ami-cd0f5cb6',InstanceType='t2.micro',SecurityGroupIds=['sg-0b0b764f630fcea2c'], \
                                     SubnetId='subnet-9a1a1eb4', MaxCount=count_instances, MinCount=1, KeyName='vaishnavi_ec2_key')


if __name__=="__main__":
    num_instances=sys.argv[1]
    instances_created=create_ec2_instances(int(num_instances))
    print("Creating {} EC2 instances".format(int(num_instances)))
    instance_running=[]
    #iteratively check status of the instance created
    for i in instances_created:
        print("Instances with {} id has startup status {} ".format(i.id, i.state))
        instance_running.append(check_Instance_status(i.id))
    #print list of instances with running status
    print("list of instance id's with status code as running are \n",instance_running)

    #terminate all running instances .
    for i in ec2.instances.all():
        i.terminate()
