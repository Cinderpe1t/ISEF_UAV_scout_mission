# ISEF 2024 ETSD037 Scout UAV Codes
## List of codes
- `crc_generate.py`: Generate CRC codes for gimbal camera UDP communication
- `gimbal_control_udp.py`: Set gimbal camera mode and orientation for ocean data collection
- `px4_gps_timestamp.py`: Establish MAVLink with PX4, request telemtry data, collect messages, add GPS coordinates and time stamp corresponding to images at log file
- `run_gstreamer.sh`: Set directory for image data, set gstreamer, collect images from two cameras and save to folder, merge two images and send to ground control station
- `run_python.sh`: Run `gimbal_control_udp.py` and `px4_gps_timestamp.py`
## Operation
- Ground control station laptop connects to mission controller through IP network. Either ssh or vnc will work.
- `run_gstreamer.sh` and `run_python.sh` are two command line programs to run separately.
- `px4_gps_timestamp.py` will wait for PX4 heart beat and image data from gstreamer.
