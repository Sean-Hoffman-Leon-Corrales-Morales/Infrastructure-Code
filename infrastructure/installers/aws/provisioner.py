'''
Created on Dec 14, 2017

@author: Leon Corrales Morales


'''
import boto3, multiprocessing
from datetime import datetime
#from threading import Thread

class provisioner(object):

#==============================================================================
# Class constructor required Paramters:
#   config   - This is the dict of configuration parameters that are obtained 
#              from the base.yaml file.
# Description: This class is responsible for the provisioning AWS EC2 and S3
#              instances using boto3.  
#==============================================================================
    def __init__(self, config, logger):
        self.workers = []
        self.managers = []
        self.managersId = []
        self.worksId = []
        self.config = config
        self.logger = logger

#==============================================================================
# Description: Simple getters for managers and works
#==============================================================================
    def getManagers(self):
        return self.managers
    
    def getWorkers(self):
        return self.workers
    
    def getManagersId(self):
        return self.managersId
    
    def getWorkersId(self):
        return self.worksId
    
#==============================================================================
# Paramters:
#   qaCountWorker    - This is the amount of EC2 docker-ee workers instances
#                      to create in QA.
#   devCountWorker   - This is the amount of EC2 docker-ee worker instances 
#                      to create in Dev.
#   stressCountWorker- This is the amount of EC2 docker-ee worker instances 
#                      to create in stress.
#   dmzCountWorker   - This is the amount of EC2 docker-ee worker instances 
#                      to create in the dmz.
#   prodCountWorker  - This is the amount of EC2 docker-ee worker instances 
#                      to create in production.
#
# Description: This method is used to provion a set number of workers to each region.
#              returns an array of ip address of the new instances.  
#==============================================================================
    def provisionWorkers(self, qaCountWorker, devCountWorker, stressCountWorker,
                         dmzCountWorker, prodCountWorker):
        
        self.setWorkers(devCountWorker, self.config['aws.dev'])
        self.setWorkers(qaCountWorker, self.config['aws.qa'])
        self.setWorkers(stressCountWorker, self.config['aws.stress'])
        self.setWorkers(dmzCountWorker, self.config['aws.dmz'])
        self.setWorkers(prodCountWorker, self.config['aws.prod'])
            
        return self.workers

#==============================================================================
# @Depricated 
# Paramters:
#   qaCountWorker    - This is the amount of EC2 docker-ee managers instances
#                      to create in QA.
#   devCountWorker   - This is the amount of EC2 docker-ee managers instances 
#                      to create in Dev.
#   stressCountWorker- This is the amount of EC2 docker-ee managers instances 
#                      to create in stress.
#   dmzCountWorker   - This is the amount of EC2 docker-ee managers instances 
#                      to create in the dmz.
#   prodCountWorker  - This is the amount of EC2 docker-ee managers instances 
#                      to create in production.
#
# Description: This method is used to provion a set number of Docker managers
#              to each region. Returns an array of ip address of the new instances.  
#==============================================================================
    def provisionManagers(self, qaCountManager, devCountManager,
                          stressCountManager, dmzCountManager, prodCountManager):
        
        self.setManagers(devCountManager, self.config['aws.dev'])
        self.setManagers(qaCountManager, self.config['aws.qa'])
        self.setManagers(stressCountManager, self.config['aws.stress'])
        self.setManagers(dmzCountManager, self.config['aws.dmz'])
        self.setManagers(prodCountManager, self.config['aws.prod'])
            
        return self.managers
    
#==============================================================================
# Paramters:
#   count    - Number AWS instances to loop through
#   zone     - Zone to create workers e.g qa, dev ... etc
#
# Description: works as helper append a new worker IP address and send AWS info
#==============================================================================
    def setWorkers(self, count, zone):
        for i in range(1, count + 1):
            #p = multiprocessing.Process(target=self.createEC2, args=(i, zone, False,))
            #p.start()
            #p.join()
            self.createEC2(i, zone, False)
        
        
#==============================================================================
# Paramters:
#   count    - Number AWS instances to loop through
#   zone     - Zone to create workers e.g qa, dev ... etc
#
# Description: works as helper append a new manager IP address and send AWS info
#==============================================================================    
    def setManagers(self, count, zone):
        for i in range(1, count + 1):
            #p = multiprocessing.Process(target=self.createEC2, args=(i, zone, True,))
            #p.start()
            #p.join()
            self.createEC2(i, zone, True)

#==============================================================================
# Paramters:
#   i        - This EC2's number whithin it's set
#   zone     - Zone to create workers e.g qa, dev ... etc
#   ismanager- Is this node a manger true/false
# Description: provisions either a Docker manager node or worker node using for 
#              a given count and zone. This is a consolidated function from old
#              code. 
#==============================================================================                
            
    def createEC2(self, i, zone, isManager):
            if(isManager):
                awsInst = self.createManager(i, zone)
            else:
                awsInst = self.createWorker(i, zone)
                
            self.logger.debug("adding " + str(awsInst[0].id) + " in " + zone)
            awsInst[0].wait_until_running()
            client = boto3.client('ec2',region_name=self.config['aws.region'],
                                   aws_access_key_id=self.config['aws.access.key'],
                                   aws_secret_access_key=self.config['aws.secret.key'])
            waiter = client.get_waiter('instance_status_ok')
            waiter.wait(InstanceIds=[str(awsInst[0].id)], IncludeAllInstances=True)
            if(isManager):
                self.managers.append(awsInst[0].private_ip_address)
                self.managersId.append(awsInst[0].id)
                fqdn = 'dockerManager-' + zone + '-' + str(i)
                route53 = self.addRoute53(fqdn, awsInst[0].private_ip_address)
                self.logger.debug("DNS route: " + str(route53) )
            else:
                self.workers.append(awsInst[0].private_ip_address)
                self.worksId.append(awsInst[0].id)
                fqdn = 'dockerNode-' + zone + '-' + str(i)
                route53 = self.addRoute53(fqdn, awsInst[0].private_ip_address)
                self.logger.debug("DNS route: " +str(route53))
            
