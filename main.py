#!/usr/bin/env python3
import subprocess
import sys
import re
import requests
import time
import socket
import threading
import pdb

from zeroconf import Zeroconf, ServiceInfo
import customtkinter

from huaweiHG8145V5Router import HuaweiHG8145V5Router

running = None
running_current = None
client_thread = None
terminate_client_thread = None
zeroconf = None
nsd_info = None
router = None
devices = []
usernameEntry = None
passwordEntry = None
ssnEntry = None
ip = ''
username = ''
password = ''
ssn = ''
last_number = 0

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

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

def publish_nsd():
    global zeroconf
    global nsd_info
    local_ip_address = get_local_ip()
    
    if (zeroconf == None):
        zeroconf = Zeroconf()
    
    if (nsd_info == None):
        service_type = "_http._tcp.local."
        service_name = "Grab Provider 3._http._tcp.local."
        service_port = 6146
        
        nsd_info = ServiceInfo(
            service_type,
            service_name,
            addresses=[socket.inet_aton(local_ip_address)],
            port=service_port,
            properties={'path': '/~paulsm/'},
        )
    print("Registering for NSD")
    zeroconf.register_service(nsd_info)
    print("Registered for NSD")

def find_device_by_ip(devices, ip):
    if (len(devices) == 0):
        return None
    for device in devices:
        if (device['ip'] == ip):
            return device
    return None

def return_device_after_time(timeout, device):
    global router
    time.sleep(timeout)
    router.unkick_devices([device['mac']])

def terminate_client(addr):
    global router
    global devices
    global last_number
    last_number = 0
    print("terminating " + addr)
    device = find_device_by_ip(devices, addr)
    if (device == None):
        devices = router.get_devices()
        device = find_device_by_ip(devices, addr)
    if (device == None):
        return
    router.kick_device(device)
    unkick_thread = threading.Thread(target=return_device_after_time, args=[20, device])
    unkick_thread.start()
    

def establish_socket():
    global running
    global running_current
    global terminate_client_thread
    find_client_timeout = 3
    get_transaction_timeout = 5
    running = True
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    host = get_local_ip()
    
    print("Socket hostname: ", host)    
    
    port = 6146                         
    
    serversocket.bind((host, port))
    
    print("Binded")
    
    serversocket.listen(5)
    
    print("Listening")
    
    while running:
        try:
            serversocket.settimeout(find_client_timeout)
            clientsocket, addr = serversocket.accept()
            print("Got a connection from %s" % str(addr))

            clientsocket.settimeout(get_transaction_timeout)
            running_current = True
            while running_current:
                try:
                    data = clientsocket.recv(1024)
                    decoded = data.decode('utf-8')
                    print("recv " + decoded)
                    # pdb.set_trace()
                    if (not confirm_transaction(decoded)):
                        print("transaction failed " + addr[0])
                        terminate_client(addr[0])
                        running_current = False
                except socket.timeout:
                    print("timeout!")
                    terminate_client(addr[0])
                    running_current = False
                # msg = str(incremented)+ "\r\n"
                # clientsocket.send(msg.encode('ascii'))

            clientsocket.close()
        except socket.timeout:
            print("...")
            pass
        except:
            break

def confirm_transaction(tran):
    global last_number
    stripped = tran.strip()
    try:
        number = int(stripped)
        is_valid = last_number + 1 == number
        last_number = number
        return is_valid
    except Exception as e:
        return False
    

def connect_router():
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

def click():
    global client_thread
    connect_router()
    publish_nsd()
    client_thread = threading.Thread(target=establish_socket)
    client_thread.start()

def start_ui():
    global zeroconf
    global nsd_info
    global usernameEntry
    global passwordEntry
    global ssnEntry
    global client_thread
    global running
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
    
    if (zeroconf != None):
        zeroconf.unregister_service(nsd_info)
        zeroconf.close()

    if (client_thread):
        running = False
        client_thread.join()

if __name__ == "__main__":
    start_ui()
    print("Hello werrree")

