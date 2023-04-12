#!/bin/bash

# configuration
source /shared/bashrc # setup environment envs
set -e # exit immediately if an error is encountered
set -x # print all commands before execution

# kill also childs on exit
trap "kill -- -$$" EXIT

sqlite_web --host 0.0.0.0 --port 8100 --url-prefix /sqlite /shared/data/kb.db

