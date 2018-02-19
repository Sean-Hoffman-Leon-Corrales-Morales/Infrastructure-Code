'''
Created on Nov 25, 2017

@author: shoffman, LFCM
'''

import infrastructure.installers.docker.docker_image as image 
import infrastructure.utilities.config_parser as parser
import infrastructure.utilities.config_logging as setupLogging
import infrastructure.installers.docker.docker_node_installer_remote as installNode
import sys


YAML_CONFIG_FILE_PATH = 'configuration/base.yaml'
LOGGING_CONFIG_FILE_PATH = 'configuration/logging.yaml'
config = None



def loadRegistry(dtrConfig, i, logger):
    URLs = {}
    oldId = ""
    i.installDockerLocal()
    for name, fullName, userPassword, isAdmin in zip(dtrConfig["accounts.name"], 
                                                 dtrConfig["accounts.fullName"],
                                                 dtrConfig["accounts.defaultPassword"], 
                                                 dtrConfig["accounts.isAdmin"]):
           
        accounts = {'name': name, 'fullName': fullName, 
                    'isOrg':False, 'isAdmin': isAdmin, 'isActive': True,
                     'password': userPassword}
        respCode = i.addAccts(accounts)
        logger.debug("response code: " + str(respCode))
       
    for name in dtrConfig["accounts.orgs"]:
        org = {'name': name, 'fullName': name , 'isOrg':True, 'isAdmin': False, 'isActive': True}
        respCode = i.addAccts(org)
        logger.debug("response code: " + str(respCode))
       
    for org, name in zip(dtrConfig["accounts.orgs"], dtrConfig["accounts.name"]):   
        payload = {'isAdmin':True, 'isPublic': True}
        respCode = i.addAcctToOrg( name, org, payload)
        logger.debug("response code: " + str(respCode))    
       
    for org in dtrConfig["accounts.orgs"]:
        key = "repos." + org 
        for repos in dtrConfig[key]: 
            repo =  { "name": repos, "shortDescription": "Repository for " + repos, "longDescription": "This is a repo created by automation.","visibility": "public"}
            respCode = i.createRepos(repo, org)
            logger.debug("response code: " + str(respCode))
     
    for image in dtrConfig["repos.images"]:
        dtrRepo = image["org"] + '/' + image["id"]
        logger.debug("DTR Repo: " + str(dtrRepo)) 
        if( oldId == image["id"] and oldId is not ""):
            URLs.update( { image["name"] : image["value"]})
        else:
            logger.debug("about to build: " + str(URLs) + " image: " + image["id"] + " repo: " + dtrRepo)
            i.buildFromRepo(URLs, image["id"], dtrRepo, 'seed')
            logger.debug("pushing to repo: " + dtrRepo)
            i.pushToDTR(dtrRepo)
            URLs.clear()
            URLs = {image["name"] : image["value"]} 
        oldId = image["id"]

if __name__ == '__main__':
    logger = setupLogging.config_logging().getLogger(LOGGING_CONFIG_FILE_PATH)
    osPassword = sys.argv[0]
    dockerPassword = sys.argv[1]
    licenseFilePath = sys.argv[2]
    dtrCount = sys.argv[3]
    workers = {}
    managers = {}
    workers['DevCount'] = sys.argv[4]
    workers['QaCount'] = sys.argv[5]
    workers['StressCount'] = sys.argv[6]
    workers['DmzCount'] = sys.argv[7]
    workers['ProdCount'] = sys.argv[8]
    managers['DevCount'] = sys.argv[9]
    managers['QaCount'] = sys.argv[10]
    managers['StressCount'] = sys.argv[11]
    managers['DmzCount'] = sys.argv[12]
    managers['ProdCount'] = sys.argv[13]
    loadDtrPath = sys.argv[14]
    logger.debug('Password: ' + osPassword)
    logger.debug('Docker Password: ' + dockerPassword)
    logger.debug('License file path ' + licenseFilePath)
    logger.debug('DTR Count ' + str(dtrCount))
    logger.debug('Worker Total Count ' + str(workers['DevCount'] + workers['QaCount'] + workers['StressCount'] + workers['DmzCount'] + workers['ProdCount']))
    logger.debug('Manager Total Count ' + str(managers['DevCount'] + managers['QaCount'] + managers['StressCount'] + managers['DmzCount'] + managers['ProdCount']))
    config = parser.config_parser(logger, YAML_CONFIG_FILE_PATH)
    installer = installNode.installNode()
    installer.install(logger, config.getConfig(), managers, workers, dtrCount, osPassword, dockerPassword, licenseFilePath)
    if loadDtrPath:
        dtrConfigInst = parser.config_parser(logger, loadDtrPath)
        dtrConfig = dtrConfigInst.getConfig()
        i = image.docker_image(logger, config.getConfig(), dockerPassword)
        loadRegistry(dtrConfig, i, logger)





        