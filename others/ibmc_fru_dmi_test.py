# ---------------------------------
# Linux iBMC FRU AutoTestTools
# Author       ： Fan Xiaodong
# Writing Date : 2026-01-27
# ---------------------------------
import os
import json

# ipmitool tool Location
ipmitool_tools = 'ipmitool'
# Product dmi Handle
product_dmi_handle = '0x0001'
# Board dmi Handle
board_dmi_handle = '0x0003'
# Chassis dmi Handle
chassis_dmi_handle = '0x0002'

def fru_data_format():
    '''
    This function returns the data format of the FRU info
    return ipmitool fru list 0 json data
    '''
    data = {}
    fru_data = os.popen(f"{ipmitool_tools} fru list 0").read()
    for line in fru_data.splitlines():
        if ":" in line:
            key , value = line.split(":")[0], line.split(":")[1]
            data[key.strip()] = value.strip()
    return json.loads(json.dumps(data, indent=4))

def dmi_data_format(handle):
    '''
    This function returns the data format of the DMI info
    return ipmitool dmi info <handle> json data
    '''
    data = {}
    dmi_data = os.popen(f"dmidecode -H {handle} ").read()
    for line in dmi_data.splitlines():
        if ":" in line:
            key , value = line.split(":")[0], line.split(":")[1]
            data[key.strip()] = value.strip()
    return json.loads(json.dumps(data, indent=4))

def _match_pr(fru_data,dmi_data,fru_key,dmi_key):
    '''
    This function matches two values and prints the result
    '''
    if fru_data != dmi_data:
        print(f"\033[91mFail\033[0m ".ljust(19)+fru_key.ljust(30)+fru_data.ljust(50)+dmi_key.ljust(30)+dmi_data)
    else:
        print(f"\033[92mPass\033[0m ".ljust(19)+fru_key.ljust(30)+fru_data.ljust(50)+dmi_key.ljust(30)+dmi_data)


def check_product_fru_dmi_info():
    '''
    This function checks if the product FRU DMI info is correct
    '''
    
    fru_data = fru_data_format()
    dmi_data = dmi_data_format(product_dmi_handle)    
    print("\n=============== Product FRU DMI Info Check [Fru & dmidecode -t 1]===============")
    print("[Result]".ljust(10)+"[FRU Key]".ljust(30)+"[FRU Data]".ljust(50)+"[DMI Key]".ljust(30)+"[DMI Data]")
    _match_pr(fru_data['Product Manufacturer'], dmi_data['Manufacturer'], 'Product Manufacturer', 'Manufacturer')
    _match_pr(fru_data['Product Name'], dmi_data['Product Name'], 'Product Name', 'Product Name')
    _match_pr(fru_data['Product Version'], dmi_data['Version'], 'Product Version', 'Version')
    _match_pr(fru_data['Product Serial'], dmi_data['Serial Number'], 'Product Serial', 'Serial Number')

def check_board_fru_dmi_info():
    '''
    This function checks if the board FRU DMI info is correct
    '''
    
    fru_data = fru_data_format()
    board_dmi_data = dmi_data_format(board_dmi_handle)
    print("\n=============== Board FRU DMI Info Check [Fru & dmidecode -t 2]===============")
    print("[Result]".ljust(10)+"[FRU Key]".ljust(30)+"[FRU Data]".ljust(50)+"[DMI Key]".ljust(30)+"[DMI Data]")
    _match_pr(fru_data['Board Mfg'], board_dmi_data['Manufacturer'], 'Board Mfg', 'Manufacturer')
    _match_pr(fru_data['Board Product'], board_dmi_data['Product Name'], 'Board Product', 'Product Name')
    _match_pr(fru_data['Board Part Number'], board_dmi_data['Version'], 'Board Part Number', 'Version')
    _match_pr(fru_data['Board Serial'], board_dmi_data['Serial Number'], 'Board Serial', 'Serial Number')
    _match_pr(fru_data['Product Asset Tag'],board_dmi_data['Asset Tag'] , 'Product Asset Tag', 'Asset Tag')

def check_chassis_fru_dmi_info():
    '''
    This function checks if the chassis FRU DMI info is correct
    '''
    print("\n=============== Chassis FRU DMI Info Check [Fru & dmidecode -t 3]===============")
    print("[Result]".ljust(10)+"[FRU Key]".ljust(30)+"[FRU Data]".ljust(50)+"[DMI Key]".ljust(30)+"[DMI Data]")
    fru_data = fru_data_format()
    chassis_dmi_data = dmi_data_format(chassis_dmi_handle)
    _match_pr(fru_data['Chassis Type'], chassis_dmi_data['Type'], 'Chassis Type', 'Type')
    _match_pr(fru_data['Chassis Part Number'], chassis_dmi_data['Version'], 'Chassis Part Number', 'Version')
    _match_pr(fru_data['Chassis Serial'], chassis_dmi_data['Serial Number'], 'Chassis Serial', 'Serial Number')
    _match_pr(fru_data['Product Asset Tag'], chassis_dmi_data['Asset Tag'], 'Product Asset Tag', 'Asset Tag')

if __name__ == "__main__":
    check_product_fru_dmi_info()
    check_board_fru_dmi_info()
    check_chassis_fru_dmi_info()