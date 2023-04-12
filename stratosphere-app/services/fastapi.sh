#!/bin/bash

# configuration
source /shared/bashrc # setup environment envs
set -e # exit immediately if an error is encountered
set -x # print all commands before execution

uvicorn --reload --host 0.0.0.0 --port 9001 pins_demo.api:app