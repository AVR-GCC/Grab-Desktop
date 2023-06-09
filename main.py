#!/usr/bin/env python3
import customtkinter
import subprocess
import sys
import re
import requests
import time

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
        
    print("output", output)

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

def click():
    print("Clicked!")
    # print(usernameEntry.get())
    # print(dir(netmiko))
    gateway_ip = get_gateway_ip();
    base_url = "https://" + gateway_ip;
    rand_count_url = base_url + "/asp/GetRandCount.asp"
    login_url = base_url + "/login.cgi?&CheckCodeErrFile=login.asp"
    username = "root"
    password = "ysceXhP2"
    ssn = "48575443471AE7AB"
    print(gateway_ip)
    
   
button = customtkinter.CTkButton(master=frame, text="Host", command=click)

button.pack(pady=12, padx=10)

root.mainloop()

print("Hello werrree")

