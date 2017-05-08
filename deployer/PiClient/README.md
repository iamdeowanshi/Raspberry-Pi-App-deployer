# Raspberry Pi Deployer Client

## Required:  
1. Add file /etc/deployer-client/deployer.conf with contents -  
   [DEFAULT]  
   ip = 192.168.0.131  

   [log]  
   file = /var/log/cmpe273/client.log  

   [rabbit]  
   host = 104.196.235.71  
   username = \*\*ask Amita\*\*  
   password = \*\*ask Amita\*\*  
   port = 5672  

2. mkdir -p /var/log/cmpe273  

## How to run the code:  
   a. Create a virtual env - virtualenv <Name>  
   b. Activate virtual env - source <Name>/bin/activate  
   c. Navigate to client code - <Repo>/deployer/PiClient  
   c. Install - pip install -r requirements.txt && pip install -e .  
   d. Run - python client/client_service.py  

## Logs  
   Logs will be generated in /var/log/cmpe273/client.log  


