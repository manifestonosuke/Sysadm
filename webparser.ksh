#!/bin/bash

PRGDIR=`type $0 | awk '{print $3}'`
PRGNAME=`basename $0`
PRGNAME=`basename $0 |  awk -F '.' '{print $1}'`

function usage {
cat << fin
$PRGNAME [ -f file ] [ -p URL] [-l N] [ -T N] | URL
Get URL from remote site and display statistics 
        -d      debug mode
	-e	Dont display empty file (file with no contents or 30x)
	-l	Loop N time (only valid with an URL file -f parameter) 
        -f      URL file to be parsed and output summary for each URL
        -h      This page 
	-p	Just display page content for this URL
	-T	Add Temporisation on N seconds (N must be integer)
if -f is used URL is ignored 
if URL is used then it will show a summary of all elements of 1 page 
fin
}

function end {
exit
}

function checkurl {
SIZE=0
NB=0
MAX=0
BIGURL="dummy"
export SIZE
export NB
export MAX
export BIGURL
#echo 'Requested URL ::: #elements : Total downloaded size : Elapsed time : Component max size : biggest component' 
NOW=$(date +%s)
wget ${WGETDEFAULT:=""} --tries=1 --max-redirect=1 --domains $DOMAIN --page-requisites -nv $URL 2>&1 | awk -F ' ' '{printf "%s %s\n",$3,$4}' | grep URL | while read element  
do 
	AFTER=$(date +%s)	
	__SIZE=$(echo "$element" | awk '{print $2}' | sed 's/.*\[\([0-9]*\).*/\1/g') 
	__URL=$(echo "$element" | awk '{print $1}' |cut -d / -f 3-) 
	
	NB=$(($NB + 1)) 
	if [ $__SIZE -gt $MAX ];
	then
		MAX=$__SIZE
		BIGURL=$__URL
	fi
	SIZE=$(($SIZE+$__SIZE))
	#echo "$NB :: $SIZE :: $__SIZE :: $BIGURL"
	#echo "$NB Pages for total $SIZE and bigger page is $MAX size ($BIGURL)" 
done
ELAPSED=$(($AFTER - $NOW))
#echo "$URL ::: $NB Pages for total $SIZE in $ELAPSED seconds biggest size $MAX ($BIGURL)" 
if [ ${BIGURL:=dummy} == "dummy" ] ; 
then
	if [ $EMPTY -eq 0 ];
	then
		printf "%-40s : %-10s : %-10s : %-10s : %-10s : %-30s\n" "$URL" "$NB" "$SIZE" "$ELAPSED" "$MAX" "Empty page" 
	fi
else
	printf "%-40s : %-10s : %-10s : %-10s : %-10s : %-30s\n" "$URL" "$NB" "$SIZE" "$ELAPSED" "$MAX" "$BIGURL" 
fi
if [ $TEMP -ne 0 ] ; 
then
	#echo "print sleep $TEMP"
	sleep $TEMP
fi
#echo "$URL ::: $NB : $SIZE : $ELAPSED : $MAX : $BIGURL" 
}

FILE=none 
CONTENT=0 
EMPTY=0
# User agent with setting cause pb with blank
# USERAGENT="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)"
WGETDEFAULT='--user-agent=ALSEIS-testing-tool --delete-after -e robots=off' 
WGETDEFAULT='-U Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0) -l 1 --delete-after -e robots=off' 
LOOP=1
TEMP=0

while getopts dD:ef:hl:p:T: sarg
do
case $sarg in
	D)	DOMAIN=$OPTARG ;;
        d)      set -x
                DEBUG=1 ;;
	e)	EMPTY=1 ;;
        f)      FILE=$OPTARG ;; 
        h)      usage
                end;;
	l)	LOOP=$OPTARG ;;
	p)	URL=$OPTARG
		CONTENT=1  ;;
	T)	TEMP=$OPTARG ;;
        v)      VERBOSE=1 ;;
        *)      echo "ERROR : $PRGNAME : Bad option or misusage"
                usage
                end ;;
esac
done

shift $(($OPTIND - 1))

if [ $CONTENT == 1 ] ; 
then
	curl -s  $URL
	end
fi

if [ $# -ne 0 ];
then
	URL=$1 
fi
# if $OPTIND is empty then there is no url to parse and we should use file



if [ ${FILE:=none} != 'none'  ];
then
	if [ ! -f $FILE ];
	then
		echo "$FILE file not found"
		exit
	fi
	printf "%-40s : %-10s : %-10s : %-10s : %-10s : %-30s\n" "Requested URL" "#elements" "Total size" "Elapsed time" "Biggest obj size"  "biggest component" 	
	if [ $LOOP -lt 1 ];
	then
		echo "ERROR : loop argument is too small"
		exit
	fi
	for THISLOOP in $(seq 1 $LOOP);
	do
		while read line 
		do
			DOMAIN=$(echo $line | cut -d '/' -f 3)
			URL=${line}	
			checkurl
		done < $FILE 
	done
else
	if [ ${URL:=empty} == 'empty' ];
	then
		echo "ERROR no URL set"	
		end
	fi
	DOMAIN=$(echo $URL | cut -d '/' -f 3)
	printf "%-40s : %-10s : %-10s : %-10s : %-10s : %-30s\n" "Requested URL" "#elements" "Total size" "Elapsed time" "Biggest obj size"  "biggest component" 
	#checkurl
	#wget ${WGETDEFAULT:=""} --domains $DOMAIN --page-requisites -nv $URL 2>&1  | awk -F ' ' '{printf "%s %s\n",$3,$4}' | grep URL | sed 's:.*//\(.*\) \[\(.*\)/.*:\2 \t \1 :'  | sort -n	
	# Change pattern to match the first number in bracket (which is the size of total)
	SUM=0
	wget ${WGETDEFAULT:=""} --domains $DOMAIN --page-requisites -nv $URL 2>&1  | awk -F ' ' '{printf "%s %s\n",$3,$4}' | grep URL | sed 's:.*//\(.*\) \[\([0-9]*\).*:\2 \t \1 :'  | sort -n \
	|while read line ;
	do
		I=$(echo $line | awk '{print $1}')
		SUM=$(($I + $SUM))
		echo "$line"
	done
	printf "%-40s : %-10s \n" "Total page size is : $SUM"
fi



