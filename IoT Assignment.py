import sqlite3
import datetime
import requests
import RPi.GPIO as GPIO
import subprocess, sys
import time
import json

# toggle LED
def toggle(state):
    if state:
        GPIO.output(4, GPIO.HIGH)
    else:
        GPIO.output(4, GPIO.LOW)
    
"""
Input:  Conn    -> SQLite Connection Object
        Data    -> Dictionary Object
        table_name    -> Table Name
Process:        -> Inserts data in to DB with the key as the column name in DB
"""
def add_data_local_db(conn, data, table_name):
    cur = conn.cursor()
    db_heading = []
    for key in list(data.keys()):
        if key is "timestamp":
            db_heading.append(key+' TEXT NULL PRIMARY KEY')
        else:
            db_heading.append(key+' INTEGER NULL')
    create_table = "CREATE TABLE IF NOT EXISTS " + table_name + "(" + ','.join(db_heading) + ");"
    cur.execute(create_table)
    cur.execute(
            'INSERT OR REPLACE INTO ' + table_name + '(' + ','.join(list(data.keys())) + ") VALUES ('" + "','".join(list(data.values())) + "')")
    conn.commit()

# send data via HTTP POST request
def send_data_thingsboard(conn):
    URL = 'http://demo.thingsboard.io/api/v1/T7CVaWF4kbbMtPHJGGjf/telemetry'
    cur = conn.cursor()
    query = "SELECT * FROM Sensor_Data"
    cur.execute(query)
    list_dict = []
    result = cur.fetchall()
    for array in result:
        dict = {}
        dict["Temperature"] = array[0]
        dict["Light"] = array[1]
        dict["Barometer"]= array[2]
        dict["timestamp"]= array[3]
        dict["Humidity"] = array[4]
        list_dict.append(dict)
    
    r = requests.post(URL, data = json.dumps(list_dict))
    if r.status_code == 200:
        query = "DELETE FROM Sensor_Data"
        cur.execute(query)
        return True        
    else:
        return False
    
# receive temperature (ambient: values[0], IR temp: values[1])
def getTemp(line):
    index = line.find("(")
    line = line[index+1:len(line)-2]
    values = line.split(", ")
    value = float(values[0])
    print ("Temp value: ", value)
    if value > 25:
        toggle(True)
    else:
        toggle(False)
    return values[0]

# parse humidity data
def getHumidity(line):
    index = line.find("(")
    line = line[index+1:len(line)-2]
    values = line.split(", ")
    return values[0]

# parse light data
def getLight(line):
    line = line.replace("Light:  ", "")
    return line

# parse barometer data
def getBarometer(line):
    index = line.find("(")
    line = line[index+1:len(line)-2]
    values = line.split(", ")
    return values[0]

# main function
if __name__ == '__main__':
    # define GPIO setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(4, GPIO.OUT)
    
    # command to run
    cmd = "sensortag -T -H -B -L 24:71:89:BB:FB:04"

    # create a process to pipe a command to the command line
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	# define dictionary to hold values from command
    dict_values = {}
	# connect to local database
    conn = sqlite3.connect("local.db")
	# define database table name
    table_name = "Sensor_Data"
    count = 0
    
	# get values and connect to the local database
    try:
        while True:
            # read the contents of the command line
            out = p.stdout.readline()
            line = out.decode("utf-8")
            
            # save values in a dictionary
            if "Temp" in line:
                dict_values["Temperature"] = getTemp(line)
            elif "Humidity" in line:
                dict_values["Humidity"] = getHumidity(line)
            elif "Barometer" in line:
                dict_values["Barometer"] = getBarometer(line)
            elif "Light" in line:
                dict_values["Light"] = getLight(line)
                dict_values["timestamp"] = str(datetime.datetime.now())
                count += 1
                send_data_live(dict_values)
                # add dictionary to local DB
                #add_data_local_db(conn, dict_values, table_name)
           # if count == 2:
           #     count = 0
           #     send_data_thingsboard(conn)
            
    # reset by pressing CTRL + C
    except KeyboardInterrupt:
        conn.close()
        GPIO.cleanup()
        print("Data retreival stopped by user")