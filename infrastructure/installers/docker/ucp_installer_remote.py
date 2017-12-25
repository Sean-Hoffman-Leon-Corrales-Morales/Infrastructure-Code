'''
Created on Nov 17, 2017

@author: shoffman
'''

import infrastructure.installers.core.os_executor as os_executor
import subprocess

# There is a yum module on RHEL and centos.  However, this API is not very well documented.
# At this time we are going to make the yum calls from the command line for this reason.


#===============================================================================
# Paramters:
#   logger      - This is the logger used to record log messages.
#   config      - This is the dict of configuration parameters that are obtained from 
#                 the base.yaml file.
#   ucpPassword - This is the password to be used for the UCP admin account.
#   licensePath - This is the path to the Docker EE license.
#   host        - This is the host where the UCP is to be installed.
#   password    - This is the password to be to login to remote servers via ssh.
# Description: This function will install the UCP on the manager node an configure it.
#              In addition, this installation will happen remotely from a central server. 
#===============================================================================
def installUCP(logger, config, ucpPassword, licenseFilePath, host, password):
    isExecuteSuccess = False
    
    logger.debug('+++ Beginning installation of UCP +++')
    ips = subprocess.check_output(['hostname', '--all-ip-addresses'])  
    # host = ips.split(' ')[1]
    
    src = licenseFilePath
    dest = config['bootstrap.user.path'] + licenseFilePath.split('/')[-1]
    os_executor.transferFile(logger, config, host, password, src, dest)
    
    cmd = 'docker container run --rm -it --name ucp -v /var/run/docker.sock:/var/run/docker.sock docker/ucp:2.2.4 install --host-address ' + host + ' --admin-username ' + config['docker.ucp.user'] + ' --admin-password ' + ucpPassword + ' --license "$(cat ' + dest + ')"' 
    output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
    
    if 'error' not in output.lower():
        isExecuteSuccess = True 
        logger.debug('+++ Successfully finished installation of UCP +++')

    else:
        logger.error('An error was encountered installing the UCP')
    
    return isExecuteSuccess
