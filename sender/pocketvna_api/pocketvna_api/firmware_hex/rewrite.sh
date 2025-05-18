#ENTER DFU MODE
set -Eexuo pipefail
if [[ ${1+x} ]]; then 
	./dfu-programmer atxmega32a4u  erase
	./dfu-programmer atxmega32a4u  flash "$1"
	./dfu-programmer atxmega32a4u  reset	
else
	echo "pass *.hex firmware file as 1st argument"
	exit 1	
fi

