#!/bin/bash

filename=$1
while read -r command; do
    source test/test_runner.sh "$command"
    if [[ $? -ne 0 ]]; then
        source test/red_fail.sh
        return $?
    fi
done < ${filename}

source test/green_pass.sh
