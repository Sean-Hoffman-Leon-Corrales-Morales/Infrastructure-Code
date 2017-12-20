'''
Created on Nov 17, 2017

@author: shoffman, LFCM
'''

import logging.config, yaml


class config_logging(object):
    def __init__(self):
        self.logger = None
#===============================================================================
# Paramters:
#   configLoggingFilePath - This is the path to the logging configuration file.
#                           This file is in yaml format.
# Description: This object will configuration logging for the entire
#              application from the specified yaml file. 
#===============================================================================    
    def getLogger(self, configLoggingFilePath):
        print configLoggingFilePath
        logging.config.dictConfig(yaml.load(open(configLoggingFilePath)))
        self.logger = logging.getLogger('base_installer')
        return self.logger
