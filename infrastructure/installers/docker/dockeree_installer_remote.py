'''
Created on Nov 17, 2017

@author: shoffman
'''

import infrastructure.installers.core.os_executor as os_executor
import os

# There is a yum module on RHEL and centos.  However, this API is not very well documented.
# At this time we are going to make the yum calls from the command line for this reason.


#==============================================================================
# Paramters:
#   logger   - This is the logger used to record log messages.
#   config   - This is the dict of configuration parameters that are obtained 
#              from the base.yaml file.
#   host     - This is the host being logged into to execute the command.
#   password - This is the password to be to login to remote servers via ssh.
# Description: This function will coordinate the installation of Docker EE on the
#              remote host.  
#==============================================================================
def executeDockerInstall(logger, config, host, password):
    isExecuteSuccess = False
    
    logger.debug('+++ Beginning environment set up on ' + host + '. +++')
    isExecuteSuccess = preInstallConfig(logger, config, host, password)
    
    if isExecuteSuccess is True:
        logger.debug('+++ Beginning installation of Docker EE +++')
        isExecuteSuccess = installDockerEE(logger, config, host, password)

    else:
        logger.error('An error was encountered setting the environment up.')

    if isExecuteSuccess is True:
        logger.debug('+++ Successfully finished the installation of Docker EE +++')
        logger.debug('+++ Beginning the configuration of the logical volume +++')
        isExecuteSuccess = configLogicalVolume(logger, config, host, password)

    else:
        logger.error('An error was encountered installing Docker EE')
    
    if isExecuteSuccess is True :
        logger.debug('+++ Successfully finished the configuration of the logical volume +++')
        logger.debug('+++ Beginning post installation configuration +++')
        isExecuteSuccess = postInstallationConfig(logger, config, host, password)

    else:
        logger.error('An error was encountered configuring the logical volume')

    if isExecuteSuccess is True:
        isExecuteSuccess = True 
        logger.debug('+++ Successfully finished post installation configuration +++')

    else:
        logger.error('An error was encountered carrying out the post installation configuration')
    
    return isExecuteSuccess


#==============================================================================
# Paramters:
#   logger   - This is the logger used to record log messages.
#   config   - This is the dict of configuration parameters that are obtained 
#              from the base.yaml file.
#   host     - This is the host being logged into to execute the command.
#   password - This is the password to be to login to remote servers via ssh.
# Description: This function add the Docker yum repo, so that Docker EE can be
#              installed.  
#==============================================================================
def preInstallConfig(logger, config, host, password):
    isExecuteSuccess = False
  
    cmd = "sh -c 'echo \"" + config['docker.ee.url'] + "/centos\" > /etc/yum/vars/dockerurl'"
    output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
  
  # if 'error' not in output.lower():
    logger.debug('Successfully added Docker URL to yum URLs')
    cmd = 'yum install -y yum-utils device-mapper-persistent-data lvm2'
    output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
  
  # else:
  #  logger.debug('An error was encountered adding Docker URL to yum URLs.')
   
  # if 'error' not in output.lower():
    logger.debug('Successfully installed yum-utils device-mapper-persistent-data lvm2')
    cmd = 'yum-config-manager --add-repo "' + config['docker.ee.url'] + '/centos/docker-ee.repo"'
    output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
  
  # else:
  #  logger.debug('An error was encountered installing yum-utils device-mapper-persistent-data lvm2.')
  
  # if 'error' not in output.lower():
    isExecuteSuccess = True
    logger.debug('Successfully added Docker repo.')
    
  # else:
  #  logger.debug('An error was encountered adding Docker repo.')
    
    return isExecuteSuccess

    
#==============================================================================
# Paramters:
#   logger   - This is the logger used to record log messages.
#   config   - This is the dict of configuration parameters that are obtained 
#              from the base.yaml file.
#   host     - This is the host being logged into to execute the command.
#   password - This is the password to be to login to remote servers via ssh.
# Description: This function will install DockerEE.  Upon completion of the 
# installation, the daemon is started to create the initial directories.  If 
# this is not done, then when the daemon.json file is created it will be
# overwritten on the first start.  The daemon is then stopped to get it ready
# for the creation of the logical volume.  
#==============================================================================
def installDockerEE(logger, config, host, password):
    isExecuteSuccess = False
  
    cmd = 'yum -y install docker-ee'
    output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
  
  # if 'error' not in output.lower():
    logger.debug('Successfully installed Docker EE')
    cmd = 'service docker start'
    output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
  
  # else:
  #  logger.debug('An error was encountered installing Docker EE')
    
  # if 'error' not in output.lower():
    cmd = 'service docker stop'
    output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
  
  # else:
    logger.debug('An error was encountered starting Docker service')

  # if 'error' not in output.lower():
    isExecuteSuccess = True
  
  # else:
  #  logger.debug('An error was encountered stopping Docker service')
  
    return isExecuteSuccess


