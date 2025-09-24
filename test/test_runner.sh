#!/bin/bash

BOLD='\033[1m'
NORMAL='\033[0m'

command=$1
echo " "
echo -e ${BOLD}$command${NORMAL}
echo "*** Start"
eval "$command"
if [[ $? -eq 0 ]]; then
    echo "*** End"
    echo " "
    echo "PASS: " $command
    return 0
else
    echo "*** End"
    echo " "
    echo "FAIL: " $command
    return 1
fi
