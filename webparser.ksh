#!/bin/ksh

PRGDIR=`type $0 | awk '{print $3}'`
PRGNAME=`basename $0`
PRGNAME=`basename $0 |  awk -F '.' '{print $1}'`

function usage {
cat << fin
$PRGNAME [ -f file ] [ -p URL] [-l N] | URL
Get URL from remote site and display statistics 
        -d      debug mode
	-e	Dont display empty file (file with no contents or 30x)
	-l	Loop N time (only valid with an URL file -f parameter) 
	-F	Force to download fonts and other usually stored in the browser files  (by default do not load $FONTS files)
        -f      URL file to be parsed and output summary for each URL
        -h      This page 
	-p	Just display page content for this URL
	-X	exclude proxy settings
if -f is used URL is ignored 
if URL is used then it will show a summary of all elements of 1 page 
fin
}

__print() {
if [ ${PRGNAME:=NULL} == "NULL" ] ;
then
        echo "ERROR __print function exiting"
        exit 99
fi
__label=$1
shift
if [ ${SILENT:=0} -ne 1 ];
then
        printf "%-10s %-10s %-22s %-30s \n" "$PRGNAME : " "$__label : " "$*"
        #echo $*
fi
}

amiroot() {
CMD=/usr/bin/whoami
if [ ! -x $CMD ];
then
        __print "ERROR" "cant get root status"
        end 2
else
        __DUM=$(/usr/bin/whoami)
        if [ ${__DUM:=NULL} == "root" ];
        then
                __print "INFO"  "You are root, continue"
        else
                __print "ERROR"  "Need to be root to run this"
                end 2
        fi
fi
}


function end {
OUT=""
[[ $# -ne 0 ]] && OUT=$#
exit $OUT
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
done
ELAPSED=$(($AFTER - $NOW))
if [ ${BIGURL:=dummy} == "dummy" ] ; 
then
	if [ $EMPTY -eq 0 ];
	then
		printf "%-40s : %-10s : %-10s : %-10s : %-10s : %-30s\n" "$URL" "$NB" "$SIZE" "$ELAPSED" "$MAX" "Empty page" 
	fi
else
	printf "%-40s : %-10s : %-10s : %-10s : %-10s : %-30s\n" "$URL" "$NB" "$SIZE" "$ELAPSED" "$MAX" "$BIGURL" 
fi
}

FILE=none 
CONTENT=0 
EMPTY=0
LOOP=1
FONTS="eot,ttf,woff,svg"
XPROXY=0

while getopts dD:ef:Fhl:p:X sarg
do
case $sarg in
	D)	DOMAIN=$OPTARG ;;
        d)      set -x
                DEBUG=1 ;;
	e)	EMPTY=1 ;;
        f)      FILE=$OPTARG ;; 
        h)      usage
                end;;
	F)	FONTS="" ;;
	l)	LOOP=$OPTARG ;;
	p)	URL=$OPTARG
		CONTENT=1  ;;
        v)      VERBOSE=1 ;;
	X)	XPROXY=1 ;;
        *)      echo "ERROR : $PRGNAME : Bad option or misusage"
                usage
                end ;;
esac
done

shift $(($OPTIND - 1))

env | grep -i http_proxy > /dev/null 2>&1 
if [[ $? -eq 0 && XPROXY -eq 0 ]] ; 
then
	__print "WARNING" "$PRGNAME" "Proxy is set"
fi


# User agent with setting cause pb with blank
# USERAGENT="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)"
WGETREJECT="-R $FONTS"
WGETDEFAULT='--user-agent=ALSEIS-testing-tool --delete-after -e robots=off' 
WGETDEFAULT='-U Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0) -l 1 --delete-after -e robots=off' 
if [ ! ${FONTS:=NULL} == "NULL" ]; 
then
	WGETDEFAULT="$WGETDEFAULT $WGETREJECT"
fi

[[ $XPROXY -eq 1 ]] && WGETDEFAULT="$WGETDEFAULT --no-proxy"

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
		__print "ERROR" "$FILE file not found"
		end 1
	fi
	printf "%-40s : %-10s : %-10s : %-10s : %-10s : %-30s\n" "Requested URL" "#elements" "Total size" "Elapsed time" "Biggest obj size"  "biggest component" 	
	if [ $LOOP -lt 1 ];
	then
		__print "ERROR" "loop argument is too small"
		end 1 
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
		__print  "ERROR" "no URL set"	
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
	__print "INFO" "Total page size is $SUM"
fi
