'''Unzips the NetworkDump.zip to Folder Unzip
Parses the Raw-Files and feed Nautobot'''

import os
import shutil
from ntc_templates.parse import parse_output
import pynautobot

UPLOAD_FOLDER = './input_files'
files_to_parse = []
dump_data = {}

HOST="127.0.0.1"
PORT="8080"
TOKEN="14BADCA122B5D74D7DB91FA3A0261970"
nautobot = pynautobot.api(url=f"http://{HOST}:{PORT}", token=TOKEN, threading=True,)


def add_to_data(key,data,hostname):
    global dump_data
    if key not in  dump_data.keys():
        dump_data[key]=[]
    for line in data:
        item ={}
        item['Devicename']=hostname
        for k in line.keys():
            item[k]=line[k]
        dump_data[key].append(item)

def unzip_all_files():
    print('Unzipping Dump-Files')
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.split(".")[-1] == "zip"]
    for file in files:
        shutil.unpack_archive(f"{UPLOAD_FOLDER}/{file}", UPLOAD_FOLDER)
        os.remove(f"{UPLOAD_FOLDER}/{file}")

def get_all_commandfiles(folder):
    command_files = []
    files = [f for f in os.listdir(folder) if os.path.isfile(f'{folder}/{f}')]
    command_files = [f for f in files if f[-12:]=='_command.txt']
    return (command_files)

def parse_command(command,output,platform):
    try:
        parsed=parse_output(platform=platform, command=command, data=output)
        return parsed
    except Exception as e:
        return ("ERROR")

def check_platform(output):
    if "Cisco IOS Software" in output:
        return ('cisco_ios')
    if "Cisco Nexus Operating System" in output:
        return ('cisco_nxos')
    if "Paloalto" in output:
        return ('paloalto_panos')
    if "Adaptive" or "ASA" in output:
        return ('cisco_asa')
    else:
        return ('cisco_ios')

def feed_device_model(output,platform):
    if "Cisco" in output:
        manufacturer='CiscoSystems'
    if "Paloalto" in output:
        manufacturer='PaloaltoNetworks'
    check_manufacturer=nautobot.dcim.manufacturers.get(slug=manufacturer.lower())
    if check_manufacturer==None:
        nautobot.dcim.manufacturers.create(slug=manufacturer.lower(), name=manufacturer, decription="Created via API")
        new_manufacturer=nautobot.dcim.manufacturers.get(slug=manufacturer.lower())
        print(f"Manufacturer {manufacturer} with ID: {new_manufacturer.id} gerated")
    manufacturer_id=nautobot.dcim.manufacturers.get(slug=manufacturer.lower())
    parsed = parse_command('show version',output, platform) 
    if parsed[0].get('platform'):
        device_type=parsed[0]['platform']
        check_device_type=nautobot.dcim.device_types.get(slug=device_type.lower())
        if check_device_type==None:
            nautobot.dcim.device_types.create(model=device_type, slug=device_type.lower(), manufacturer=manufacturer_id.id)
            device_type_id=nautobot.dcim.device_types.get(slug=device_type.lower())
            print (f'DeviceType {device_type} with ID: {device_type_id.id} created')
    elif parsed[0].get('hardware'): # Get back List
        device_type=parsed[0]['hardware']
        for device_typ in device_type:
            check_device_type=nautobot.dcim.device_types.get(slug=device_typ.lower())
            if check_device_type==None:
                nautobot.dcim.device_types.create(model=device_typ, slug=device_typ.lower(), manufacturer=manufacturer_id.id)
                device_type_id=nautobot.dcim.device_types.get(slug=device_typ.lower())
                print (f'DeviceType {device_type} with ID: {device_type_id.id} created')
    
