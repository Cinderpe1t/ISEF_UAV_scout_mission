# ISEF 2024 ETSD037 Scout UAV Codes
Codes for scout mission at scout UAV and ground control station.
## Scout UAV codes
- `crc_generate.py`: Generate CRC codes for gimbal camera UDP communication
- `gimbal_control_udp.py`: Set gimbal camera mode and orientation for ocean data collection
- `mavlink.log`: output of `px4_gps_timestamp.py` from a scout mission
- `px4_gps_timestamp.py`: Establish MAVLink with PX4, request telemtry data, collect messages, add GPS coordinates and time stamp corresponding to images at log file
- `run_gstreamer.sh`: Set directory for image data, set gstreamer, collect images from two cameras and save to folder, merge two images and send to ground control station
- `run_python.sh`: Run `gimbal_control_udp.py` and `px4_gps_timestamp.py`
## Ground control station codes
- `px4_start_gstreamer_sink.sh`: gstreamer sink for video feed display at ground control station
## Operation
- Ground control station laptop connects to mission controller through IP network. Either ssh or vnc will work.
- `run_gstreamer.sh` and `run_python.sh` are two command line programs to run separately.
- `px4_gps_timestamp.py` will wait for PX4 heart beat and image data from gstreamer.
## Scout sample image
![sample image](https://github.com/Cinderpe1t/ISEF_UAV_scout_mission/blob/main/gimbal0_1700.jpg)
## mavlink.log sample
```
2023-12-24 13:58:16.217227	Initiate mavlink
2023-12-24 13:58:16.256445	/dev/ttyTHS1, baud=115200
2023-12-24 13:58:16.256542	Wait for MAVlink connection
2023-12-24 13:58:16.257003	None for ping count: 1
2023-12-24 13:58:16.762404	PING {time_usec : 1703455096256590, seq : 0, target_system : 255, target_component : 0} for ping count: 2
2023-12-24 13:58:17.263432	Wait for heart beat
2023-12-24 13:58:17.267906	Heartbeat: (system 1 component 0)
2023-12-24 13:58:17.267973	Request messages
2023-12-24 13:58:17.308791	1-second stand by
2023-12-24 13:58:18.359545	UTM data returned 0	[329615610, -1172683911, -36957, 0, 0, -1, 0.0, 0.00840712245553732, 211, 0, -2.3139562606811523, 0.01829640194773674]
2023-12-24 13:58:19.361206	wait for image files to show up
2023-12-24 13:58:19.368698	image file(s) detected
2023-12-24 13:58:19.374103	camera0 images: 56, gimbal0 images: 56
2023-12-24 13:58:19.430728	camera0_55.jpg	55	[329615609, -1172683909, -36970, 0, 0, -2, 0.0, 0.005494401324540377, 211, 0, -2.347041606903076, 0.02051376923918724]
2023-12-24 13:58:19.430868	gimbal0_55.jpg	55	[329615609, -1172683909, -36970, 0, 0, -2, 0.0, 0.005494401324540377, 211, 0, -2.347041606903076, 0.02051376923918724]
2023-12-24 13:58:19.456013	camera0 images: 57, gimbal0 images: 56
2023-12-24 13:58:19.458361	camera0_56.jpg	56	[329615609, -1172683909, -36972, 0, 0, -2, 0.0, 0.005494401324540377, 211, 0, -2.347041606903076, 0.02051376923918724]
2023-12-24 13:58:19.486036	camera0 images: 57, gimbal0 images: 56
2023-12-24 13:58:19.520427	camera0 images: 58, gimbal0 images: 56
2023-12-24 13:58:19.527554	camera0_57.jpg	57	[329615609, -1172683909, -36972, 0, 0, -2, 0.0, 0.005254873540252447, 211, 0, -2.347592830657959, 0.020625337958335876]
2023-12-24 13:58:19.555626	camera0 images: 58, gimbal0 images: 56
```
