'''
Created on Feb 6, 2018

@author: lcorr
'''
import infrastructure.installers.core.os_executor as os_executor
import infrastructure.installers.docker.docker_node_installer_remote as installer_remote


class MyClass(object):
    '''
    classdocs
    '''


    def __init__(self, logger, config, password):
        '''
        Constructor
        @param logger - 
        @param config - 
        @param password -
        '''
        self.logger = logger
        self.config = config
        self.password = password
    
    def loadCLI(self):
        nodeInstaller = installer_remote.installNode()
        auth = nodeInstaller.getAuthToken(self.logger, self.config, "https://ucp.aws.gce.org", self.password )       
        filepath = self.config["download.location"] + "/cli-bundle.zip"
        header = {"Authorization": "Bearer " + auth}
        success = os_executor.downloadFileHTTP(self.logger, filepath, "https://ucp.aws.gce.org/api/clientbundle", header)
        if success:     
            cmd = 'unzip ' + filepath + " -d " + self.config["download.location"] +  " && cd " +  self.config["download.location"]
            output = os_executor.executeCmd(self.logger, cmd)
            
            if 'error' not in output.lower():
                raise ValueError("Failed to add docker ee repo localy.")
            
            cmd =  "eval \"$(<env.sh)\""
            output = os_executor.executeCmd(self.logger, cmd)
            
            if 'error' not in output.lower():
                raise ValueError("Failed to add docker ee repo localy.") 
            
    def deploy(self, pathToComposeFile):
        