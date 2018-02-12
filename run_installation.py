#!/usr/local/bin/python2.7
'''
Created on Nov 25, 2017

@author: shoffman
'''

from infrastructure.installers.core.pre_install_regimin import installPythonPackages
import argparse, sys
from _cffi_backend import string

LOGGING_CONFIG_FILE_PATH = 'configuration/logging.yaml'
config = None


def runPreInstall(inputs):
    usage = 'executor [options]'
    description = 'This module will install and configure the DevOps infrastructure, including: DockerEE, UCP. Docker Trusted Registry, as well as the  initial Jenkins container.'
    parser = argparse.ArgumentParser(description=description, usage=usage)
    
    parser.add_argument('-p', '--password', dest='osPassword', help='password for os user.')
    parser.add_argument('-dp', '--dockerPassword', dest='dockerPassword', help='password for UCP and DTR user.')
    parser.add_argument('-l', '--licensePath', dest='licenseFilePath', help='path to DockerEE license.')
    parser.add_argument('-d', '--dtrs', dest='dtrCount', type=int, help='the number of DTR instances to install.')
    parser.add_argument('-wd', '--workersDev', dest='workerDevCount', type=int, help='the number of worker nodes to install.')
    parser.add_argument('-wq', '--workersQa', dest='workerQaCount', type=int, help='the number of worker nodes to install.')
    parser.add_argument('-ws', '--workersStress', dest='workerStressCount', type=int, help='the number of worker nodes to install.')
    parser.add_argument('-wz', '--workersDMZ', dest='workerDmzCount', type=int, help='the number of worker nodes to install.')
    parser.add_argument('-wp', '--workersProd', dest='workerProdCount', type=int, help='the number of worker nodes to install.')    
    parser.add_argument('-md', '--managersDev', dest='managerDevCount', type=int, help='the number of manager nodes to install.')
    parser.add_argument('-mq', '--managersQa', dest='managerQaCount', type=int, help='the number of manager nodes to install.')
    parser.add_argument('-ms', '--managersStress', dest='managerStressCount', type=int, help='the number of manager nodes to install.')
    parser.add_argument('-mz', '--managersDMZ', dest='managerDmzCount', type=int, help='the number of manager nodes to install.')
    parser.add_argument('-mp', '--managersProd', dest='managerProdCount', type=int, help='the number of manager nodes to install.')
    parser.add_argument('-ldtr', '--loadDtr', dest='loadDtr', type=bool, help='Pre-load the dtr.')
    parser.add_argument('-ldtrp', '--loadDtrPath', dest='loadDtrPath', type=string, help='Path to the yml file that will pre-load the DTR.')

    args = parser.parse_args()
    if not args.osPassword: #handle a no password argument
        args.osPassword = ""
    password = args.osPassword
    dockerPassword = args.dockerPassword
    licenseFilePath = args.licenseFilePath
    dtrCount = args.dtrCount
    ##workers by zone
    workerDevCount = args.workerDevCount
    workerQaCount = args.workerQaCount
    workerStressCount = args.workerStressCount
    workerDmzCount = args.workerDmzCount
    workerProdCount = args.workerProdCount
    ##managers by zone
    managerDevCount = args.managerDevCount
    managerQaCount = args.managerQaCount
    managerStressCount = args.managerStressCount
    managerDmzCount = args.managerDmzCount
    managerProdCount = args.managerProdCount
    loadDtr = args.loadDtr
    loadDtrPath = args.loadDtrPath
    if licenseFilePath:
    # Decide if you want to keep this if here.  You can remove it if necessary.
    # if os.path.isfile(licenseFilePath):
        isExecuteSuccess = installPythonPackages()
        
        if isExecuteSuccess is True:
            sys.argv = [password, dockerPassword, licenseFilePath, dtrCount, workerDevCount, workerQaCount,
                        workerStressCount, workerDmzCount, workerProdCount, managerDevCount, managerQaCount, 
                        managerStressCount, managerDmzCount, managerProdCount, loadDtr, loadDtrPath]
            execfile('execute.py')
            
        else:
            print 'The necessary python packages were not installed.'
              
    # else:
     #     print 'Unable to find the license file at: ' + licenseFilePath
    
    else:
        print 'Check the input parameters and retry. There is a parameter(s) missing'
    
    
if __name__ == '__main__':
    parameters = sys.argv[1:]

    if parameters:
        runPreInstall(parameters)
    
    else:
        print 'Please re-run the application with the appropriate parameters.  If you need assistance on this please run:\n\t python run_installation.py -h'
