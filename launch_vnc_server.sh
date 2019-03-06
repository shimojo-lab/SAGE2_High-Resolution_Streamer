#!/bin/bash

path=$(cat ./config.json | jq -r .vnc.path)
display=$(cat ./config.json | jq .vnc.number)
width=$(cat ./config.json | jq .vnc.width)
height=$(cat ./config.json | jq .vnc.height)
depth=$(cat ./config.json | jq .vnc.depth)

eval '${path} -kill :${display}'
eval '${path} -geometry ${width}x${height} -depth ${depth} :${display}'

