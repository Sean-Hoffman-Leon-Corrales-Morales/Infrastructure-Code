'''
Created on Nov 22, 2017

@author: shoffman, LFCM
'''

import subprocess

#==============================================================================
# Paramters:
#   cmd      - This is the shell command to be executed on the remote host.
# Description: This function  execute the specified command.
# Important:   This function is replicated in os_executor.py and that is the
#              one used in all other modules.  This one is here, because
#              there are other functions in that module whose packages are
#              installed here.  
#
#==============================================================================
def executeCmd(cmd):
  print 'Executing command: ' + cmd
  p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
  output = ''
  
  for line in iter(p.stdout.readline, ''):
    print line
    output += line

  return output


#==============================================================================
# Paramters:
#   logger   - This is the logger used to record log messages.
#   config   - This is the dict of configuration parameters that are obtained 
#              from the base.yaml file.
# Description: This function will install the python packages necessary to run
#              this application.  5383
#==============================================================================
def installPythonPackages():
  isExecuteSuccess = False
  
  cmd = 'yum -y update'
  output = executeCmd(cmd)
  
  cmd = 'yum -y --enablerepo=extras install epel-release'
  output = executeCmd(cmd)
  
  if 'error' not in output.lower():
    cmd = 'yum -y install python-pip'
    output = executeCmd(cmd)
  
  else:
    print 'An error was encountered installing pip'
  
  if 'error' not in output.lower():
    print 'Successfully installed pip.'
    upgrade = pipInstaller('sudo pip install --upgrade pip')
    pyyaml = pipInstaller('pip install pyyaml')
    fabric = pipInstaller('sudo pip install fabric')
    requests = pipInstaller('pip install requests')
    boto3 = pipInstaller('sudo pip install boto3')
    pydoc = pipInstaller('pydoc modules')
    ipaddress = pipInstaller('sudo pip install ipaddress')

  if upgrade and pyyaml and fabric and requests and boto3 and pydoc:
    print 'Successfully upgraded pip, installed pyyaml, fabric, requests, boto3 and pydoc.'
    isExecuteSuccess = True
          
  else:
    print 'The modules pyyaml and fabric were not successfully installed.'
    isExecuteSuccess = False
    
  return isExecuteSuccess  


#==============================================================================
# Paramters:
#   cmd   - pip command string to execute
#
# Description: This function will execute pip commands and outputs a 
#              success/fail strings and returns an accompanying bool.  
#
# Returns: Bool 
#==============================================================================
def pipInstaller(cmd):
    output = executeCmd(cmd)
    if 'error' not in output.lower():
        print 'successfully executed: ' + cmd + '.'
        return True
    else:
        print 'Failed to execute: ' + cmd + '.'
        return False
