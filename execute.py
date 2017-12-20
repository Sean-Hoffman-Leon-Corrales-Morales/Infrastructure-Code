'''
Created on Nov 25, 2017

@author: shoffman, LFCM
'''


import infrastructure.utilities.config_parser as parser
import infrastructure.utilities.config_logging as setupLogging
import infrastructure.installers.docker.docker_node_installer_remote as installNode
import sys
from distutils.core import setup


# YAML_CONFIG_FILE_PATH = 'C:/Users/shoffman/software/eclipse/workspace/BaseInstaller/configuration/base.yaml'
YAML_CONFIG_FILE_PATH = 'configuration/base.yaml'
# LOGGING_CONFIG_FILE_PATH = 'C:/Users/shoffman/software/eclipse/workspace/BaseInstaller/configuration/logging.yaml'
LOGGING_CONFIG_FILE_PATH = 'configuration/logging.yaml'
config = None

if __name__ == '__main__':
    logger = setupLogging.config_logging().getLogger(LOGGING_CONFIG_FILE_PATH)
    password = sys.argv[0]
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
    
    logger.debug('Password: ' + password)
    logger.debug('Docker Password: ' + dockerPassword)
    logger.debug('License file path ' + licenseFilePath)
    logger.debug('DTR Count ' + str(dtrCount))
    logger.debug('Worker Total Count ' + str(workers['DevCount'] + workers['QaCount'] + workers['StressCount'] + workers['DmzCount'] + workers['ProdCount']))
    logger.debug('Manager Total Count ' + str(managers['DevCount'] + managers['QaCount'] + managers['StressCount'] + managers['DmzCount'] + managers['ProdCount']))
    config = parser.config_parser(logger, YAML_CONFIG_FILE_PATH)
    installNode.installNode(logger, config, managers, workers, dtrCount, password, dockerPassword, licenseFilePath)
