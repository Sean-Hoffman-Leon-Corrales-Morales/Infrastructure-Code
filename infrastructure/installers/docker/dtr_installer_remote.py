'''
Created on Nov 17, 2017

@author: shoffman
'''

import infrastructure.installers.core.os_executor as os_executor
import socket

# There is a yum module on RHEL and centos.  However, this API is not very well documented.
# At this time we are going to make the yum calls from the command line for this reason.


#===============================================================================
# Paramters:
#   logger      - This is the logger used to record log messages.
#   config      - This is the dict of configuration parameters that are obtained from 
#                 the base.yaml file.
#   ucpPassword - This is the password to be used for the UCP admin account.
#   ucpUrl      - This is the URL including port that the UCP is listening on.
#                 The URL would normally be something like:
#                 https://something.com
#   host        - This is the host where the UCP is to be installed.
#   password    - This is the password to be to login to remote servers via ssh.
# Description: This function will create a worker node, add it to the swarm,
#              install the DTR, and configure it. 
#===============================================================================
def installDTR(logger, config, ucpPassword, ucpUrl, dtrHost, password):
  logger.debug('Beginning installation of DTR.')  
  output = None
  #hostname = socket.gethostbyaddr(host)[0]
  cmd = 'docker container run -it --rm docker/dtr:2.4.0 install --dtr-external-url ' + dtrHost + ' --ucp-node ' + dtrHost + ' --ucp-insecure-tls --ucp-username ' + config['docker.ucp.user'] + ' --ucp-password ' + ucpPassword + ' --ucp-url ' + ucpUrl
  #Replaced the host ip with the dtr domain name
  output = os_executor.executeRemoteCommand(logger, config, cmd, dtrHost, password)
  
  if 'success' in output.lower():
    isExecuteSuccess = True
    logger.debug('+++ Successfully installed the DTR +++')
  
  else:
    logger.error('An error was encountered installing the DTR. ' + output)
  
  return isExecuteSuccess
