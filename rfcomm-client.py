from bluetooth import *

server_address = "5C:F3:70:84:AC:78"
port = 1

sock = BluetoothSocket(RFCOMM)
sock.connect((server_address, port))

sock.send("hello!" * 10)

sock.close()
