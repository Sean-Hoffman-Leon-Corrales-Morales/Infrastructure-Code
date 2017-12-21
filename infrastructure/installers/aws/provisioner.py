'''
Created on Dec 14, 2017

@author: Leon Corrales Morales


'''
import boto3


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
        self.config = config
        self.logger = logger
        for key, value in self.config.iteritems():
            logger.debug('- ' + key + ': ' + str(value))
        logger.debug("config in provisioner is now " + str(self.config))

#==============================================================================
# Description: Simple getters for managers and works
#==============================================================================
    def getManagers(self):
        return self.managers
    
    def getWorkers(self):
        return self.workers

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
        self.setworkers(stressCountWorker, self.config['aws.stress'])
        self.setworkers(dmzCountWorker, self.config['aws.dmz'])
        self.setworkers(prodCountWorker, self.config['aws.prod'])
            
        return self.workers

#==============================================================================
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
            awsInst = self.createWorker(i, zone)
            self.logger.debug("adding " + str(awsInst[0].private_ip_address))
            awsInst[0].wait_until_running()
            self.workers.append(awsInst[0].private_ip_address)

#==============================================================================
# Paramters:
#   count    - Number AWS instances to loop through
#   zone     - Zone to create workers e.g qa, dev ... etc
#
# Description: works as helper append a new manager IP address and send AWS info
#==============================================================================    
    def setManagers(self, count, zone):
        for i in range(1, count + 1):
            awsInst = self.createManager(i, zone)
            self.logger.debug("adding " + str(awsInst[0].private_ip_address))
            awsInst[0].wait_until_running()
            
            self.managers.append(awsInst[0].private_ip_address)
            
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
            newInst = ec2.create_instances(ImageId=self.config['aws.ami'],
                                 InstanceType=self.config['aws.worker'],
                                 SecurityGroupIds=[self.config['aws.securityGroupId']],
                                 MinCount=1,
                                 MaxCount=1,
                                 SubnetId=zone,
                                 TagSpecifications=[{
                                     'ResourceType': 'instance',
                                        'Tags': [{
                                            'Key': 'Name',
                                            'Value': 'dockerNode-' + str(count)}
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
        newInst = ec2.create_instances(ImageId=self.config['aws.ami'],
                                 InstanceType=self.config['aws.manager'],
                                 SecurityGroupIds=[self.config['aws.securityGroupId']],
                                 MinCount=1,
                                 MaxCount=1,
                                 SubnetId=zone,
                                 TagSpecifications=[{
                                     'ResourceType': 'instance',
                                        'Tags': [{
                                            'Key': 'Name',
                                            'Value': 'dockerManager-' + str(count)}
                                        ]}
                                 ])
        return newInst
    
