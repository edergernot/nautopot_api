'''
Used to create default RFC1918 Prefix and default Site as well as default RIR 
'''

import pynautobot
import api_login

HOST=api_login.HOST
PORT=api_login.PORT
TOKEN=api_login.TOKEN
nautobot = pynautobot.api(url=f"http://{HOST}:{PORT}", token=TOKEN)

# Create AutoSite 
my_site='AutoSite'
site=nautobot.dcim.sites.get(slug=my_site.lower())
if site == None:
    site = nautobot.dcim.sites.create(name=my_site.capitalize(), slug=my_site.lower(), description="Created via API", status = "Active")
    print(f'Site {my_site} created')

# Create Device Role 
my_device_role = "Network"
device_role=nautobot.dcim.device_roles.get(slug=my_device_role.lower())
print(device_role)
if device_role == None:
    device_role = nautobot.dcim.device_roles.create(name=my_device_role.capitalize(), slug=my_device_role.lower(), color= "ff0000",description="Created via API")
    print(f'Device Role {my_device_role} created')

# Create RFC1918 RIR
rirs = ['RFC1918', 'RIPE', 'RFC6598']
for rir in rirs:
    checkrir = nautobot.ipam.rirs.get(slug=rir.lower())
    if checkrir == None:
        nautobot.ipam.rirs.create(name=rir.upper(),slup=rir.lower())
        rir_id=nautobot.ipam.rirs.get(slug=rir.lower())
        print (f'RIR {rir} with ID: {rir_id.id} created')

# Create RFC1918 Aggregates
aggregates = ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16']
rir_id = nautobot.ipam.rirs.get(slug='rfc1918')
for agg in aggregates:
    check_agg = nautobot.ipam.aggregates.get(prefix=agg)
    if check_agg == None:
        nautobot.ipam.aggregates.create(prefix=agg, rir=rir_id.id)
        agg_id = nautobot.ipam.aggregates.get(prefix=agg)
        print (f'Aggregate {agg} with ID: {agg_id.id} created')

# Create RFCRFC6598 Aggregate
aggregates = ['100.64.0.0/10']
rir_id = nautobot.ipam.rirs.get(slug='rfc6598')
for agg in aggregates:
    check_agg = nautobot.ipam.aggregates.get(prefix=agg)
    if check_agg == None:
        agg_id = nautobot.ipam.aggregates.get(prefix=agg)
        nautobot.ipam.aggregates.create(prefix=agg, rir=rir_id.id, description='Shared Address Space')
        agg_id = nautobot.ipam.aggregates.get(prefix=agg)
        print (f'Aggregate {agg} with ID: {agg_id.id} created')

# Create Prefices
prefixes =  ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '100.64.0.0/10']
for prefix in prefixes:
    check_pre = nautobot.ipam.prefixes.get(prefix=prefix)
    if check_pre == None:
        nautobot.ipam.prefixes.create(prefix=prefix, status= 'Container')
        prefix_id = nautobot.ipam.prefixes.get(prefix=prefix)
        print (f'Prefix {prefix} with ID: {prefix_id.id} generated')

# Create Tags
tags = ['STP-Blocking', 'CDP-Neighbor', 'notconnect']
for tag in tags:
    check_tag = nautobot.extras.tags.get(slug=tag.lower())
    if tag == 'STP-Blocking':
        color='aa1409'
    elif tag == 'CDP-Neighbor':
        color = '2196f3'
    else:
        color ='ff5722'
    if check_tag == None:
        nautobot.extras.tags.create(name=tag, color= color, slug=tag.lower())
        check_tag = nautobot.extras.tags.get(slug=tag.lower())
        print (f'Tag "{tag}" with ID: {check_tag.id} generated')
