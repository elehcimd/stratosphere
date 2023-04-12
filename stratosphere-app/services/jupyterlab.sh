#!/bin/bash

# configuration
source /shared/bashrc # setup environment envs
set -e # exit immediately if an error is encountered
set -x # print all commands before execution

# kill also childs on exit
trap "kill -- -$$" EXIT

jupyter lab --VoilaConfiguration.enable_nbextensions=True --VoilaConfiguration.file_whitelist "['.*']"
#--debug