#==============================================================================
# Paramters:
#   count    - Number AWS instances to loop through
#   zone     - Zone to create workers e.g qa, dev ... etc
#
# Description: template aws boto3 method for creating and instance. returns the
#              returns the entire instance to the setworker method.
#============================================================================== 
    def createWorker(self, count, zone): 
        if count > 0: 
            ec2 = boto3.resource('ec2', self.config['aws.region'], None , None , None , None , self.config['aws.access.key'], self.config['aws.secret.key'], None, None)
            newInst = ec2.create_instances(
                                 BlockDeviceMappings=[
                                    {
                                        'DeviceName': self.config['block.disk.path'],
                                        'VirtualName': 'dockerWorker-'+ str(count) + '-' + zone + '-Drive',
                                        'Ebs': {
                                            'DeleteOnTermination': True,
                                            'VolumeSize': 30,
                                            'VolumeType': 'gp2'
                                        },
                                    },
                                ],
                                 ImageId=self.config['aws.ami'],
                                 InstanceType=self.config['aws.worker'],
                                 SecurityGroupIds=[self.config['aws.securityGroupId']],
                                 MinCount=1,
                                 MaxCount=1,
                                 SubnetId=zone,
                                 TagSpecifications=[{
                                     'ResourceType': 'instance',
                                        'Tags': [{
                                            'Key': 'Name',
                                            'Value': 'dockerNode-' + zone + '-' + str(count)}
                                        ]}
                                 ])
            
            # newinst[0].private_ip_address
            return newInst
    
#==============================================================================
# Paramters:
#   count    - Number AWS instances to loop through
#   zone     - Zone to create workers e.g qa, dev ... etc
#
# Description: template aws boto3 method for creating and instance. returns the
#              returns the entire instance to the setmanager method.
#==============================================================================     
    def createManager(self, count, zone): 
        ec2 = boto3.resource('ec2', self.config['aws.region'], None , None , None , None , self.config['aws.access.key'], self.config['aws.secret.key'], None, None)
        newInst = ec2.create_instances(
                                    BlockDeviceMappings=[
                                    {
                                        'DeviceName': self.config['block.disk.path'],
                                        'VirtualName': 'dockerManager-'+ str(count) + '-' + zone + '-Drive',
                                        'Ebs': {
                                            'DeleteOnTermination': True,
                                            'VolumeSize': 30,
                                            'VolumeType': 'gp2'
                                        },
                                    },
                                ],
                                 ImageId=self.config['aws.ami'],
                                 InstanceType=self.config['aws.manager'],
                                 SecurityGroupIds=[self.config['aws.securityGroupId']],
                                 MinCount=1,
                                 MaxCount=1,
                                 SubnetId=zone,
                                 TagSpecifications=[{
                                     'ResourceType': 'instance',
                                        'Tags': [{
                                            'Key': 'Name',
                                            'Value': 'dockerManager-'+ zone + '-' + str(count)}
                                        ]}
                                 ])
        return newInst
    
#==============================================================================
# Paramters:
#   fqdn          - DNS name for a resources ex: somthing-somthing -> something.somthing.[aws.domainName]
#   ipaddress     - IP address of the host being registered for as the resource
#
# Description: Used to create a DNS entry using AWS route53.
#==============================================================================       
    def addRoute53(self, fqdn, ipAddress ):
        startTime = datetime.now()
        fqdn = fqdn.replace('-', '.')
        client = boto3.client('route53',region_name=self.config['aws.region'],
                                   aws_access_key_id=self.config['aws.access.key'],
                                   aws_secret_access_key=self.config['aws.secret.key'])
        response = client.change_resource_record_sets(
            HostedZoneId=self.config['aws.hostedZone'],
            ChangeBatch={
                'Comment': 'Automated DNS entry.' ,
                'Changes': [
                    {
                        'Action':'UPSERT',
                        'ResourceRecordSet': {
                            'Name': fqdn +"." + self.config['aws.domainName'],
                            'Type': 'A',
                            'SetIdentifier': fqdn +"."+ self.config['aws.domainName'],
                            'Region': self.config['aws.region'],
                                'TTL': 180,
                                'ResourceRecords': [
                                    {
                                        'Value': ipAddress
                                    },
                                ],
                            }
                        },
                    ]
                }
            )
        #this wait is kinda costly/inefficient beacuse it's waiting one by one.
        waiter = client.get_waiter('resource_record_sets_changed')
        waiter.wait(
            Id=response['ChangeInfo']['Id'],
            WaiterConfig={
                'Delay': 15,
                'MaxAttempts': 40
                }
            )
        
        self.logger.debug("ROUTE53 ID: " + response['ChangeInfo']['Id'] + " exec time: " + str(datetime.now() - startTime) + "added DNS:" + fqdn +"." + self.config['aws.domainName'].rstrip('.') + " -> " + str(ipAddress))
        return fqdn +"." + self.config['aws.domainName'].rstrip('.')
