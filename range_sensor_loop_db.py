# import required libraries
import RPi.GPIO as GPIO
import time
import psycopg2
import sys
from datetime import datetime

parking_id = None
reserved = False
parking_list = []
DATABASE_URL = "postgres://xvemqfxjegjchm:ec00778873a847ce6432fcb422ffb35cdd3560fb0f61b9968bab5dae7bfa774c@ec2-54-235-156-60.compute-1.amazonaws.com:5432/dcgid45fi7n6ll"
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

def toggle(state, LEDid):
    if state:
        GPIO.output(LEDid, GPIO.HIGH)
    else:
        GPIO.output(LEDid, GPIO.LOW)

def distance(TRIG, ECHO):


    # initiate pulse (10 microseconds)
    # cause sensor to start ranging (8 x 40 kHz ultrasound bursts)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # listen to input pin (start time of pulse)
    pulse_start = time.time()
    while GPIO.input(ECHO)== 0:
        pulse_start = time.time()

    # listen to input pin (Round trip time of pulse)
    pulse_end = time.time()
    while GPIO.input(ECHO)==1:
        pulse_end = time.time()
        
    # compute pulse duration    
    pulse_duration = pulse_end - pulse_start

    # compute object distance
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because pulse is sent there and back (RTT)
    distance = (pulse_duration * 34300) / 2
    # round distance value to two decimal places
    distance = round(distance, 2)
    
    # return distance
    return distance

def is_empty(parking_id, state, conn):
    print(parking_id)
    cur = conn.cursor()
    sql = "INSERT INTO parking (id, is_empty) VALUES ('"+parking_id+"','"+str(state)+"') ON CONFLICT (id) DO UPDATE SET is_empty= "+str(state)+";"
    print(sql)
    cur.execute(sql)
    conn.commit()

def select_all(conn):
    cur = conn.cursor()
    sql = "SELECT * FROM parking"
    print(sql)
    cur.execute(sql)
    conn.commit()
    return cur.fetchall()

def reserve_listen(conn, LEDid):
    global reserved
    global parking_id
    cur = conn.cursor()
    sql = "SELECT * FROM parking WHERE id='"+parking_id+"';"
    cur.execute(sql)
    db_data = cur.fetchall()
    for element in db_data:
        print(element)
        if element[4] != None and element[5] != None:
            startTime = datetime.strptime(element[4], "%Y-%m-%d %H:%M:%S")
            endTime = datetime.strptime(element[5], "%Y-%m-%d %H:%M:%S")
            if datetime.now() >= startTime and datetime.now() <= endTime:
                reserved = True
                toggle(True, LEDid)
            else:
                emptyUserId(parking_id)
                reserved = False
                toggle(False, LEDid)
       
def emptyUserId(parking_id):
    global reserved
    cur = conn.cursor()
    sql = "UPDATE parking SET is_reserved=False AND reserved_at=NULL AND reserved_till=NULL AND user_id=NULL WHERE id='"+parking_id+"';"
    cur.execute(sql)
    conn.commit()

    
def getVacancy(conn, TRIG, ECHO, LEDid):
    global reserved
    global parking_list
    global parking_id
    #check if distance is less than 20 cm then update DB that car is parked
    dist = distance(TRIG, ECHO)
    print(dist)
    if dist < 20:
        print("we here")
        parking_list.append(True)
        
    else:
        print("not here")
        parking_list.append(False)
    
    print(set(parking_list))
    if(len(parking_list) == 5):
        if ((len(set(parking_list))==1) and parking_list[0] == True):
            is_empty(parking_id,False, conn)
            print(reserved)
            if not reserved:
                toggle(True, LEDid)
        else:
            is_empty(parking_id,True, conn)
            if not reserved:
                toggle(False, LEDid)
        parking_list=[]

def main(ECHO, TRIG, LEDid, p_id):
    global conn
    global parking_id
    ECHO = int(ECHO)
    TRIG = int(TRIG)
    LEDid = int(LEDid)
    parking_id = p_id
    # initialize output pin (sensor trigger)and
    # input pin (read return signal from sensor)
    sensorIO = {'A1':[24, 23, 4], 'A2':[27, 17, 22]}
    
    try:
        # parse command line arguments (GPIO pin numbers)
        
        
        # set GPIO pin mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # bind GPIO pins
        GPIO.setup(LEDid, GPIO.OUT)
        GPIO.setup(TRIG, GPIO.OUT)
        GPIO.setup(ECHO, GPIO.IN)
        while True:
            # notify user that measurement is in progress
            print ("Distance Measurement In Progress")
            # set trigger to low
            GPIO.output(TRIG, False)
            # give the sensor a moment to settle
            print ("Waiting For Sensor To Settle")
            time.sleep(2)
            
            reserve_listen(conn, LEDid)
            getVacancy(conn, TRIG, ECHO, LEDid)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Measurement stopped by user")
        print(select_all(conn))
        conn.close()
        # reset I/O pins
        GPIO.cleanup()

if __name__ == '__main__' and len(sys.argv) == 5:
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
