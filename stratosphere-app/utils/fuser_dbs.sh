#!/bin/bash

# configuration
source /shared/bashrc # setup environment envs

# kill also childs on exit
trap "kill -- -$$" EXIT

while true
do
    for pathname in /shared/data/probe.db /shared/data/kb.db
    do
        pids=$(fuser $pathname 2>&1 | grep : | cut -f2- -d:)
        if [ ! -z "$pids" ]
        then
            echo "=== $(date +"%H:%M:%S") $pathname ==="
            first="true"
            for pid in $pids
                do
                    if [ $first = "true" ]
                    then
                        ps aux -q $pid
                    else
                        ps aux -q $pid | grep -v PID
                    fi
                    first="false"
                done
            echo ""
        fi
    done
    sleep .5

done