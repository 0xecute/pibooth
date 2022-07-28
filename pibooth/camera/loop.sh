#!/bin/bash
export DISPLAY=:0.0
x=1
RIGHT="xdotool mousemove 600 100 click 1"
LEFT="xdotool mousemove 100 100 click 1"
while [ $x -le 5 ]
do
  `$RIGHT`
  `$RIGHT`
  sleep 20
  `$LEFT`
  x=$(( $x + 1 ))
done