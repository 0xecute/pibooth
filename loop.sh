#!/bin/bash
export DISPLAY=:0.0
x=1
RIGHT="xdotool mousemove 600 100 click 1; sleep 1"
LEFT="xdotool mousemove 100 100 click 1; sleep 1"

WAIT=$1



take_one() {
  echo "1 picture..."
  `$LEFT`
  `$RIGHT`
   sleep $WAIT

}

take_three() {
  echo "3 pictures..."
  `$LEFT`
  `$LEFT`
  sleep $(( $WAIT * 3 ))
}

after_print() {
  if [[ -z "$1" ]]; then
    echo "No printer..."
    `$LEFT`
  else
    echo "Printing"
    if ! (($1 % $2)); then
      echo "Really printing..."
      `$RIGHT`
      `$RIGHT`
      `$RIGHT`
      sleep 20
      if ! (($1 % ($2*2))); then
        echo "Doing extra printing..."
        `$RIGHT`
        `$RIGHT`
        `$RIGHT`
        `$RIGHT`
        sleep 20
      else
        `$LEFT`
      fi
    else
      `$LEFT`
    fi
  fi
}


no_printer() {
  while [ $x -le 300 ]
  do
    take_one
    after_print
    take_three
    after_print
    x=$(( $x + 1 ))
  done
}


with_printer() {
  while [ $x -le 300 ]
  do
    take_one
    after_print  $x 6
    take_three
    after_print  $x 6
    x=$(( $x + 1 ))
  done
}

with_printer