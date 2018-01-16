# Infrastructure-Code 

## Usage

    python run_installation.py [options]
    
### Options
optional arguments:
  `-h` , `--help`            shows help message and CLI parameters. 
  
  `-p` *OSPASSWORD* , --password OSPASSWORD
                    password for os user.
                        
  `-dp` *DOCKERPASSWORD*, --dockerPassword DOCKERPASSWORD
                        password for UCP and DTR user.
                        
  `-l` *LICENSEFILEPATH*, --licensePath LICENSEFILEPATH
                        path to DockerEE license.
                        
  `-d` *DTRCOUNT*, --dtrs DTRCOUNT
                        the number of DTR instances to install.
                        
  `-wd` *WORKERDEVCOUNT*, --workersDev WORKERDEVCOUNT
                        the number of worker nodes to install.
                        
  `-wq` *WORKERQACOUNT*, --workersQa WORKERQACOUNT
                        the number of worker nodes to install.
                        
  `-ws` *WORKERSTRESSCOUNT*, --workersStress WORKERSTRESSCOUNT
                        the number of worker nodes to install.
                        
  `-wz` *WORKERDMZCOUNT*, --workersDMZ WORKERDMZCOUNT
                        the number of worker nodes to install.
                        
  `-wp` *WORKERPRODCOUNT*, --workersProd WORKERPRODCOUNT
                        the number of worker nodes to install.
                        
  `-md` *MANAGERDEVCOUNT*, --managersDev MANAGERDEVCOUNT
                        the number of manager nodes to install.
                        
  `-mq` *MANAGERQACOUNT*, --managersQa MANAGERQACOUNT
                        the number of manager nodes to install.
                        
  `-ms` *MANAGERSTRESSCOUNT*, --managersStress MANAGERSTRESSCOUNT
                        the number of manager nodes to install.
                        
  `-mz` *MANAGERDMZCOUNT*, --managersDMZ MANAGERDMZCOUNT
                        the number of manager nodes to install.
                        
  `-mp` *MANAGERPRODCOUNT*, --managersProd MANAGERPRODCOUNT
                        the number of manager nodes to install.
                        
## Configuration File
Bellow are fields and break down of each value used in the configuration file. 

#### This is the URL of the yum repo that must be added in order to get access to the docker-ee package

`docker.ee.url`: The urlkey given to you Docker for license ex: https://storebits.docker.com/ee/centos/sub-bcb3e940-2bc6-4eb0-85a2-3031e1f0508c

#### This is the yum repo that must be added to access the docker-ee package

`docker.ee.repo:` docker-ee.repo

#### Docker-ee package configuration values. For more information see the Docker EE manual on instalation. 

`docker.ee.package`: docker-ee

`block.disk.path`: second storage needed by Docker EE. ex:  /dev/sdb

`docker.disk.profile`: Ex: /etc/lvm/profile/docker-thinpool.profile

`docker.disk.profile.name`: Ex: docker-thinpool.profile

`docker.daemon.config`: Ex: /etc/docker/daemon.json

`docker.daemon.config.name`: Ex: daemon.json

`docker.user`: <YOUR_USERNAME>  This is the user that will manage the docker daemon

`docker.ucp.user`: This is the docker admin user Ex: admin

`bootstrap.user.path`: The working path used for executing and saving files.

`bootstrap.src.path`: The project path used for bootstraping or whatever you named the project ex <YOUR_WORKING_PATH> + </CODE_FOLDER>

`bootstrap.dest.path`: This can be the same as above or it can be different. This is used for the remote machines.

`docker.ports`: These is the list of firewall ports that must be opened Ex: 12376,12379,12380,12381,12382,12383,12384,12385,12386,12387,2376,2377,443,80

`docker.api.url`: your API URL may different based on your OS. Ex: https://index.docker.io/v1/

`docker.ucp.port`: This is the port that the UCP manager nodes listen on for API requests Ex: 2377


#### AWS Configuration. Note we are making an assumption that you breaking out zones out by subnet. 

`aws.access.key`: your AWS account access key

`aws.secret.key`: your AWS account secret key

`aws.pemFile`: Your .pem file

`aws.region`: AWS region ex: us-east-1

`aws.ami`: AMI ID ex: ami-######

`aws.worker`: EC2 type for a worker ex: m4.large

`aws.manager`: EC2 type for a manager m4.xlarge

`aws.securityGroupId`: Zone's / VPC security group id ex:  sg-########

`aws.dev`: Dev subnet id if setting up a dev zone

`aws.qa`: QA subnet id if setting up a qa zone 

`aws.stress`: Stress subnet id if setting up a stress zone

`aws.prod`: Production subnet id if setting up a prod zone

`aws.dmz`: DMZ subnet id if setting up s dmz zone subnet-02bf0649

`aws.hostedZone`: Route 53 hosted zone ID. 

`aws.domainName`: Route 53 domain name.


## Common Configuration 

## Configuring on-site setup 

## Configuring AWS setup
