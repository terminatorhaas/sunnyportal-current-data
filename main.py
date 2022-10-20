from random import randint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.options import Options
import json
import time
import re
from smartplug import SmartPlug
import datetime as dt  


def isNowInTimePeriod(): 
    now = dt.datetime.now()
    print(now)
    current_time = now.strftime("%H:%M:%S")
    start = '06:00:00'
    end = '21:19:20'
    if current_time > start and current_time < end:
        return True
    return False


f = open('config.json')
config = json.load(f)
print(config)

f.close()

options = Options()
#options.add_argument('--headless')
options.add_argument('window-size=1920x1080')
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
options.add_argument(f'user-agent={user_agent}')

email = config["email"]
password = config["password"]

#Uncomment next lines if you want to use a edimax smartplug
ip = config["spip"]
smpas  = config["sppassword"]
print(ip)
print(smpas)
p = SmartPlug(ip, ('admin', smpas))


day= False
driver = webdriver.Chrome('./chromedriver', chrome_options=options)

while True:
    try:
        #time.sleep(randint(300,600))
        if isNowInTimePeriod():

            if day == False:
                driver = webdriver.Chrome('./chromedriver', chrome_options=options)
                driver.get("https://www.sunnyportal.com/Templates/Start.aspx")
                time.sleep(3)
                driver.find_element(By.ID,"txtUserName").send_keys(email)
                time.sleep(2)
                driver.find_element(By.ID,"txtPassword").send_keys(password)
                time.sleep(2)
                driver.find_element(By.ID,"onetrust-reject-all-handler").click()
                time.sleep(2)
                driver.find_element(By.ID,"ctl00_ContentPlaceHolder1_Logincontrol1_LoginBtn").click()
                day = True
            driver.refresh()
            time.sleep(randint(200,300  ))
            driver.find_element(By.ID,"ctl00_ContentPlaceHolder1_CurrentStatusLabel").click()
            element = WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'batteryStatus-pv')))

            pvproduct = ((element.text).splitlines()[1])
            print(pvproduct)

            element = WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'batteryStatus-consumption')))

            consumption = ((element.text).splitlines()[1])
            print(consumption)

            element = WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'batteryStatus-battery')))

            battery =(re.findall(r'\d+', ((element.text).splitlines()[3]))[0])
            print(battery)

            if (float(pvproduct)-float(consumption) > 3.0) and float(battery)>=70.0:
                p.state= "ON"
                print("turning on")
            elif float(pvproduct)-float(consumption) <= 0.0 or (float(battery)<70 and float(pvproduct-consumption)<5.0):
                p.state="OFF"
                print("turning off")
            elif (float(battery)<70.0 and float(pvproduct)-float(consumption)>5.0):
                p.state="ON"
                print("turning on")

        elif day==True:
            driver.close()
            day=False
        else:
            time.sleep(randint(300,600))
    except:
        print("Error")
        day=False

