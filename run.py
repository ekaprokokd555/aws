import boto3
import time
import paramiko

# Setup AWS Boto3 client
ec2 = boto3.client('ec2', region_name='us-west-2')  # Ganti dengan region yang sesuai
key_name = 'your-key-pair'  # Ganti dengan nama key pair AWS Anda
ami_id = 'ami-0c55b159cbfafe1f0'  # Ganti dengan ID AMI yang sesuai (Ubuntu 20.04, atau lainnya)
instance_type = 't2.micro'  # Ganti dengan instance type yang sesuai (t2.micro untuk Free Tier)
security_group_id = 'sg-xxxxxxxx'  # Ganti dengan ID security group yang sesuai

# 1. Membuat EC2 instance
def create_ec2_instance():
    response = ec2.run_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        KeyName=key_name,
        SecurityGroupIds=[security_group_id],
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [
                {'Key': 'Name', 'Value': 'MyProxyVPS'}
            ]
        }]
    )

    instance_id = response['Instances'][0]['InstanceId']
    print(f"EC2 Instance {instance_id} telah dibuat.")
    return instance_id

# 2. Menunggu hingga instance siap
def wait_for_instance(instance_id):
    waiter = ec2.get_waiter('instance_running')
    print("Menunggu instance siap...")
    waiter.wait(InstanceIds=[instance_id])
    print("Instance siap.")
    
    # Mendapatkan Public IP instance
    instance_info = ec2.describe_instances(InstanceIds=[instance_id])
    public_ip = instance_info['Reservations'][0]['Instances'][0]['PublicIpAddress']
    return public_ip

# 3. Menyiapkan SSH untuk mengonfigurasi proxy
def setup_proxy(public_ip):
    print(f"Terhubung ke instance dengan IP: {public_ip}")
    
    # Gunakan Paramiko untuk mengakses instance via SSH
    key = paramiko.RSAKey.from_private_key_file(f'/path/to/{key_name}.pem')  # Path ke private key file
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(public_ip, username='ubuntu', pkey=key)

    # Install Squid Proxy di VPS (contoh menggunakan Squid Proxy)
    commands = [
        "sudo apt-get update -y",
        "sudo apt-get install squid -y",
        "sudo service squid start",
        "sudo ufw allow 3128/tcp"  # Port default untuk Squid
    ]
    
    for command in commands:
        print(f"Menjalankan command: {command}")
        stdin, stdout, stderr = ssh_client.exec_command(command)
        print(stdout.read().decode())
        print(stderr.read().decode())

    print("Proxy server Squid telah terinstal dan dijalankan.")
    ssh_client.close()

# Main function untuk membuat VPS dan proxy
def main():
    # Langkah 1: Membuat EC2 instance
    instance_id = create_ec2_instance()
    
    # Langkah 2: Tunggu hingga instance siap
    public_ip = wait_for_instance(instance_id)
    
    # Langkah 3: Setup proxy pada instance
    setup_proxy(public_ip)

if __name__ == '__main__':
    main()
