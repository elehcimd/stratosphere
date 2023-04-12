#!/bin/bash

# configuration
source /shared/bashrc # setup environment envs
set -e # exit immediately if an error is encountered
set -x # print all commands before execution

# kill also childs on exit
trap "kill -- -$$" EXIT

# --no-web-open-browser --web-host '*'
mitmdump --set confdir=/shared/mitmproxy_confdir   --scripts /shared/src/stratosphere/mitmproxy/probe.py
# --intercept "~ts .*html.*" 