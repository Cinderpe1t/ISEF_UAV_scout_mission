from pymavlink import mavutil 
import time, sys
import threading 
import math 
import os 
import glob
import re
import numpy as np
import datetime

frame_rate=10

#append message to log file
def print_write_log(log_msg):
    now=datetime.datetime.now()
    log_str=str(now)+"\t"+log_msg
    print(log_str)
    log_str+="\n"
    f.write(log_str)

#wait for MAVLink connection
def wait_conn():
    """
    Sends a ping to stabilish the UDP communication and awaits for a response
    """
    ping_count=1
    msg = None
    while not msg:
        master.mav.ping_send(
            int(time.time() * 1e6), # Unix time in microseconds
            0, # Ping number
            0, # Request ping of all systems
            0 # Request ping of all components
        )
        msg = master.recv_match()

        now=datetime.datetime.now()
        log_msg=str(now)+"\t"+str(msg)+" for ping count: "+str(ping_count)
        print(log_msg)
        log_msg+="\n"
        f.write(log_msg)

        ping_count+=1
        time.sleep(0.5)

#Request MAVLink telemetry data update to PX4
def request_message_interval(message_id: int, frequency_hz: float): 
    message = master.mav.command_long_encode(
        master.target_system, master.target_component, 
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0, 
        message_id, # The MAVLink message ID 
        1e6 / frequency_hz, # The interval between two messages in microseconds. Set to -1 to disable and 0 to request default rate. 
        0, 0, 0, 0, # Unused parameters 
        0, # Target address of message stream (if message has target address fields). 0: Flight-stack default (recommended), 1: address of requestor, 2: broadcast. 
    ) 
    master.mav.send(message)
    # Wait for a response (blocking) to the MAV_CMD_SET_MESSAGE_INTERVAL command and print result 
    response = master.recv_match(type='COMMAND_ACK', blocking=True) 
    if response and response.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL and response.result == mavutil.mavlink.MAV_RESULT_ACCEPTED: 
        print("Command accepted") 
    else: 
        print("Command failed") 

#Request GPS and flight data messages
def request_message(): 
    request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_UTM_GLOBAL_POSITION, 20) #340 
    request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD, 20) #74
    #request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_OPEN_DRONE_ID_BASIC_ID, 1) #12900
    #request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_OPEN_DRONE_ID_LOCATION, 1) #12901

#Collect telemetry data
def get_telemetry_data(): 
    ack_msg = master.recv_match(type='COMMAND_ACK') 
    observation=[] 
    t_param='UTM_GLOBAL_POSITION' #340 
    try:  
        UTM_GLOBAL_POSITION_lat = master.messages[t_param].lat
        UTM_GLOBAL_POSITION_lon = master.messages[t_param].lon
        UTM_GLOBAL_POSITION_alt = master.messages[t_param].alt
        UTM_GLOBAL_POSITION_vx = master.messages[t_param].vx
        UTM_GLOBAL_POSITION_vy = master.messages[t_param].vy
        UTM_GLOBAL_POSITION_vz = master.messages[t_param].vz
        UTM_GLOBAL_POSITION_data=[UTM_GLOBAL_POSITION_lat,UTM_GLOBAL_POSITION_lon,UTM_GLOBAL_POSITION_alt,
                                  UTM_GLOBAL_POSITION_vx,UTM_GLOBAL_POSITION_vy,UTM_GLOBAL_POSITION_vz]
        observation.extend(UTM_GLOBAL_POSITION_data) #count=45+3=48 
    except: 
        #print(t_param, ":", 'No message received')
        print_write_log(t_param+":"+'No message received')

    t_param='VFR_HUD' #74
    try: 
        VFR_HUD_airspeed = master.messages[t_param].airspeed
        VFR_HUD_groundspeed = master.messages[t_param].groundspeed
        VFR_HUD_heading = master.messages[t_param].heading
        VFR_HUD_throttle = master.messages[t_param].throttle
        VFR_HUD_alt = master.messages[t_param].alt
        VFR_HUD_climb = master.messages[t_param].climb
        VFR_HUD_data=[VFR_HUD_airspeed,VFR_HUD_groundspeed,VFR_HUD_heading,VFR_HUD_throttle,VFR_HUD_alt,VFR_HUD_climb]
        observation.extend(VFR_HUD_data) #count=29+4=33
    except:
        #print(t_param, ":", 'No message received')
        print_write_log(t_param+":"+'No message received')
    return observation 

