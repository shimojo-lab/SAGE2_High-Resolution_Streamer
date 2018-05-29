#!/bin/bash

display=$(cat ../config.json | jq .display)
width=$(cat ../config.json | jq .width)
height=$(cat ../config.json | jq .height)
quality=$(cat ../config.json | jq .quality)

ffmpeg -f x11grab \
-video_size ${width}x${height} \
-i :${display} \
-f image2pipe \
-pix_fmt rgb32 -vcodec rawvideo \
- 

