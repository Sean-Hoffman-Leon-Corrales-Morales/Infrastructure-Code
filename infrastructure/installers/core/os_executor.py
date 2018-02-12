'''
Created on Nov 17, 2017

@author: shoffman
'''

from fabric.api import local, run, env, put
import subprocess, requests, os

MAX_RETRIES = 3
retries = 0

# Must test getting of the output of the command.  If it works,
# then we will return the output.


#==============================================================================
# Paramters:
#   logger   - This is the logger used to record log messages.
#   filePath - This is the path to the file that is being updated. 
#   content  - This is the content that we are updating in the file.
# Description: This function will update the content in the specified file.  
#==============================================================================
def updateFile(logger, filePath, content):
    logger.debug('Updating file ' + filePath)
    file = open(filePath, 'w') 
    file.write(content)
    file.close()
    logger.debug('Finished writing to ' + filePath) 


#==============================================================================
# Paramters:
#   logger   - This is the logger used to record log messages.
#   filePath - This is the path to the file that is being updated. 
# Description: This function will read the content of the specified file.  
#==============================================================================
def readFile(logger, filePath):
    logger.debug('Reading file ' + filePath)
    
    with open (filePath, "r") as file:
        content = file.readlines()
      
    logger.debug('Finished reading ' + filePath) 
      
    return content



#==============================================================================
# Paramters:
#   logger   - This is the logger used to record log messages.
#   filePath - where to save the file
#   url      - This is the server where we're downloading from .
#   header   - header data to pass along.
#
# Description: This function download a file, save it and return true/false.
#              
#==============================================================================
def downloadFileHTTP(logger, filePath, url, header):
    r = requests.get(url,verify=False, headers=header)
    with open( filePath, "wb") as code:
        code.write(r.content)
        code.close()
    if os.path.isfile(filePath) and r.status_code == 200:
        return True
    else: 
        return False
    
    
#==============================================================================
# Paramters:
#   logger   - This is the logger used to record log messages.
#   config   - This is the dict of configuration parameters that are obtained 
#              from the base.yaml file.
#   host     - This is the host being logged into to execute the command.
#   password - This is the password to be to login to remote servers via ssh.
#   cmd      - This is the shell command to be executed on the remote host.
# Description: This function will ssh to the specified host, then execute the
#              specified command.  
#==============================================================================
def executeRemoteCommand(logger, config, cmd, host, password):
    env.host_string = host
    env.user = config['docker.user']
    if password: 
        env.password = password
        logger.debug("Password is set")
    elif not password:
        env.key_filename = [str(config['aws.pemFile'])]
        logger.debug("Using aws pem file" + config['aws.pemFile'])
    cmd = 'sudo ' + cmd
    
    logger.debug('Host: ' + host)
    logger.debug('Executing command: ' + cmd)
    output = run(cmd)
    
    logger.debug('Output: ' + output)
    
    return output

  
#==============================================================================
# Paramters:
#   logger   - This is the logger used to record log messages.
#   config   - This is the dict of configuration parameters that are obtained 
#              from the base.yaml file.
#   host     - This is the host being logged into to execute the command.
#   password - This is the password to be to login to remote servers via ssh.
#   src      - This is the path to the file that is being transferred.
#   dest     - This is the path to the final destination.
# Description: This function will scp the file to the remote machine.  
#==============================================================================
def transferFile(logger, config, host, password, src, dest):
    env.host_string = host
    env.user = config['docker.user']
    if password: 
        env.password = password
    elif not password:
        env.key_filename = config['aws.pemFile']
        
    logger.debug('Host: ' + host)
    logger.debug('Copying: ' + src + ' | To: ' + dest)
    put(src, dest)


#==============================================================================
# Paramters:
#   logger   - This is the logger used to record log messages.
#   config   - This is the dict of configuration parameters that are obtained 
#              from the base.yaml file.
#   ports    - This is a list of ports to be opened in the firewall.
#   host     - This is the host being logged into to execute the command.
#   password - This is the password to be to login to remote servers via ssh.
# Description: This function will permanently open the supplied ports in the 
#              firewall, then check to see if all ports were opened.  If they
#              are not all opened, then it will retry a max of 3 times before
#              aborting the installation.
#==============================================================================
def openFirewallPorts(logger, config, ports, host, password):
  isExecuteSuccess = True
  
  for port in ports:  
    logger.debug('Attempting to open port ' + port)
    cmd = 'firewall-cmd --zone=public --add-port=' + port + '/tcp --permanent'
    output = executeRemoteCommand(logger, config, cmd, host, password)
    
    if 'success' in output.lower():
      logger.debug('Successfully opened port ' + port)
     
    else:
      logger.error('An error was encountered while opening port ' + port)  
  
  logger.debug('Reloading firewall rules...')
  cmd = 'firewall-cmd --reload'
  output = executeRemoteCommand(logger, config, cmd, host, password)
    
  if 'success' in output.lower():
    logger.debug('Successfully reloaded firewall rules')
  
  else:
    logger.error('An error was encountered reloading the firewall rules.')  
  
  logger.debug('Checking open ports...')
  cmd = 'firewall-cmd --list-all'
  output = executeRemoteCommand(logger, config, cmd, host, password)

  for port in ports:
    if port not in output:
        isExecuteSuccess = False
        # Maybe we retry here?  Only 3 times though?
        logger.error('Port ' + port + 'not opened')
  
  if isExecuteSuccess is False and retries < 4:
      retries += 1
      openFirewallPorts(logger, config, ports, host, password)
  
  else:
      return isExecuteSuccess


#==============================================================================
# Paramters:
#   logger   - This is the logger used to record log messages.
#   cmd      - This is the shell command to be executed on the remote host.
# Description: This function  execute the specified command.  
#==============================================================================
def executeCmd(logger, cmd):
  logger.debug('Executing command: ' + cmd)
  p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
  # p.wait()
  
  output = ''
  
  for line in iter(p.stdout.readline, ''):
    output += line
    logger.debug(output)
  
  return output
