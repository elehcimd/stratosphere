#!/bin/bash

# configuration
source /shared/bashrc # setup environment envs
set -e # exit immediately if an error is encountered
set -x # print all commands before execution

python -m http.server 3000

# install required packages
#npm install

# in some cases, the nextjs cache breakes. let's make sure we start from a clean state.
#rm -rf .next ./next-env.d.ts

#cd /shared/web
# start nextjs (demo app)
#PORT=3000 npm run dev
#PORT=3000 npm run start
