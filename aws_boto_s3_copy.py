import boto3
import botocore
import uuid,time

#generates unique bucket name
def generate_bucket_name(bucketName):
    #generates unique bucket name with bucketName argument as prefix for readable bucket name
    return "".join([bucketName,str(uuid.uuid4())])


#create bucket at particular location where boto3 creates the session
def create_bucket(bucketName,s3):
    session=boto3.session.Session()
    region=session.region_name
    bucketName=generate_bucket_name(bucketName)
    #print(bucketName,region)
    if region == 'us-east-1':
        response=s3.create_bucket(Bucket=bucketName)
    else:
        response=s3.create_bucket(ucket=bucketName,CreateBucketConfiguration={'LocationConstraint': region})

    return bucketName,response

#making bucket public
def make_bucket_public(bucket_name):
    time.sleep(1)
    s3.put_bucket_acl(Bucket=bucket_name,ACL='public-read-write')
    print("ACL set to public - read - write for bucket {}".format(bucket_name))


#copy files from one bucket to another
def bucket_copy(source_bucket_name,destination_bucket_name,key_filename):
    source= {'Bucket':source_bucket_name,'Key':key_filename}
    s3.copy(source,destination_bucket_name,key_filename)
    print("File {} sucessfully copied from {} to {}".format(key_filename,source_bucket_name,destination_bucket_name))

#read contents of bucket
def read_files(bucketName,key):
    data=s3.get_object(Bucket=bucketName,Key=key)
    #(data)
    return data['Body'].read().decode()

#perform operations on bucket
#check for existance of bucket
#check if bucket is not empty

def Bucket_operations(source_bucket_name,destination_bucket_name):
    #code to check if bucket is not empty
    exists=True
    try:
        s3.head_bucket(Bucket=source_bucket_name)
        print("{} Bucket exist".format(source_bucket_name))
    except botocore.exceptions.ClientError as e:
        #check for any exception if error is 404 bucket does not exist
        #throw execption that the given bucket does not exist
        error_code=int(e.response['Error']['Code'])
        if error_code==404:
            print("{} Bucket does not exist".format(source_bucket_name))
            exists=False
    # perform file read and copy file content to destination bucket if bucket is not empty
    if (exists):
        #finding all files in source bucket
        http_response = s3.list_objects_v2(Bucket=source_bucket_name)
        #return file names if files exist else store None in Keys_exist
        keys_exist=http_response.get('Contents')
        if keys_exist!=None:
                for file_metadata in http_response.get('Contents',[]):
                        key = file_metadata['Key']
                    #if file_metadata['Size']!=0:
                        try:
                                # read contents in files
                                content = read_files(source_bucket_name, key)
                                print("=======" * 10)
                                print("Filename name : {}".format(key))
                                # print content
                                print("*******"*10)
                                print(content)
                                print("*******"*10)
                                # copying files to bucket
                                bucket_copy(source_bucket_name, destination_bucket_name, key)
                        except Exception as e:
                            #exception will be passed if directory or file is empty
                            pass
                    #else:
                    #    print("{} file is empty".format(key))
        else:
            print("Bucket is empty")


#create resource s3

if __name__=="__main__":
    s3=boto3.client('s3')
    source_bucket_name="wsu2017fall"
    destination_bucket_name,b_response=create_bucket("vaishnavi-cc-bucket",s3)
    print("My bucket Name{}".format(destination_bucket_name))
    make_bucket_public(destination_bucket_name)
    Bucket_operations(source_bucket_name,destination_bucket_name)
