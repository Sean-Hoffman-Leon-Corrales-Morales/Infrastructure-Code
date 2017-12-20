'''
Created on Nov 17, 2017

@author: shoffman
'''

from yaml import load


class config_parser(object):
    
#===============================================================================
# Paramters:
#   logger         - This is the logger used to record log messages.
#   configFilePath - This is the path to the config file where the configuration
#                    parameters are stored .
# Description: This function will load the information in the specified yaml 
#              config file into a dictionary. 
#===============================================================================
    def __init__(self, logger, configFilePath):
        self.config_dict = None
        logger.debug('+++ Beginning parse of configuration file +++')
        logger.debug('Opening file: ' + configFilePath)
      
        with open(configFilePath) as config:
            config_dict = load(config)
            logger.debug('Config file loaded successfully')
      
        logger.debug('Config file values:')  
        for key, value in config_dict.iteritems():
            logger.debug('- ' + key + ': ' + str(value))
          
        logger.debug('+++ Successfully finished parse of configuration file +++')
      
        return self.config_dict    
