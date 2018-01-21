'''
Created on Nov 28, 2017

@author: shoffman, LFCM
'''

import socket
import ipaddress
from infrastructure.utilities.http_request import http_request
from infrastructure.installers.aws.provisioner import provisioner
from infrastructure.installers.docker.dockeree_installer_remote import executeDockerInstall
from infrastructure.installers.docker.ucp_installer_remote import installUCP
from infrastructure.installers.docker.dtr_installer_remote import installDTR
import infrastructure.installers.core.os_executor as os_executor
from pip._vendor.pyparsing import empty


class installNode(object):
#===============================================================================
# Paramters:
#   logger        - This is the logger used to record log messages.
#   config        - This is the dict of configuration parameters that are obtained from 
#                   the base.yaml file.
#   managerCount  - This is the number of Swarm manager nodes to install.
#   workerCount   - This is the number of Swarm worker nodes to install.
#   dtrCount      - This is the number of DTR's to install.
#   password      - This is the password to be to login to remote servers via ssh.
#   ucpPassword   - This is the password to be used for the UCP admin account.
#   licensePath   - This is the path to the Docker EE license.
# Description: This function will coordinate the installation of the complete Docker 
#              installation. 
#===============================================================================
    def __init__(self, logger, config, managers, workers, dtrCount, password, ucpPassword, licenseFilePath):
        self.requester = http_request()
        managerCounter = 0 
        workerCounter = 0  
        dtrCounter = 0
        awsFlag = True #<===== HARD CODED CHANGE FOR ON-SITE. Need to decide how to handle it in the above classes 
        ucpInstalled = False
        ucpUrl = None
        dtrHost = None
        dtrIp = None
        logger.debug('logger works in installNode Class')
        aws = provisioner(config, logger)
        aws.provisionManagers(managers['QaCount'], managers['DevCount'], managers['StressCount'],
                                           managers['DmzCount'], managers['ProdCount'])
        managerHosts = aws.getManagers()
        managerCount = len(managerHosts)
        logger.debug('building ' + str(managerCount) + ' Docker managers')
        for host in managerHosts:
            logger.debug('Connecting to host ' + host)
            logger.debug('Building ' + str(managerCount) + ' manager nodes')           
            isExecuteSuccess = executeDockerInstall( logger, config, host, password)

            if managerCounter <= managerCount: 
            
                if isExecuteSuccess is True and ucpInstalled is False:
                    logger.debug('Successfully installed Docker EE')
                    if awsFlag is True:
                        logger.debug("sending to Route53: ucp.*domain -> " + str(host))
                        aws.addRoute53("docker.ucp", str(host))
                    isExecuteSuccess = installUCP(logger, config, ucpPassword, licenseFilePath, host, password)
    
                elif isExecuteSuccess is False:
                    logger.error('An error was encountered installing Docker EE')
    
                elif ucpInstalled is True:
                    isExecuteSuccess = addManagerNode(self, logger, config, ucpUrl, ucpPassword, password, host)  # <-- ucp url
    
                if isExecuteSuccess is True and ucpInstalled is False:
                    ucpUrl = 'https://' + host
                    ucpInstalled = True
            
                managerCounter += 1
        
        workerHosts = aws.provisionWorkers(workers['QaCount'], workers['DevCount'], workers['StressCount'],
                                       workers['DmzCount'], workers['ProdCount'])
        workerCount = len(workerHosts)
        logger.debug('building ' + str(workerCount) + ' Docker managers')
        for host in workerHosts: 
            logger.debug('Connecting to host ' + host + ' counter is at: ' + str(workerCounter))
            isExecuteSuccess = executeDockerInstall(logger, config, host, password)
            
            if workerCounter < workerCount:
                if isExecuteSuccess is True:
                    logger.debug('logger:' + str(logger) + ' config: ' + str(config) + ' ucpUrl' + str(ucpUrl) + ' ucpPassword ' + ucpPassword + ' host ' + host)
                    isExecuteSuccess = addWorkerNode(self, logger, config, ucpUrl, ucpPassword, password, host)  # <-- ucp url
                
                else:
                    logger.error('An error was encountered installing Docker EE')
                
                if isExecuteSuccess is True:
                    logger.debug('Successfully added worker node to Swarm')
                  
                if dtrCounter < dtrCount:
                    if awsFlag is True:
                        logger.debug("sending to Route53: dtr.*domain -> " + str(host))
                        dtrHost = aws.addRoute53("dtr", str(host))
                        dtrIp = host
                    if dtrHost is empty: 
                        dtrHost = host
                        dtrIp = host
                    isExecuteSuccess = installDTR(logger, config, ucpPassword, ucpUrl, host, dtrHost, password)
              
                if isExecuteSuccess is True and dtrCounter < dtrCount:
                    dtrCounter += 1
              
                workerCounter += 1

                if workerCounter > dtrCounter:
                    isExecuteSuccess = registerWithDTR(self, logger, config, host, dtrHost, dtrIp, ucpPassword, password)
      
                if isExecuteSuccess is True:
                    logger.debug('Successfully installed the worker node')
        
                else:
                    logger.error('An error was encountered installing the worker node')
                    
