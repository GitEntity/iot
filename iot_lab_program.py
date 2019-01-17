import json
import requests
import SensorsInterface

# send data via HTTP POST request
def send_data_thingsboard():
   URL = 'http://demo.thingsboard.io/api/v1/VQbcYDA2UI9b1GJKkcyS/telemetry'
   list_dict = []
   dict = {}
   light = SensorsInterface.getAmbientLight()
   if light < 10:
       SensorsInterface.ledOn()
   else:
       SensorsInterface.ledOff()
   dict["Light"] = light
   list_dict.append(dict)
   r = requests.post(URL, data = json.dumps(list_dict))
  
def main():
   send_data_thingsboard()

# main function
if __name__ == '__main__':
  # get values and connect to the local database
   try:
  SensorsInterface.setupSensorian()
       while True:
          main()
   # reset by pressing CTRL + C
   except KeyboardInterrupt:
       print("Data retreival stopped by user")
