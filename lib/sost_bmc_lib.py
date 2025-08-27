import os
import requests
import re
import json

class bmc_info():
    def __init__(self, bmc_ip, bmc_user, bmc_pass):
        # Validate the BMC IP address format
        self.bmc_ip = bmc_ip
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', bmc_ip):
            raise ValueError("Invalid BMC IP address format. Please provide a valid IPv4 address.")
        # Validate the BMC IP address format
        self.bmc_user = bmc_user
        self.bmc_pass = bmc_pass
        # Set the BMC type
        self.bmc_type = 'ASTSPEED'
        # Initialize a session for making requests
        self.session = requests.Session()
        self.session.auth = (bmc_user, bmc_pass)
        self.session.verify = False  # Disable SSL verification for simplicity

    def login_ibmc(self):
        url = f'https://{self.bmc_ip}/redfish/v1/SessionService/Sessions'
        headers = {'Content-Type': 'application/json'}
        payload = {
            "UserName": self.bmc_user,
            "Password": self.bmc_pass
        }
        response = self.session.post(url, headers=headers, json=payload)
        if response.status_code != 201:
            raise Exception(f"Login failed: {response.status_code} - {response.text}")
        return response.json()
    
    def login_astspeed(self):
        url = f'https://{self.bmc_ip}/api/login'
        headers = {'Content-Type': 'application/json'}
        payload = {
            "username": self.bmc_user,
            "password": self.bmc_pass
        }
        response = self.session.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.status_code} - {response.text}")
        return response.json()

    def return_bmc_session(self):
        return self.session

if __name__ == "__main__":
    bmc_ip = os.getenv('BMC_IP', '192.168.60.113')
    bmc_user = os.getenv('BMC_USER', 'admin')
    bmc_pass = os.getenv('BMC_PASS', 'admin')
    if not bmc_ip or not bmc_user or not bmc_pass:
        print("Please set BMC_IP, BMC_USER, and BMC_PASS environment variables.")
    else:
        bmc = bmc_info(bmc_ip, bmc_user, bmc_pass)
        try:
            print("BMC Version:", bmc.get_bmc_version())
            print("BIOS Version:", bmc.get_bios_version())
        except Exception as e:
            print(f"Error: {e}")