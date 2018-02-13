'''
Created on Nov 19, 2017

@author: shoffman
'''

import requests, json, os


class http_request(object):

    def __init__(self):
        self.response = None
    
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
        if response.status_code != 200 :
            logger.error('Received HTTP ' + str(response.status_code))
            self.response = None
      
        else:
            logger.debug('Received HTTP ' + str(response.status_code))
            try:
                self.response = response.json()
            except Exception:
                logger.info('failed to decode response to JSON') 
                pass
            
            logger.debug('Response: ' + str(self.response))
        
        return self.response
    
#===============================================================================
# Paramters:
#   logger  - This is the logger used to record log messages.
#   url     - This is the URL that requests are posted to.
#   payload - This is the payload that will be sent in the post.
#   username- user name added to the post.
#   password- password to use.
# Description: This function will execute an HTTP POST using the specified URL
#              and payload using username and password. 
#===============================================================================
    def authPost (self, logger, url, payload, username, password):
        logger.debug('Making POST request to: ' + url)
        logger.debug('Payload: ' + str(payload))
        logger.debug('username: ' + username + " password: "+ password)
        r = requests.post(url, json=payload, verify=False, auth=(username,password) )
        if r.ok:
            return r
        else:
            r.raise_for_status()

#===============================================================================
# Paramters:
#   logger  - This is the logger used to record log messages.
#   url     - This is the URL that requests are posted to.
#   payload - This is the payload that will be sent in the post.
#   username- user name added to the post.
#   password- password to use.
# Description: This function will execute an HTTP PUT using the specified URL
#              and payload using username and password. 
#===============================================================================
    def authPut (self, logger, url, payload, username, password):
        logger.debug('Making Put request to: ' + url)
        logger.debug('Payload: ' + str(payload))
        r = requests.put(url, json=payload, verify=False, auth=(username,password) )
        if r.ok:
            return r
        else:
            r.raise_for_status()

            
#===============================================================================
# Parameters:
#   logger       - This is the logger used to record log messages.
#   url          - This is the URL the file is being downloaded from.
#   saveLocation - This is location the downloaded file is being saved to.
# Description: This function will download a file from a specified URL and save
#              it to the specified location. 
#===============================================================================
    def downloadFile(self, logger, url, downloadLocation):
        logger.debug('Downloading file from ' + url)
        response = requests.get(url, stream=True, verify=False)
  
        with open(downloadLocation, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024): 
                if chunk: 
                    f.write(chunk)

        if os.path.isfile(downloadLocation) is True:
            isExecuteSuccess = True
    
        return isExecuteSuccess

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
            self.response = None
    
        else:
            logger.debug('Received HTTP ' + str(response.status_code))
            self.response = response.json()
            logger.debug('Response: ' + str(response))
    
        return self.response
