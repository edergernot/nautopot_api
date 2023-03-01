import pynautobot

HOST="127.0.0.1"
PORT="8080"
TOKEN="14BADCA122B5D74D7DB91FA3A0261970"
nautobot = pynautobot.api(url=f"http://{HOST}:{PORT}", token=TOKEN)

my_platform = "IOS"
my_devicetype = "WS-C3850-24XS"
my_devicename = "swaccess01-1"
my_vendor ="cisco"
my_site = "autosite"
my_status = "active"
my_device_role = "Network"
my_SN="123412324"

# Create Manufacturer if not exist
manufacturer=nautobot.dcim.manufacturers.get(slug=my_vendor.lower())
print(manufacturer)
if manufacturer == None:
    manufacturer = nautobot.dcim.manufacturers.create(name=my_vendor.capitalize(), slug=my_vendor.lower(), description="Created via API")
    print(manufacturer.created)
print(manufacturer.id)

# Create Device Role if not exist
device_role=nautobot.dcim.device_roles.get(slug=my_device_role.lower())
print(device_role)
if device_role == None:
    device_role = nautobot.dcim.device_roles.create(name=my_device_role.capitalize(), slug=my_device_role.lower(), color= "ff0000",description="Created via API")
    print(device_role.created)
print(device_role.id)

# Create Platform if not exist
platform=nautobot.dcim.platforms.get(slug=my_platform.lower())
print(platform)
if platform == None:
    platform = nautobot.dcim.platforms.create(name=my_platform.capitalize(), slug=my_platform.lower(), description="Created via API")
    print(platform.created)
print(platform.id)

# Create Device Type if not exist
device_type=nautobot.dcim.device_types.get(slug=my_devicetype.lower())
print(device_type)
if device_type == None:
    device_type = nautobot.dcim.device_types.create(model=my_devicetype, slug=my_devicetype.lower(), description="Created via API", manufacturer=manufacturer.id)
    print(device_type.created)
print(device_type.id)

# Crete Device:
device =  nautobot.dcim.devices
switch = device.get(name=my_devicename)
site = nautobot.dcim.sites.get(slug=my_site.lower())
if switch == None:
    switch = device.create(device_type=device_type.id, name=my_devicename, device_role=device_role.id, site=site.id, status = my_status.lower(), serial = my_SN)
    print (switch.created)
print (switch.name)    
print (switch.id)
