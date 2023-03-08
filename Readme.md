# Tools to parse NetworkDump files and feed it to Nautbot.
## Bring up nautobot containers

        docker-compose up

This brings up containerized nautobot envireonment. Login with username admin and pasword admin to http://localhost:8080 is possible. Do not use this settings in production environment. Modify 'local.env' for your need.
For details about nautobot see https://docs.nautobot.com/projects/core/en/stable/. Modify api_login.py for your nautobot installation.

## Install required Python Libraries

        pip install -r requirement.txt

## Initialize Nautopot 

        python3 init_nautobot.py

This initialize nautobot with default site, and rfc1918 prefixes etc.


## Parse and feed Nautobot
* Copy Networkdump.zip file into Folder
* run 

        python feed_nautobot.py

* This unzipps Networkdump.zip, parses it and feed Nautobot
* This takes a while

After parsing you should see Devices, VLANs, IP-Prefies and IP-Addresses with it's MAC address