#===============================================================================
# Paramters:
#   logger   - This is the logger used to record log messages.
#   config   - This is the dict of configuration parameters that are obtained from 
#              the base.yaml file.
#   host     - This is the host being logged into to execute the command.
#   password - This is the password to be to login to remote servers via ssh.
# Description: This function will create a logical volume configured as a thin 
# pool to use as backing for the storage pool. It assumes that you have a spare 
# block device at /dev/xvdf with enough free space to complete the task. The 
# device identifier and volume sizes may be different in your environment and you 
# should substitute your own values throughout the procedure. The procedure also 
# assumes that the Docker daemon is in the stopped state. 
#===============================================================================
def configLogicalVolume(logger, config, host, password):
    isExecuteSuccess = False
      
    cmd = 'yum install -y yum-utils device-mapper-persistent-data lvm2'
    output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
    
    if 'error' not in output.lower():
        cmd = 'pvcreate ' + config['block.disk.path']
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)

    else:
        logger.debug('An error was encountered installing device-mapper-persistent-data and lvm2 packages')

    if 'error' not in output.lower():
        cmd = 'vgcreate docker ' + config['block.disk.path']
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)

    else:
        logger.debug('An error was encountered creating the physical volume')

    if 'error' not in output.lower():
        cmd = 'lvcreate --wipesignatures y -n thinpool docker -l 95%VG'
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)

    else:
        logger.debug('An error was encountered creating the volume group')

    if 'error' not in output.lower():
        cmd = 'lvcreate --wipesignatures y -n thinpoolmeta docker -l 1%VG'
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)

    else:
        logger.debug('An error was encountered creating the logical volume thinpool docker')

    if 'error' not in output.lower():
        cmd = 'lvconvert -y --zero n -c 512K --thinpool docker/thinpool --poolmetadata docker/thinpoolmeta'
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)

    else:
        logger.debug('An error was encountered creating logical volume thinpoolmeta docker')

    if 'error' not in output.lower():
        filePath = config['docker.disk.profile']
        content = 'activation { \n thin_pool_autoextend_threshold=80 \n thin_pool_autoextend_percent=20 \n }'
        os_executor.updateFile(logger, filePath, content)
        
        src = config['docker.disk.profile']
        dest = config['bootstrap.user.path'] + config['docker.disk.profile.name']
        os_executor.transferFile(logger, config, host, password, src, dest)
        
        cmd = 'mv ' + dest + ' ' + src
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)

    else:
        logger.debug('An error was encountered while changing the mirrored volume configuration')

    if 'error' not in output.lower():
        cmd = 'lvchange --metadataprofile docker-thinpool docker/thinpool'
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)

    else:
        logger.debug('An error was encountered while updating the disk profile')
          
    if 'error' not in output.lower():
        cmd = 'lvs -o+seg_monitor'
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)

    else:
        logger.debug('An error was encountered while applying the LVM profile')

    if 'error' not in output.lower():
        filePath = config['bootstrap.user.path'] + config['docker.daemon.config.name']
        content = '{ \n "storage-driver": "devicemapper", \n "storage-opts": [ \n "dm.thinpooldev=/dev/mapper/docker-thinpool", \n "dm.use_deferred_removal=true", \n "dm.use_deferred_deletion=true" \n ]}'
        os_executor.updateFile(logger, filePath, content)
        
        src = filePath
        dest = config['docker.daemon.config']
        os_executor.transferFile(logger, config, host, password, src, src)
        
        cmd = 'mv ' + src + ' ' + dest
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
    else:
        logger.debug('An error was encountered while creating a linux virtual server')

    if 'error' not in output.lower():
        os.remove(filePath)
        cmd = 'service docker start'
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)

    else:
        logger.debug('An error was encountered while updating daemon.json')

    if 'error' not in output.lower():
        isExecuteSuccess = True

    else:
        logger.debug('An error was encountered starting Docker service')

    return isExecuteSuccess


#===============================================================================
# Paramters:
#   logger   - This is the logger used to record log messages.
#   config   - This is the dict of configuration parameters that are obtained from 
#              the base.yaml file.
#   host     - This is the host being logged into to execute the command.
#   password - This is the password to be to login to remote servers via ssh.
# Description: This function will configure a new non-root user to be able to 
# manage Docker.  It will also configure Docker to start on system start-up. 
#===============================================================================
def postInstallationConfig(logger, config, host, password):
    isExecuteSuccess = False  
    cmd = 'usermod -a -G docker ' + config['docker.user']
    output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
    
    if 'error' not in output.lower():
        cmd = 'systemctl enable docker'
        isExecuteSuccess = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
    
    else:
        logger.debug('An error was encountered while adding docker group to ' + config['docker.user'])

    if 'error' not in output.lower():
        ports = config['docker.ports']
        ports = ports.split(',')
        os_executor.openFirewallPorts(logger, config, ports, host, password)

    else:
        logger.debug('An error was encountered while configuring the Docker service to start on system start')

    if 'error' not in output.lower():
        isExecuteSuccess = True

    else:
        logger.debug('An error was encountered while opening the firewall ports')

    return isExecuteSuccess
