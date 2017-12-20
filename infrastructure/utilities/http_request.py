'''
Created on Nov 19, 2017

@author: shoffman
'''

import requests, json


class http_request(object):
    
#===============================================================================
# Paramters:
#   logger  - This is the logger used to record log messages.
#   url     - This is the URL that requests are posted to.
#   payload - This is the payload that will be sent in the post.
#   headers - This is the list of HTTP headers that are to be added to the post.
# Description: This function will execute an HTTP POST using the specified URL
#              and payload. 
#===============================================================================
    def post(self, logger, url, payload, headers):
        logger.debug('Making POST request to: ' + url)
        logger.debug('Payload: ' + str(payload))
        response = requests.post(url, headers=headers, verify=False, data=json.dumps(payload))
      
        logger.debug('RESPONSE: ' + str(response))
        if response.status_code != 200:
            logger.error('Received HTTP ' + str(response.status_code))
            response = None
      
        else:
            logger.debug('Received HTTP ' + str(response.status_code))
            response = response.json()
            logger.debug('Response: ' + str(response))
        
        return response

# REMOVE THIS IF WE CAN
    def postO(self, logger, url, payload, headers):
        logger.debug('Making POST request to: ' + url)
        logger.debug('Payload: ' + str(json.dumps(payload)))
        s = requests.Session()

        req = requests.Request('POST', url, data=json.dumps(payload), headers=headers)
        logger.debug('HEADERS: ' + str(req.headers))
        logger.debug('DATA: ' + str(req.data))
        prepped = req.prepare()
        response = s.send(prepped, verify=False)
  
        if response.status_code != 200:
            logger.error('Received HTTP ' + str(response.status_code))
            response = None
  
        else:
            logger.debug('Received HTTP ' + str(response.status_code))
            response = response.json()
            logger.debug('RESPONSE: ' + str(response))
  
        return response

#===============================================================================
# Paramters:
#   logger  - This is the logger used to record log messages.
#   url     - This is the URL that requests are posted to.
#   headers - This is the list of HTTP headers that are to be added to the post.
# Description: This function will execute an HTTP GET to the specified URL. 
#===============================================================================
    def get(self, logger, url, headers):
        logger.debug('Making GET request to: ' + url)
  
        if headers is not None:
            response = requests.get(url, headers=headers, verify=False)
  
        logger.debug('RESPONSE: ' + str(response))
        if response.status_code != 200:
            logger.error('Received HTTP ' + str(response.status_code))
            response = None
    
        else:
            logger.debug('Received HTTP ' + str(response.status_code))
            response = response.json()
            logger.debug('Response: ' + str(response))
    
        return response
