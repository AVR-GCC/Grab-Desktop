#!/usr/bin/env python3
import customtkinter
import subprocess
import sys
import re
import requests
import time

from huaweiHG8145V5Router import HuaweiHG8145V5Router

router = None
usernameEntry = None
passwordEntry = None
ssnEntry = None
ip = ''
username = ''
password = ''
ssn = ''

def get_gateway_ip():
    gateway_ip = None

    # Determine the command based on the operating system
    if sys.platform.startswith('win'):
        command = 'ipconfig'
    else:
        command = 'netstat -nr'

    # Execute the command and capture the output
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
    except subprocess.CalledProcessError:
        print("Failed to retrieve the gateway IP.")
        return None

    # Extract the gateway IP address from the output
    if sys.platform.startswith('win'):
        # Parse IP address from ipconfig output on Windows
        match = re.search(r'Default Gateway.*?: ([\d.]+)', output, re.IGNORECASE)
        if match:
            gateway_ip = match.group(1)
    else:
        # Parse IP address from netstat output on Linux or macOS
        lines = output.splitlines()
        match = [str.split() for str in lines]
        titles = match[1]
        results = match[2:]
        gateway_index = 0
        flags_index = 0
        cur_index = 0
        
        for title in titles:
            if (title == 'Gateway'):
                gateway_index = cur_index
            if (title == 'Flags'):
                flags_index = cur_index
            cur_index += 1
        
        cur_index = 0
        default_gateway_index = 0
        
        for result in results:
            if (result[flags_index] == "UG"):
                gateway_ip = result[gateway_index]
                
    return gateway_ip

def click():
    global usernameEntry
    global passwordEntry
    global ssnEntry
    global router
    global username
    global password
    global ssn
    new_ip = get_gateway_ip();
    # new_username = usernameEntry.get()
    new_username = "root"
    # new_password = passwordEntry.get()
    new_password = "ysceXhP2"
    # new_ssn = ssnEntry.get()
    new_ssn = "48575443471AE7AB"
    if (new_ip != ip or new_username != username or new_password != password or new_ssn != ssn):
        base_url = "https://" + new_ip;
        print("Connecting to router on ip: " + new_ip)
        print("With username: " + new_username + " password: " + new_password + " ssn: " + new_ssn)
        username = new_username
        password = new_password
        ssn = new_ssn
        try:
            router = HuaweiHG8145V5Router(new_ip, new_username, new_password, new_ssn)
            devices = router.get_devices()
            print(devices)
        except:
            print("Connection to router failed... Please review the inputed information")
        
def start_ui():
    global usernameEntry
    global passwordEntry
    global ssnEntry
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")
    
    root = customtkinter.CTk()
    
    root.geometry("500x350")
    
    frame = customtkinter.CTkFrame(master=root)
    frame.pack(pady=20, padx=60, fill="both", expand=True)
    
    label = customtkinter.CTkLabel(master=frame, text="Grab")
    
    label.pack(pady=12, padx=10)
    
    usernameEntry = customtkinter.CTkEntry(master=frame, placeholder_text="Username")
    usernameEntry.pack(pady=12, padx=10)
    
    passwordEntry = customtkinter.CTkEntry(master=frame, placeholder_text="Password")
    passwordEntry.pack(pady=12, padx=10)
    
    ssnEntry = customtkinter.CTkEntry(master=frame, placeholder_text="SSN")
    ssnEntry.pack(pady=12, padx=10)
    
    # subprocess.run(['xclip', '-selection', 'clipboard'], input=curlCommand.encode(), check=True)
    
    button = customtkinter.CTkButton(master=frame, text="Host", command=click)
    
    button.pack(pady=12, padx=10)
    
    root.mainloop()

start_ui()
print("Hello werrree")