#Get Open Drone ID's
def get_open_drone_id(): 
    ack_msg = master.recv_match(type='COMMAND_ACK') 
    t_param='OPEN_DRONE_ID_BASIC_ID' #340 
    try:  
        OPEN_DRONE_ID_BASIC_ID_id_or_mac = master.messages[t_param].id_or_mac
        OPEN_DRONE_ID_BASIC_ID_uas_id = master.messages[t_param].uas_id
        print("OPEN_DRONE_ID_BASIC_ID_id_or_mac: ", OPEN_DRONE_ID_BASIC_ID_id_or_mac)
        print("OPEN_DRONE_ID_BASIC_ID_uas_id: ", OPEN_DRONE_ID_BASIC_ID_uas_id)
    except: 
        print(t_param, ":", 'No message received') 
    t_param='OPEN_DRONE_ID_LOCATION' #340 
    try:  
        OPEN_DRONE_ID_LOCATION_id_or_mac = master.messages[t_param].id_or_mac
        print("OPEN_DRONE_ID_LOCATION_id_or_mac: ", OPEN_DRONE_ID_LOCATION_id_or_mac)
    except: 
        print(t_param, ":", 'No message received') 

#Start main
#Open log file
f = open('/home/akim/px4_video/mavlink.log','w')
boot_time = time.time() 
print_write_log("Initiate mavlink")

#MAVLink through UART or UDP
master = mavutil.mavlink_connection("/dev/ttyTHS1", baud=115200)
#master = mavutil.mavlink_connection("udpout:192.168.144.19:14540")
print_write_log("/dev/ttyTHS1, baud=115200")

#Wait for MAVLink connection
print_write_log("Wait for MAVlink connection")
wait_conn()

#Wait for heartbeat from PX4
print_write_log("Wait for heart beat")
master.wait_heartbeat() 

#Heart beat was received
log_msg="Heartbeat: (system %u component %u)" % (master.target_system, master.target_component)
print_write_log(log_msg)

#Request MAVLink telementry data
print_write_log("Request messages")
request_message()

log_msg="1-second stand by"
print_write_log(log_msg)

time.sleep(1)

#Repeat request as needed
observation=[]
count=0
while len(observation)==0:
    observation=get_telemetry_data()
    print_write_log("UTM data returned "+str(count)+"\t"+str(observation))
    time.sleep(1)
    count=count+1
    if count>10:
        print_write_log("Request messages again") 
        request_message()
        count=0

#camara output file counting setup
camera1_prefix='camera1_'
camera2_prefix='camera2_'

count_camera1_files=0
count_camera2_files=0
len_camera1_files=0
len_camera2_files=0

root_path='/home/akim/px4_video/'
#dirFiles=os.listdir('/home/akim/px4_video/')

#wait for first image files to show up at the folder
print_write_log("wait for image files to show up") 
while len_camera1_files == 0 and  len_camera2_files == 0:
    camera1_files=glob.glob(root_path+camera1_prefix+'*.jpg')
    camera1_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    len_camera1_files=len(camera1_files)

    camera2_files=glob.glob(root_path+camera2_prefix+'*.jpg')
    camera2_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    len_camera2_files=len(camera2_files)

print_write_log("image file(s) detected") 

#Write GPS and timestamp when a new image shows up
while True:
    #count files from each camera
    camera1_files=glob.glob(root_path+camera1_prefix+'*.jpg')
    camera1_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    len_camera1_files=len(camera1_files)

    camera2_files=glob.glob(root_path+camera2_prefix+'*.jpg')
    camera2_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    len_camera2_files=len(camera2_files)

    #report current status
    print_write_log("camera1 images: "+str(len_camera1_files)+", camera2 images: "+str(len_camera2_files)) 

    #refresh telemetry data
    TELEM_data=get_telemetry_data()
    
    #camera1 - new files to add tag
    if count_camera1_files < len_camera1_files:
        filepath=camera1_files[len_camera1_files-1]
        filename_full=filepath[len(root_path):len(filepath)] 
        filename=filepath[len(root_path)+len(camera1_prefix):len(filepath)] # remove root path from file name
        fileidx=re.sub('\D','', filename)
        data_to_write=filename_full+"\t"+fileidx+"\t"+str(TELEM_data)
        print_write_log(data_to_write)
        count_camera1_files = len_camera1_files

    #camera2 - new files to add tag
    if count_camera2_files < len_camera2_files:
        filepath=camera2_files[len_camera2_files-1]
        filename_full=filepath[len(root_path):len(filepath)] 
        filename=filepath[len(root_path)+len(camera2_prefix):len(filepath)] # remove root path from file name
        fileidx=re.sub('\D','', filename)
        data_to_write=filename_full+"\t"+fileidx+"\t"+str(TELEM_data)
        print_write_log(data_to_write)
        count_camera2_files = len_camera2_files
    time.sleep(0.1/frame_rate)
