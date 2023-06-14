#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

class HuaweiHG8145V5Router:
  def __init__(self, ip, username, password, ssn):  
    self.tabs = []
    self.devices = []
    self.devices_list_open = False
    options = Options()
    options.set_preference('acceptInsecureCerts', True)
    options.add_argument('--headless')
    
    self.driver = webdriver.Firefox(options=options)
    self.wait = WebDriverWait(self.driver, 10)
    self.driver.get("https://" + ip)
    self.wait.until(EC.presence_of_element_located((By.ID, "txt_Username")))
    print("Page opened")
    
    user_name_input = self.driver.find_element(by=By.ID, value="txt_Username")
    password_input = self.driver.find_element(by=By.ID, value="txt_Password")
    ssn_input = self.driver.find_element(by=By.ID, value="txt_loginsn")
    
    user_name_input.send_keys(username)
    password_input.send_keys(password)
    ssn_input.send_keys(ssn)
    
    print("Logging in...")
    
    self.driver.execute_script("LoginSubmit(\"loginbutton\");")
    self.location = 'main'
    self.go_to_frame("menuIframe")
    self.wait.until(EC.element_to_be_clickable((By.ID, "wifidevIcon")))
    self.driver.switch_to.default_content()
    
    print("Logged in.")
    self.get_current_page()
  
  def go_to_main(self):
    if (self.location != "main"):
      self.tabs[0].click()
      location = 'main'
      
  def go_to_advance(self):
    self.devices_list_open = False
    if (self.location != "advance"):
      self.tabs[3].click()
      self.location = "advance"
  
  def go_to_frame(self, id):
    self.wait.until(EC.presence_of_element_located((By.ID, id)))
    self.driver.switch_to.frame(id)
  
  def get_current_page(self):
    if (len(self.tabs) == 0):
      self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "menuContent")))
      self.tabs = self.driver.find_elements(by=By.CLASS_NAME, value="menuContent")
    for tab in self.tabs:
      atts = tab.get_attribute("class")
      if (len(atts.split(' ')) > 1):
        return tab.get_attribute("id")
    return None
  
  def get_devices(self):
    print("Getting devices")
    self.go_to_main()
    if (self.devices_list_open): 
      self.go_to_frame("ContectdevmngtPageSrc")
      refreshButton = self.wait.until(EC.element_to_be_clickable((By.ID, "refresh")))
      refreshButton.click()
    else:
      self.go_to_frame("menuIframe")
      devicesIcon = self.wait.until(EC.element_to_be_clickable((By.ID, "wifidevIcon")))
      devicesIcon.click()
    self.devices_list_open = True
    self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "DevTableList")))
  
    # names
    labels = self.driver.find_elements(by=By.TAG_NAME, value="label")
    names = [label.get_attribute("title") for label in labels][1:]
  
    # info
    infoDivs = self.driver.find_elements(by=By.XPATH, value="//*[contains(@id, 'DivIpandMac')]");
    infos = [info.text for info in infoDivs]
      
    # statuses
    statusesDivs = self.driver.find_elements(by=By.XPATH, value="//*[contains(@id, 'DivDevStatus')]");
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
  
    self.driver.switch_to.default_content()
    print("Devices: " + str(devices))
    return devices
    
  def to_mac_filtering(self):
    self.go_to_advance()
    security_config_button = self.wait.until(EC.element_to_be_clickable((By.ID, "securityconfig")))
    security_config_button.click()
    wifi_mac_filtering_button = self.wait.until(EC.element_to_be_clickable((By.ID, "wlanmacfilter")))
    wifi_mac_filtering_button.click()
    self.go_to_frame("menuIframe")
    enable_filtering_checkbox = self.wait.until(EC.element_to_be_clickable((By.ID, "EnableMacFilter")))
    return enable_filtering_checkbox
  
  def kick_device(self, device):
    print("Kicking device " + str(device))
    enable_filtering_checkbox = self.to_mac_filtering()
    if(not enable_filtering_checkbox.is_selected()):
      enable_filtering_checkbox.click()
    new_button = self.wait.until(EC.element_to_be_clickable((By.ID, "Newbutton")))
    new_button.click()
    
    device_name_input = self.wait.until(EC.element_to_be_clickable((By.ID, "DeviceName")))
    device_mac_address_input = self.wait.until(EC.element_to_be_clickable((By.ID, "SourceMACAddress")))
    
    device_name_input.send_keys(device['name'])
    device_mac_address_input.send_keys(device['mac'])
    
    self.driver.execute_script("SubmitEx();")
    self.driver.switch_to.default_content()
    print("Device kicked.")
    
  def unkick_devices(self, macs):
    print("Unkicking devices " + str(macs))
    self.to_mac_filtering()
    macCells = self.driver.find_elements(by=By.XPATH, value="//*[contains(@id, 'WMacfilterConfigList')]");
    for cell in macCells:
      if (cell.text in macs or len(macs) == 0):
        id = cell.get_attribute("id")
        index = id.split('_')[1]
        checkBox = self.wait.until(EC.element_to_be_clickable((By.ID, "WMacfilterConfigList_rml" + index)))
        checkBox.click()
    deleteButton = self.wait.until(EC.element_to_be_clickable((By.ID, "DeleteButton")))
    deleteButton.click()
    alert = self.driver.switch_to.alert
    alert.accept()
    self.driver.switch_to.default_content()
    print("Devices unkicked.")
  
  def __del__(self):
    print("Closing router.")
    self.driver.close()

if __name__ == "__main__":
  new_ip = '192.168.100.1'
  new_username = "root"
  new_password = "ysceXhP2"
  new_ssn = "48575443471AE7AB"
  router = HuaweiHG8145V5Router(new_ip, new_username, new_password, new_ssn)
  devices = router.get_devices()
  print(devices)
  time.sleep(10)
  # unkick_device(["0c:7a:15:77:1c:b7"])
  # time.sleep(5)
  # close()