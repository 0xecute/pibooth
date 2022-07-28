#!/bin/bash
export DISPLAY=:0.0
x=1
RIGHT="xdotool mousemove 600 100 click 1"
LEFT="xdotool mousemove 100 100 click 1"

WAIT=$1



take_one() {
  `$LEFT`
  `$RIGHT`
  sleep $WAIT
  `$LEFT`
}

take_three() {
  `$LEFT`
  `$LEFT`
  sleep $(( $WAIT * 3 ))
  `$LEFT`
}



while [ $x -le 100 ]
do
  take_one
  take_three
  x=$(( $x + 1 ))
done