def feed_device(data):
    print("Feeding Nautobot with Devices")
    for item in data:
        hostname = item['hostname']
        device_role=nautobot.dcim.device_roles.get(slug='network')
        site = nautobot.dcim.sites.get(slug='autosite')
        check_device=nautobot.dcim.devices.get(name=hostname)  # check if device allready exist
        if check_device!=None: # Next item if Device not found
            continue
        if item.get('hardware'):
            device_type=item['hardware'][0]
        elif item.get('platform'):
            device_type=item['platform']
        device_type_id=nautobot.dcim.device_types.get(slug=device_type.lower())
        if type(item['serial']) == list:
            serial = item['serial'][0]
        else :
            serial = item['serial']
        nautobot.dcim.devices.create(name=hostname, device_type=device_type_id.id, status='active', device_role=device_role.id, site=site.id, serial=serial )
        print(f'Device {hostname} created')
         
def parse_file(file):
    platform='cisco_ios'
    hostname=file[:-12]
    with open(f"{UPLOAD_FOLDER}/{file}") as f:
        f_data=f.read()
    f_data1 = f_data.split('\n****************************************\n')
    for blob in f_data1:
        try:
            blobsplit=blob.split('\n**----------------------------------------**\n')
            command=blobsplit[0]
            output=blobsplit[1]
        except IndexError:
            continue
        if command == "show version":
            platform = check_platform(output)
            feed_device_model(output,platform)
        try:
            parsedcommand=parse_command(command,output,platform)
        except:
            continue
        key=command.replace(" ","_")
        if parsedcommand == "ERROR":
            continue
        add_to_data(key,parsedcommand,hostname)

def feed_vlans_nautobot(vlans):
    print('Feeding Nautobot with VLANs')
    for vlan in vlans:
        ID=(int(vlan['vlan_id']))
        check_vlan=nautobot.ipam.vlans.get(vid=ID)
        if check_vlan!=None: # Vlan allready exist
            continue
        if vlan['status']!='active': # Vlan is not active
            continue
        site_id=nautobot.dcim.sites.get(slug='autosite')
        nautobot.ipam.vlans.create(vid=ID, name=vlan['name'], status=vlan['status'], site=site_id.id)
        print(f'VLAN{ID}  is created')

def feed_prefix(data):
    print('feeding prefixes to Nautobot')
    for line in data:

        if line['protocol']!='C':
            continue
        line_prefix=f"{line['network']}/{line['mask']}"
        check_prefix=nautobot.ipam.prefixes.get(prefix=line_prefix)
        if check_prefix!=None:
            continue
        if 'Vlan' in line['nexthop_if']:
            ID=line['nexthop_if'][4:]
            vlan_id = check_vlan=nautobot.ipam.vlans.get(vid=ID)
            nautobot.ipam.prefixes.create(prefix=line_prefix, status='active', description=f'Routed on {line["Devicename"]}', vlan=vlan_id.id)
        else:
            nautobot.ipam.prefixes.create(prefix=line_prefix, status='active', description=f'Routed on {line["Devicename"]}')
        print(f'Prefix {line_prefix} created')

def feed_ip_addresses(data):
    print('feeding IP-Addresses')
    counter=0
    for line in data:
        ip_addr=line['address']+'/32'
        mac=line['mac']
        hostname=line['Devicename']
        check_ip=nautobot.ipam.ip_addresses.get(address=ip_addr)
        if check_ip!=None:
            continue
        nautobot.ipam.ip_addresses.create(address=ip_addr, status='active', description=f'MAC-Addr: {mac} learned on Device {hostname}')
        counter+=1
        if counter%10 == 0:
            print(f'{counter} IP-Addresses added')