#===============================================================================
# Paramters:
#   logger      - This is the logger used to record log messages.
#   config      - This is the dict of configuration parameters that are obtained from 
#                 the base.yaml file.
#   ucpUrl      - This is the URL including port that the UCP is listening on.
#                 The URL would normally be something like:
#                 https://something.com
#   ucpPassword - This is the password to be used for the UCP admin account.
# Description: This function will login and obtain an authorization token to be used
#              in subsequent REST calls. 
#===============================================================================
def getAuthToken(self, logger, config, ucpUrl, ucpPassword):
    logger.debug('+++ Getting Auth Token +++')
    authToken = None
    requestUrl = ucpUrl + '/auth/login'
    headers = {'Content-Type': 'application/json'}
    payload = {'password': ucpPassword, 'username': config['docker.ucp.user']}
    response = self.requester.post(logger, requestUrl, payload, headers)
    
    if response != None:
        authToken = response['auth_token']  
        logger.debug('Successfully retrieved auth token.')   
      
    else:
        logger.error('An error was encountered getting auth token. ' + str(response))   
    return authToken


#===============================================================================
# Paramters:
#   logger        - This is the logger used to record log messages.
#   config        - This is the dict of configuration parameters that are obtained from 
#                   the base.yaml file.
#   host          - This is the host of the generic worker node.
#   dtrHost       - This is the host of the dtr node.
#   password      - This is the password to be to login to remote servers via ssh.
# Description: This function will register the worker node with the DTR.  It carries
#              out the following four steps:
#                1. Download the certs from the DTR.
#                2. Transfers the certs to the worker node being installed.
#                3. Updates the ca trust.
#                4. Restarts the Docker service.
#===============================================================================
def registerWithDTR(self, logger, config, host, dtrHost, dtrIp, ucpPassword, password):
    logger.debug('+++ Beginning registration with DTR +++')
    # this was dtrHost
    hostname = socket.gethostbyaddr(dtrIp)[0]
    
    # I know this sucks.  But I will remove the additional parameters once we test this and it working.
    if dtrHost is dtrIp:
      dtrHost = hostname
    
    url = 'https://' + dtrHost + '/ca'
    certName = dtrHost + '.crt'
    downloadLocation = config['download.location'] + '/' + certName
    isExecuteSuccess = self.requester.downloadFile(logger, url, downloadLocation)
    output = ''
    
    if isExecuteSuccess is True:
        logger.debug('Transferring certificate to ' + host)
        dest = config['download.location'] + '/' + certName
        #have to do this because we can't put into the final dir
        os_executor.executeRemoteCommand(logger, config, "mkdir  -p " + config['docker.dtr.cert.location'] , host, password)
        output = os_executor.transferFile(logger, config, host, password, downloadLocation, dest)
        saveLocation = config['docker.dtr.cert.location'] + '/' + certName  
        cmd = 'mv ' + dest + ' ' + saveLocation
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
    else:
        logger.error('An error was encountered downloading the DTR certificate.')
  
    if 'error' not in output.lower():
        logger.debug('+++ Successfully transferred certificate to ' + host + ' +++')
        logger.debug('Beginning update of ca trust on ' + host)
        cmd = 'update-ca-trust'
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
    
    else:
        logger.error('An error was encountered transferring the DTR certificate to ' + host)   
  
    if 'error' not in output.lower():
        logger.debug('+++ Successfully updated the ca trust on the worker node +++')
        logger.debug('Beginning restart of the Docker service on ' + host)
        cmd = 'service docker restart'
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
    
    else:
        logger.error('An error was encountered updating the ca trust on ' + host) 
  
    if 'error' not in output.lower():
        logger.debug('Successfully restarted the Docker service on ' + host)
        cmd = 'docker login -u admin -p' + ucpPassword + ' ' + dtrHost
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
    
    else:
        logger.error('An error was encountered restarting the Docker service on ' + host)
   
    if 'error' not in output.lower():
        isExecuteSuccess = True
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)
    
    else:
        logger.error('An error was encountered logging into the DTR on ' + dtrHost)
    
    return isExecuteSuccess
    

