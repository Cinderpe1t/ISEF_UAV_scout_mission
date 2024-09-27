# one of two shell scripts for scout UAV launch
# execute python codes in sequence
# set gimbal modes and orientation
python3 ./gimbal_control_udp.py
#start adding GPS tag and time stamps to images
python3 ./px4_gps_timestamp.py