def find_int_type(data):
    '''Needet to return supported Iterface - Type 
    virtual, lag,100base-tx, 1000base-t, 2.5gbase-t, 5gbase-t, 10gbase-t, 10gbase-cx4,1000base-x-gbic,1000base-x-sfp,10gbase-x-sfpp,
    10gbase-x-xfp, 10gbase-x-xenpak, 10gbase-x-x2, 25gbase-x-sfp28, 40gbase-x-qsfpp, 50gbase-x-sfp28, 100gbase-x-cfp, 100gbase-x-cfp2,
    200gbase-x-cfp2, 100gbase-x-cfp4, 100gbase-x-cpak, 100gbase-x-qsfp28, 200gbase-x-qsfp56, 400gbase-x-qsfpdd, 400gbase-x-osfp,
    ieee802.11a, ieee802.11g, ieee802.11n, ieee802.11ac, ieee802.11ad, ieee802.11ax, gsm, cdma, lte, sonet-oc3, sonet-oc12,
    sonet-oc48, sonet-oc192, sonet-oc768, sonet-oc1920, sonet-oc3840, 1gfc-sfp, 2gfc-sfp, 4gfc-sfp, 8gfc-sfpp, 16gfc-sfpp, 32gfc-sfp28,
    64gfc-qsfpp, 128gfc-sfp28, infiniband-sdr, infiniband-ddr, infiniband-qdr, infiniband-fdr10, infiniband-fdr, infiniband-edr,
    infiniband-hdr, infiniband-ndr, infiniband-xdr, t1, e1, t3, e3, cisco-stackwise, cisco-stackwise-plus, cisco-flexstack,
    cisco-flexstack-plus, juniper-vcp, extreme-summitstack, extreme-summitstack-128, extreme-summitstack-256, extreme-summitstack-512, other" '''
    if data['port'][:2]=='Fa':
        return('100base-tx')
    elif data['port'][:2]=='Gi' and data['type'][-2:]=='TX':
        return('1000base-t')
    elif data['port'][:2]=='Gi':
        return('1000base-x-sfp')
    elif data['port'][:2]=='Te' and data['type'][-2:]=='TX':
        return ('10gbase-t')
    elif data['port'][:2]=='Te':
        return ('10gbase-x-xfp')
    elif data['port'][:2]=='Tw':
        return('25gbase-x-sfp28')
    elif data['port'][:2]=='Hu':
        return('100gbase-x-qsfp28')
    elif data['port'][:2]=='Fo':
        return('40gbase-x-qsfpp')
    else:
        return('other')
      
def feed_interfaces(data):
    print('Feeding Interfaces')
    count=0
    for line in data:
        tags=[]
        hostname=line['Devicename']
        name = line['port']
        device=nautobot.dcim.devices.get(name=hostname)
        int_type = find_int_type(line)
        if line['vlan']=='trunk':
            mode='tagged'
        else:
            mode='access'
        #check_interface=nautobot.dcim.interfaces.filter(device=device.id, name=name) 
        #if check_interface != None:
        #    continue
        if line['status']=='notconnect':
            tag=nautobot.extras.tags.get(slug='notconnect')
            tags.append(tag.id)
        if line['status']=='disabled':
            enabled=False
        else:
            enabled=True
        try:
            nautobot.dcim.interfaces.create(device=device.id, name=name, type=int_type, description=line['name'], mode=mode, tags=tags, enabled=enabled)
        except pynautobot.core.query.RequestError:
            continue
        count+=1
        if count%10 == 0:
            print(f'{count} interfaces created')
        
def feed_nautobot(dump_data: dict):
    # Add devices
    feed_device(dump_data['show_version'])
    print('Devices done')

    # Add Vlans
    feed_vlans_nautobot(dump_data['show_vlan'])
    print('VLANS done')
        
    # Add Prefix from show_ip_route
    feed_prefix(dump_data['show_ip_route'])   
    print('Prexixes done') 

    # Add IP-Adresses from show_ip_arp
    feed_ip_addresses((dump_data['show_ip_arp']))
    print('IP-Adresses done')

    #Add Interfaces to device-types
    feed_interfaces(dump_data["show_interfaces_status"])
    print ('Interfaces done')

    
   




########################################################

if __name__ == '__main__':
    
    unzip_all_files()
    files_to_parse=get_all_commandfiles(UPLOAD_FOLDER)
    for file in files_to_parse:
        print(f"Parsing File {file}")
        parse_file(file)
    print('parsing done, feeding nautobot')
    feed_nautobot(dump_data)

#    print('*'*40)
#    print(dump_data["show_interfaces_status"])


   




