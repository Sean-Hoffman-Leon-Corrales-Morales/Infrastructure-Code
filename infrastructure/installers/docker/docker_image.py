'''
Created on Jan 25, 2018

@author: Leon
'''
import socket
import infrastructure.installers.core.os_executor as os_executor
import infrastructure.utilities.http_request as http_request
import infrastructure.installers.docker.docker_node_installer_remote as installer_remote
from asn1crypto._ffi import null
from pyasn1.type.univ import Null

 
class docker_image(object):
    '''
    classdocs
    '''

    def __init__(self, logger, config, dockerPassword, osPassword = Null):
        '''
        Constructor
        
        @param logger - 
        @param config - 
        @param password -
        '''
        self.logger = logger
        self.config = config
        self.dockerPassword = dockerPassword
        self.osPassword = osPassword
        
        '''
        @summary: description: 
            downloades the cli-bundle and installs docker-ee but does not add as node to the UCP
            this is for remote CLI. 
        '''
    def installDockerLocal(self):
        self.logger.debug("+++installing Docker localy+++")
        cmd = "sudo yum remove docker docker-common docker-selinux docker-engine-selinux ocker-engine docker-ce docker-ee && rm -rf /var/lib/docker"
        #try and remove old versions of docker.
        os_executor.executeCmd(self.logger, cmd)
        
        cmd = "sh -c 'echo \"" + self.config['docker.ee.url'] + "/centos\" > /etc/yum/vars/dockerurl'"
        output = os_executor.executeCmd(self.logger, cmd)
        
        if 'error' in output.lower():
            raise ValueError("Failed to add docker ee repo localy.")
        
        self.logger.debug('Successfully added Docker URL to yum URLs')
        cmd = 'yum install -y yum-utils device-mapper-persistent-data lvm2 unzip'
        output = os_executor.executeCmd(self.logger, cmd)
        
        if 'error' in output.lower():
            raise ValueError("Failed to add docker ee repo localy.")
        
        self.logger.debug('Successfully installed yum-utils device-mapper-persistent-data lvm2')
        
        cmd = 'yum-config-manager --add-repo "' + self.config['docker.ee.url'] + '/centos/docker-ee.repo"'
        output = os_executor.executeCmd(self.logger, cmd)
        
        if 'error' in output.lower():
            raise ValueError("Failed to add docker ee repo localy.")
        
        self.logger.debug('Successfully added Docker repo.')        
        
        cmd = 'yum -y install docker-ee'
        output = os_executor.executeCmd(self.logger, cmd)
        
        if 'error' in output.lower(): 
            raise ValueError('Unable to install docker.')
        
        self.logger.debug('Successfully installed Docker EE')
        
        cmd = 'service docker start'
        output = os_executor.executeCmd(self.logger, cmd)      
        
        if 'error' in output.lower(): 
            raise ValueError('Unable to start docker.')
               
    def buildFromRepo(self, URLs, folder, repo, tag):
        buildDir = self.config["download.location"] + '/' + folder
        cmd = 'mkdir ' + buildDir
        output = os_executor.executeCmd(self.logger, cmd)

        for name, url in URLs.items():
            cmd = 'curl --insecure --header \'PRIVATE-TOKEN:' + self.config["repo.token"] + '\' -o ' + buildDir + '/' + name + ' ' + url
            self.logger.debug("downloading asset with: " + cmd)
            output = os_executor.executeCmd(self.logger, cmd)
        
        cmd = 'docker build -f ' + buildDir + '/Dockerfile -t ' + self.config["aws.dockerReg"] + '/' + repo + ':' + tag + ' .'
        self.logger.debug("building docker file with: " + cmd)
        output = os_executor.executeCmd(self.logger, cmd)
        return output
        
    def pushToDTR(self, imageName ):
        self.logger.debug("+++Starting a DTR push for " + imageName)
        ir = installer_remote.installNode()
        host = self.getIp()
        dtrHost = self.config["aws.dockerReg"]
        dtrIp = socket.gethostbyname(dtrHost)
        self.logger.debug("host IP: " + host + " dtrIP: " + dtrIp + " dtrHost: " + dtrHost)
        ir.registerWithDTR(self.logger, self.config, host, dtrHost, dtrIp, self.dockerPassword, self.osPassword, True)
        cmd = "docker login " + dtrHost + " -u " + self.config["docker.ucp.user"] + " -p " + self.dockerPassword
        self.logger.debug("running.." + cmd)
        output = os_executor.executeCmd(self.logger, cmd)
        self.logger.debug("got back : " + str(output))
        cmd = "docker push " + dtrHost + '/' + imageName
        output = os_executor.executeCmd(self.logger, cmd)

    def addAccts(self, accounts ):
        '''
        Use the API to create accts
        ccheck for InfraUser: if not there then create it.
        '''
        req = http_request.http_request()
        url = "https://" + self.config["aws.dockerReg"] + '/enzi/v0/accounts'
        payload = accounts
        return req.authPost(self.logger, url, payload, self.config['docker.ucp.user'], self.dockerPassword)

    def addAcctToOrg(self, user, org, payload):
        req = http_request.http_request()
        url = "https://" + self.config["aws.dockerReg"] + '/enzi/v0/accounts/' + org + '/members/' + user
        return req.authPut(self.logger, url, payload, self.config['docker.ucp.user'], self.dockerPassword)       
    
    def createRepos(self, repo, org):
        req = http_request.http_request()
        url = "https://" + self.config["aws.dockerReg"] + '/api/v0/repositories/' + org
        payload = repo
        return req.authPost(self.logger, url, payload, self.config['docker.ucp.user'], self.dockerPassword)        

    def getIp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('8.8.8.8', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP
        