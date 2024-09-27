#!/bin/bash
#
# one of two shell scripts for scout UAV launch
# prepare video folders
# launch gstreamer by collecting video streams from gimbals
FRAME_RATE=10
STREAM_FRAME_RATE=5
PX4_VIDEO="/home/akim/px4_video"
PX4_VIDEO_backup="/home/akim/px4_video_backup"

#create px4_video directoy if missing
echo "check $PX4_VIDEO directory"
if [ -d "$PX4_VIDEO" ]; then
  echo "$PX4_VIDEO directory exist"
  echo "move existing $PX4_VIDEO directory as $PX4_VIDEO_backup"
  mv "$PX4_VIDEO" "$PX4_VIDEO_backup"
  mkdir "$PX4_VIDEO"
else
  echo "$PX4_VIDEO directory does not exist"
  echo "create $PX4_VIDEO directory"
  mkdir "$PX4_VIDEO"
fi

#echo stream setup
echo "launch gstreamer"
echo "Camera frame rate: $FRAME_RATE"
echo "Stream frame rate: $STREAM_FRAME_RATE"
echo "-----------------------"

#start gstreamer
#collect videos from gimbal1 (192.168.144.25) and gimbal2 (192.168.144.26)
#save frames with index number to folders
#scale down frames and merge into a single image using tee
#send the merged image to ground control station (192.168.144.10) through UDP
gst-launch-1.0 \
    uridecodebin uri=rtsp://192.168.144.25:8554/main.264 source::latency=0 \
  ! tee name=t0_camera1 \
  ! nvvidconv \
  ! videorate \
  ! "video/x-raw(memory:NVMM),framerate=$FRAME_RATE/1" \
  ! nvvidconv \
  ! nvjpegenc \
  ! multifilesink location=~/px4_video/camera1_%d.jpg \
    uridecodebin uri=rtsp://192.168.144.26:8554/main.264 source::latency=0 \
  ! tee name=t0_camera2 \
  ! nvvidconv \
  ! videorate \
  ! "video/x-raw(memory:NVMM),framerate=$FRAME_RATE/1" \
  ! nvvidconv \
  ! nvjpegenc \
  ! multifilesink location=~/px4_video/camera2_%d.jpg \
    t0_camera1. \
  ! nvvidconv \
  ! 'video/x-raw(memory:NVMM),width=960,height=540,format=RGBA' \
  ! queue ! comp. \
    t0_camera2. \
  ! nvvidconv \
  ! 'video/x-raw(memory:NVMM),width=960,height=540,format=RGBA' \
  ! queue ! comp. \
    nvcompositor name=comp \
    sink_0::xpos=0 sink_0::ypos=0   sink_0::width=960 sink_0::height=540 \
    sink_1::xpos=0 sink_1::ypos=540 sink_1::width=960 sink_1::height=540 \
  ! nvvidconv \
  ! "video/x-raw(memory:NVMM),format=NV12" \
  ! videorate \
  ! "video/x-raw(memory:NVMM),framerate=$STREAM_FRAME_RATE/1" \
  ! nvvidconv \
  ! nvjpegenc \
  ! rtpjpegpay \
  ! udpsink host=192.168.144.10 port=5010 