#===============================================================================
# Paramters:
#   logger    - This is the logger used to record log messages.
#   ucpUrl    - This is the URL including port that the UCP is listening on.
#               The URL would normally be something like:
#               https://something.com
#   authToken - This is the token that authorizes the completion of REST calls to UCP.
# Description: This function will get a list of the manager nodes. 
#===============================================================================
def getManagerNodeList(self, logger, ucpUrl, authToken):
    logger.debug('+++ Getting Manager List +++')
    headers = {'Authorization': 'Bearer ' + authToken, 'Content-Type': 'application/json'}
    managers = []
    requestUrl = ucpUrl + '/nodes'
    response = self.requester.get(logger, requestUrl, headers)
    if response != None:
        logger.debug("response: " + str(response) + " of type: " + str(type(response)))
        for manager in response:
            if 'ManagerStatus' in manager.keys():
                managerIp = manager['ManagerStatus']['Addr']
                managers.append(managerIp) 
            
            else:
                logger.error('An error was encountered in getting the manager list. ' + str(response))   
            
    return managers


#===============================================================================
# Paramters:
#   logger        - This is the logger used to record log messages.
#   config        - This is the dict of configuration parameters that are obtained from 
#                   the base.yaml file.
#   ucpUrl        - This is the URL including port that the UCP is listening on.
#                   The URL would normally be something like:
#                   https://something.com
#   ucpPassword   - This is the password to be used for the UCP admin account.
#   password      - This is the password to be to login to remote servers via ssh.
#   host          - This is the host where the UCP is to be installed.
# Description: This function will create a new worker node and add it to the Swarm. 
#===============================================================================
def addWorkerNode(self, logger, config, ucpUrl, ucpPassword, password, host):
    logger.debug('+++ Beginning creation of worker node +++')
    authToken = getAuthToken(self, logger, config, ucpUrl, ucpPassword)
    headers = {'Authorization': 'Bearer ' + authToken, 'Content-Type': 'application/json'}
    managers = getManagerNodeList(self, logger, ucpUrl, authToken)
    
    swarmToken = None
    isExecuteSuccess = False
    requestUrl = ucpUrl + '/swarm'
    output = None
    response = self.requester.get(logger, requestUrl, headers)

    if response != None:
        swarmToken = response['JoinTokens']['Worker']
        logger.debug('Using worker swarm token: ' + swarmToken)
        cmd = 'docker swarm join --token ' + swarmToken + ' ' + managers[0]
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)

    else:
        logger.error('An error was encountered getting swarm token. ' + str(response))   

    if 'error' not in output.lower():
        isExecuteSuccess = True
        logger.debug('+++ Successfully added a worker node +++')
    else:
        logger.error('An error was encountered adding a worker node')
    
    return isExecuteSuccess


#===============================================================================
# Paramters:
#   logger        - This is the logger used to record log messages.
#   config        - This is the dict of configuration parameters that are obtained from 
#                   the base.yaml file.
#   ucpUrl        - This is the URL including port that the UCP is listening on.
#                   The URL would normally be something like:
#                   https://something.com
#   ucpPassword   - This is the password to be used for the UCP admin account.
#   password      - This is the password to be to login to remote servers via ssh.
#   host          - This is the host where the UCP is to be installed.
# Description: This function will create a new worker node and add it to the Swarm. 
#===============================================================================
def addManagerNode(self, logger, config, ucpUrl, ucpPassword, password, host):
    logger.debug('+++ Beginning creation of manager node +++')
    authToken = getAuthToken(self, logger, config, ucpUrl, ucpPassword)
    headers = {'Authorization': 'Bearer ' + authToken}
    managers = getManagerNodeList(self, logger, ucpUrl, authToken)
    
    swarmToken = None
    isExecuteSuccess = False
    requestUrl = ucpUrl + '/swarm'
    output = None
    
    response = self.requester.get(logger, requestUrl, headers)
    
    if response != None:
        swarmToken = response['JoinTokens']['Manager']
        logger.debug('Using worker swarm token: ' + swarmToken)
        cmd = 'docker swarm join --token ' + swarmToken + ' ' + managers[0]
        output = os_executor.executeRemoteCommand(logger, config, cmd, host, password)

    else:
        logger.error('An error was encountered getting swarm token. ' + str(response))   

    if 'error' not in output.lower():
        isExecuteSuccess = False
        logger.debug('+++ Successfully added a manager node +++')

    else:
        logger.error('An error was encountered adding a manager node')  
        
    return isExecuteSuccess
