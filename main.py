import requests
from smartplug import SmartPlug
import json
import time

def main():
    f = open('config.json')
    config = json.load(f)
    print(config)

    f.close()

    email = config["email"]
    password = config["password"]

    print(email)
    print(password)

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Origin': 'https://www.sunnyportal.com',
        'Referer': 'https://www.sunnyportal.com/Templates/Start.aspx?logout=true',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36 RuxitSynthetic/1.0 v9119321939944316627 t8052286838287810618'
    }

    data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        'ctl00$ContentPlaceHolder1$Logincontrol1$txtUserName': email,
        'ctl00$ContentPlaceHolder1$Logincontrol1$txtPassword': password,
        'ctl00$ContentPlaceHolder1$Logincontrol1$LoginBtn': 'Login',
        'ctl00$ContentPlaceHolder1$Logincontrol1$RedirectURL': '/homemanager',
        'ctl00$ContentPlaceHolder1$Logincontrol1$RedirectPlant': '',
        'ctl00$ContentPlaceHolder1$Logincontrol1$RedirectPage': '',
        'ctl00$ContentPlaceHolder1$Logincontrol1$RedirectDevice': '',
        'ctl00$ContentPlaceHolder1$Logincontrol1$RedirectOther': '',
        'ctl00$ContentPlaceHolder1$Logincontrol1$PlantIdentifier': '',
        'ctl00$ContentPlaceHolder1$Logincontrol1$ServiceAccess': 'true'
    }

    s = requests.Session()

    #Uncomment next lines if you want to use a edimax smartplug
    ip = config["spip"]
    smpas  = config["sppassword"]
    print(ip)
    print(smpas)
    p = SmartPlug(ip, ('admin', smpas))


    while True:
        try:
            response = s.post('https://www.sunnyportal.com/Templates/Start.aspx', headers=headers, data=data)

            print(response.json())

            # Do something with the insights gathered, for example turn on a smartplug for heating
            pvproduct = (response.json()["PV"])
            consumption = (response.json()["TotalConsumption"])
            battery = (response.json()["BatteryChargeStatus"])

            if(pvproduct == None or consumption == None):
                print("error")
            else:
                print("PV:" + str(pvproduct))
                print("TotalConsumption:" + str(consumption))

                if ((pvproduct-consumption) > 3000) and battery>=70:
                    p.state= "ON"
                    print("turning on")
                elif (pvproduct-consumption) <= 0 or (battery<70 and (pvproduct-consumption)<5000):
                    p.state="OFF"
                    print("turning off")
                elif (battery<70 and (pvproduct-consumption)>5000):
                    p.state="ON"
                    print("turning on")

            time.sleep(60*5)
        except Exception as e:
            print("Error: " + str(e))
            time.sleep(60*5)

    
if __name__ =="__main__":
    main()