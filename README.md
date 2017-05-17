# CMPE-273-Raspberry-Pi-App-deployer

Requirements :
Please run "pip install backports.tempfile" command before running the client code on Pi.



App link:  https://104.196.235.71/  
SSL is enabled on nginx with self signed certificate. So we need to use https in the url.

Architecture Diagram :  

[![Architecture-Overview-Diagram.png](https://s22.postimg.org/mvz6w7cf5/Architecture-_Overview-_Diagram.png)](https://postimg.org/image/4gepysyal/)

To see list of Pi's connected double click client IP filed in UI. 
whenever client code is run on PI, it first registers itself to the rabbit server which in turen creates a queue for the client on which requests are sent. The client continuously listens on its queue for requests.
To find your public repositories click "Find"

[![Homepage.png](https://s14.postimg.org/jxms8d49t/Homepage.png)](https://postimg.org/image/kn5kkq4t9/)

Sending deploy request for the first time creates a webhook on the repository, installs packages under requirements.txt and runs the app.
Whenever commits are made to the repository, webhooks get triggered, and the packages get installed again and the app is run again.

[![webhook.png](https://s16.postimg.org/w2gnlyz9x/webhook.png)](https://postimg.org/image/x4qu4ii35/)
