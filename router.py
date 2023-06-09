#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

driver = None
wait = None
tabs = []
devices = []
location = 'main'

def initialize(ip, username, password, ssn):
  global driver
  global wait

  options = Options()
  options.set_preference('acceptInsecureCerts', True)
  options.add_argument('--headless')
  
  driver = webdriver.Firefox(options=options)
  wait = WebDriverWait(driver, 10)
  driver.get("https://" + ip)
  wait.until(EC.presence_of_element_located((By.ID, "txt_Username")))
  print("Page opened")
  
  user_name_input = driver.find_element(by=By.ID, value="txt_Username")
  password_input = driver.find_element(by=By.ID, value="txt_Password")
  ssn_input = driver.find_element(by=By.ID, value="txt_loginsn")
  
  user_name_input.send_keys(username)
  password_input.send_keys(password)
  ssn_input.send_keys(ssn)
  
  print("Logging in...")
  
  driver.execute_script("LoginSubmit(\"loginbutton\");")
  go_to_frame("menuIframe")
  wait.until(EC.element_to_be_clickable((By.ID, "wifidevIcon")))
  driver.switch_to.default_content()
  
  print("Logged in.")
  
  get_current_page()
  
def go_to_main():
  global location
  if (location != "main"):
    print("Moving to main page")
    tabs[0].click()
    location = 'main'
    
def go_to_advance():
  global location
  if (location != "advance"):
    print("Moving to advanced page")
    tabs[3].click()
    location = "advance"

def go_to_frame(id):
  wait.until(EC.presence_of_element_located((By.ID, id)))
  driver.switch_to.frame(id)

def get_current_page():
  global tabs
  if (len(tabs) == 0):
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "menuContent")))
    tabs = driver.find_elements(by=By.CLASS_NAME, value="menuContent")
  for tab in tabs:
    atts = tab.get_attribute("class")
    if (len(atts.split(' ')) > 1):
      return tab.get_attribute("id")
  return None

def get_devices():
  global tabs
  global devices
  global location
  print("Getting devices")
  go_to_main()
  go_to_frame("menuIframe")
  devicesIcon = wait.until(EC.element_to_be_clickable((By.ID, "wifidevIcon")))
  devicesIcon.click()
  go_to_frame("ContectdevmngtPageSrc")
  wait.until(EC.presence_of_element_located((By.CLASS_NAME, "DevTableList")))

  # names
  labels = driver.find_elements(by=By.TAG_NAME, value="label")
  names = [label.get_attribute("title") for label in labels][1:]

  # info
  infoDivs = driver.find_elements(by=By.XPATH, value="//*[contains(@id, 'DivIpandMac')]");
  infos = [info.text for info in infoDivs]
    
  # statuses
  statusesDivs = driver.find_elements(by=By.XPATH, value="//*[contains(@id, 'DivDevStatus')]");
  statuses = [status.text for status in statusesDivs]
    
  devices = []
    
  for index in range(len(names)):
    if (statuses[index] == "Online"):
      splittedInfo = infos[index].splitlines()
      devices.append({
        'name': names[index],
        'mac': splittedInfo[0],
        'ip': splittedInfo[1]
      })

  driver.switch_to.default_content()
  return devices
  
def to_mac_filtering():
  global tabs
  global location
  go_to_advance()
  security_config_button = wait.until(EC.element_to_be_clickable((By.ID, "securityconfig")))
  security_config_button.click()
  wifi_mac_filtering_button = wait.until(EC.element_to_be_clickable((By.ID, "wlanmacfilter")))
  wifi_mac_filtering_button.click()
  go_to_frame("menuIframe")
  enable_filtering_checkbox = wait.until(EC.element_to_be_clickable((By.ID, "EnableMacFilter")))

def kick_device(device):
  print("Kicking device " + device['name'])
  to_mac_filtering()
  if(not enable_filtering_checkbox.is_selected()):
    enable_filtering_checkbox.click()
  new_button = wait.until(EC.element_to_be_clickable((By.ID, "Newbutton")))
  new_button.click()
  
  device_name_input = wait.until(EC.element_to_be_clickable((By.ID, "DeviceName")))
  device_mac_address_input = wait.until(EC.element_to_be_clickable((By.ID, "SourceMACAddress")))
  
  device_name_input.send_keys(device['name'])
  device_mac_address_input.send_keys(device['mac'])
  
  driver.execute_script("SubmitEx();")
  driver.switch_to.default_content()
  print("Device kicked")
  
def unkick_device(macs):
  print("Unkicking device " + device['name'])
  to_mac_filtering()
  macCells = driver.find_elements(by=By.XPATH, value="//*[contains(@id, 'WMacfilterConfigList')]");
  for cell in macCells:
    if (cell.text in macs or len(macs) == 0):
      id = cell.get_attribute("id")
      index = id.split('_')[1]
      checkBox = wait.until(EC.element_to_be_clickable((By.ID, "WMacfilterConfigList_rml" + index)))
      checkBox.click()
  deleteButton = wait.until(EC.element_to_be_clickable((By.ID, "DeleteButton")))
  deleteButton.click()
  alert = driver.switch_to.alert
  alert.accept()
  driver.switch_to.default_content()
  print("Device unkicked")

def close():
  driver.close()

# initialize("192.168.100.1", "root", "ysceXhP2", "48575443471AE7AB")
# print("Finished initialization")
# get_devices()
# unkick_device(["0c:7a:15:77:1c:b7"])
# time.sleep(5)
# close()