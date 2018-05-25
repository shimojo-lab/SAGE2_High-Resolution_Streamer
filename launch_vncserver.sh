#!/bin/bash
## run_vncserver.sh (VNCサーバ起動用スクリプト)

# 設定ファイルをパース
path=$(cat ./config.json | jq -r .vnc_path)
display=$(cat ./config.json | jq .display)
width=$(cat ./config.json | jq .width)
height=$(cat ./config.json | jq .height)
depth=$(cat ./config.json | jq .depth)

# VNCサーバを起動
eval '${path} -kill :${display}'
eval '${path} -geometry ${width}x${height} -depth ${depth} :${display}'

