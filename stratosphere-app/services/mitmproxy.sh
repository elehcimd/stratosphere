#!/bin/bash

# configuration
source /shared/bashrc # setup environment envs
set -e # exit immediately if an error is encountered
set -x # print all commands before execution

# kill also childs on exit
trap "kill -- -$$" EXIT

# If switching to mitmweb:
# --no-web-open-browser --web-host '*'

# --set validate_inbound_headers=false : 
# Required to avoid some HTTP/2 errors, happening on https://www.nginx.com/ and some other websites
# https://github.com/mitmproxy/mitmproxy/issues/4836

mitmdump --set validate_inbound_headers=false --set confdir=/shared/mitmproxy_confdir   --scripts /shared/src/stratosphere/mitmproxy/probe.py

