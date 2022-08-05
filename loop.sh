#!/bin/bash
export DISPLAY=:0.0
x=1
RIGHT="ls"
LEFT="pwd"

WAIT=$1



take_one() {
  `$LEFT`
  `$RIGHT`
  sleep $WAIT

  if [ "$1" == ""]; then
    `$LEFT`
  else
    if ! (($1 % $2)); then
      `RIGHT`
    else
    `$LEFT`
    fi

  fi
}

take_three() {
  `$LEFT`
  `$LEFT`
  sleep $(( $WAIT * 2 ))
  if [ "$1" == ""]; then
    `$LEFT`
  else
    if ! (($1 % $2)); then
      `RIGHT`
    else
    `$LEFT`
    fi

  fi
}


no_printer() {
  while [ $x -le 300 ]
  do
    take_one
    take_three
    x=$(( $x + 1 ))
  done
}


with_printer() {
  while [ $x -le 300 ]
  do
    take_one $x 10
    take_three $x 10
    x=$(( $x + 1 ))
  done
}

no_printer