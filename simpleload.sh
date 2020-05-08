#!/bin/bash


SIZE=10
COUNT=0 # endless
NAME=file
DEL=0 
SLEEP=1

function usage() {
cat << fin
$0 [-s SIZE] [-c COUNT] [-n name] [ -r ]
-c :Count of dd to do
-s : Size (in MB) to dd 
-r : Loop after count is reached remove all files staring with file name and loop again (ctrl c to quit)
-n : name of the file to create
File are created on current directory

if count is not set it will loop and not delete 
if count is set it will stop after count 
if count and loop are set, it create count files, delete them and loop again 

script sleep 1 second between each dd

fin
}


while getopts c:dhn:rs: sarg
do
case $sarg in
  c)  COUNT=$OPTARG ;;
  d)  set -x
      DEBUG=1 ;;
  h)  usage
      exit ;;
  n)  NAME=$OPTARG ;;
  r)  DEL=1 ;;
  s)  SIZE=$OPTARG ;;
  *)  echo "ERROR : Bad option or misusage"
      usage
      exit ;;
esac
done

shift $(($OPTIND - 1))

NB=0
while true;
do
  D=$(date '+%m%d-%H%M%S')
  #echo $COUNT $NB
  if [ ${COUNT} -ne 0 ];
  then
    if [ $NB -ge ${COUNT} ];
    then
      echo "Count file processed ending at $D"
      break
    fi
  fi
  dd if=/dev/urandom of=${NAME}-${D} count=$SIZE bs=1M 2>&1 | grep -v records
  NB=$((NB + 1))
  sleep $SLEEP
  if [ $DEL -eq  1 ];
  then 
    if [ $NB -eq $COUNT ];
    then
      echo "Count reached, deleting files"
      \rm ${NAME}*
      NB=0
    fi
  fi
done

 
 

