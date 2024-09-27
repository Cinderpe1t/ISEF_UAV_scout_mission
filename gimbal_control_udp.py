#Set caemra mode and fixed angles through UDP
#TBD: Camera angles can be adapted based on the UAV's pitch angle
import socket, sys

#Set camera IP addresses and UDP ports
Camera1_IP='192.168.144.25'
Camera2_IP='192.168.144.26'
Camera_UDP_Port=37260

#Create a UDP socket
Socket_Camera1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
Socket_Camera2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Bind the socket to the port
Camera1_Address = (Camera1_IP, Camera_UDP_Port)
Camera2_Address = (Camera2_IP, Camera_UDP_Port)
print("Camera1 IP address and port: ", Camera1_Address)
print("Camera2 IP address and port: ", Camera2_Address)

#Set camera1 0 degree pitch including cdc code
UDP_MESSAGE = bytes.fromhex("55 66 01 04 00 00 00 0e 00 00 00 00 e8 c7")
print("Data to camera1 : ", UDP_MESSAGE)
Socket_Camera1.sendto(UDP_MESSAGE, Camera1_Address) #Send message to UDP port

#Receive confirmation data from camera1
data, address = Socket_Camera1.recvfrom(Camera_UDP_Port)
print("Data from camera1 : ", data, address)

#Set camera2 -90 degree pitch including cdc code
UDP_MESSAGE = bytes.fromhex("55 66 01 04 00 00 00 0e 00 00 7c fc 4f a4")
print("Data to camera2 : ", UDP_MESSAGE)
Socket_Camera2.sendto(UDP_MESSAGE, Camera2_Address) #Send message to UDP port

#Receive confirmation data from camera2
data, address = Socket_Camera2.recvfrom(Camera_UDP_Port)
print("Data from camera2 : ", data, address)

#Set fixed angle modes at both cameras
UDP_MESSAGE = bytes.fromhex("55 66 01 01 00 00 00 0c 05 91 9e") #FPV mode
print("Data to camera  : ", UDP_MESSAGE)
Socket_Camera1.sendto(UDP_MESSAGE, Camera1_Address) #Send message to UDP port
Socket_Camera2.sendto(UDP_MESSAGE, Camera2_Address) #Send message to UDP port
#There is no ack from A8 by defition

#Close sockets
Socket_Camera1.close()
Socket_Camera2.close()