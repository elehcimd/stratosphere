#!/bin/bash

# configuration
source /shared/bashrc # setup environment envs
set -e # exit immediately if an error is encountered
set -x # print all commands before execution

# kill also childs on exit
trap "kill -- -$$" EXIT

# Cull idle kernels: https://voila.readthedocs.io/en/stable/customize.html#cull-idle-kernels

jupyter lab \
    --VoilaConfiguration.enable_nbextensions=True \
    --VoilaConfiguration.file_whitelist "['.*']" \
    --MappingKernelManager.cull_interval=60 \
    --MappingKernelManager.cull_idle_timeout=120 \
    --VoilaExecutor.timeout=30 \
    --VoilaConfiguration.show_tracebacks=True
#--debug
