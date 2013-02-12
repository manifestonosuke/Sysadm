#!/bin/ksh

PRGDIR=`type $0 | awk '{print $3}'`
PRGNAME=`basename $0`
PRGNAME=`basename $0 |  awk -F '.' '{print $1}'`

function usage {
cat << fin
$PRGNAME [ -f file ] [ -p URL] | URL
Get URL from remote site and display statistics 
        -d      debug mode
	-e	Dont display empty file (file with no contents or 30x)
        -f      URL file to be parsed and output summary for each URL
        -h      This page 
	-p	Just display page content for this URL 
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
wget ${WGETDEFAULT:=""} --tries=1 --max-redirect=1 --domains $DOMAIN --page-requisites -nv $URL 2>&1 | awk -F ' ' '{printf "%s %s\n",$3,$4}' | grep URL | while read a  
do 
	AFTER=$(date +%s)	
	__SIZE=$(echo "$a" | awk '{print $2}' | sed 's/.*\[\([0-9]*\).*/\1/g') 
	__URL=$(echo "$a" | awk '{print $1}' |cut -d / -f 3-) 
	
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
#echo "$URL ::: $NB : $SIZE : $ELAPSED : $MAX : $BIGURL" 
}

FILE=none 
CONTENT=0 
EMPTY=0
# User agent with setting cause pb with blank
WGETDEFAULT='--user-agent=ALSEIS-testing-tool --delete-after' 

while getopts dD:ef:hp: sarg
do
case $sarg in
	D)	DOMAIN=$OPTARG ;;
        d)      set -x
                DEBUG=1 ;;
	e)	EMPTY=1 ;;
        f)      FILE=$OPTARG ;; 
        h)      usage
                end;;
	p)	URL=$OPTARG
		CONTENT=1  ;;
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
	while read line 
	do
		DOMAIN=$(echo $line | cut -d '/' -f 3)
		URL=${line}
		checkurl
	done < $FILE 
else
	if [ ${URL:=empty} == 'empty' ];
	then
		echo "ERROR no URL set"	
		end
	fi
	DOMAIN=$(echo $URL | cut -d '/' -f 3)
	printf "%-40s : %-10s : %-10s : %-10s : %-10s : %-30s\n" "Requested URL" "#elements" "Total size" "Elapsed time" "Biggest obj size"  "biggest component" 
	#checkurl
	wget ${WGETDEFAULT:=""} --domains $DOMAIN --page-requisites -nv $URL 2>&1  | awk -F ' ' '{printf "%s %s\n",$3,$4}' | grep URL | sed 's:.*//\(.*\) \[\(.*\)/.*:\2 \t \1 :'  | sort -n
fi



