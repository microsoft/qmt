#!/bin/bash

# ADAPT THE CONFIGURATION VARIABLES BELOW TO YOUR USE CASE! You will at least
# need to change the absolute path to this script.

# invoke as follows:
# 1) For an interactive session, run:
# docker_python.sh --int
# 2) For a bash shell in the same environment where python would run, do
# docker_python.sh --bash
# 3) To run a non-interactive Python execution:
# docker_python.sh whatever.py <...>
# In all cases, if all goes well, it will be executed in the directory where the
# shell script is invoked.

# To get a jupyter notebook, you can in principle run
# docker_python.sh --jupyter
# However, that has some odd behavior, so I recommend doing a docker_python.sh --bash
# and then, in that bash, running (say)
# source activate py36
# jupyter notebook --port=$JUPYTER_PORT --ip=0.0.0.0 --no-browser

## -- BEGIN CONFIGURATION --

# This is the absolute path to this script - you will need to change it!
# This could in principle be inferred, but that might be unsafe with symlinks.
export DOCKER_PYTHON_SCRIPT=/Users/MYNAME/docker_python.sh

# These options can be left as they are if you just want to run the latest QMT.
# The latest docker image:
export DOCKER_IMAGE=johnkgamble/qmt_base:latest
# The path (in the docker container) to the correct python distribution.:
export CMD=/usr/local/envs/py36/bin/python
# replace this with NETWORK_OPTS="--host" on Linux if you want all ports to be forwarded:
export NETWORK_OPTS="-p 9000:9000"
export JUPYTER_PORT=9000
# The python environment:
export PYENV=py36

## -- END CONFIGURATION --

# TODO: move this to an entrypoint script
if [ -f /.dockerenv ]; then
    cd $ORIGCWD
    if [ "$(whoami)" == $USERNAME ]; then
        CMD "${@:1}"
    else
        if [ "$1" == "--int" ]; then
            echo "interactive session"
            useradd -r -u $USERID -d $USRHOME $USERNAME
            su -m $USERNAME -c "cd $ORIGCWD && source activate $PYENV && $CMD"
        elif [ "$1" == "--bash" ]; then
            echo "starting bash"
            useradd -r -u $USERID -d $USRHOME $USERNAME
            su - $USERNAME
        elif [ "$1" == "--jupyter" ]; then
            echo "starting jupyter server"
            useradd -r -u $USERID -d $USRHOME $USERNAME
            echo "Entering directory $ORIGCWD as $USERNAME"
            # someone should figure out why this doesn't work with -m?
            # and it seems difficult to gracefully kill the jupyter notebook if run like this?
            su $USERNAME -c "cd $ORIGCWD && source activate $PYENV && jupyter notebook --port=$JUPYTER_PORT --ip=0.0.0.0 --no-browser"
        else
            echo "executing command: python ${@:1}"
            useradd -r -u $USERID -d $USRHOME $USERNAME
            su -m $USERNAME -c "source activate $PYENV && cd $ORIGCWD && $CMD ${*:1}"
        fi
    fi
else
    export USERID=`id -u`
    export USERNAME=`id -un`
    export GRPID=`id -g`
    export GRPNAME=`id -gn`
    export USRHOME=`echo $HOME`
    export ORIGCWD=`pwd`

    # docker pull $DOCKER_IMAGE

    if [ "$1" == "--bash" ]; then
        docker run \
                -v $HOME:$HOME \
                -e MKL_NUM_THREADS -e OMP_NUM_THREADS \
                -e USERID -e USERNAME -e GRPID -e GRPNAME -e USRHOME -e ORIGCWD \
                $NETWORK_OPTS -it \
                $DOCKER_IMAGE $DOCKER_PYTHON_SCRIPT --bash;
    elif [ "$1" == "--int" ]; then
        docker run \
            -v $HOME:$HOME \
            -e MKL_NUM_THREADS -e OMP_NUM_THREADS \
            -e USERID -e USERNAME -e GRPID -e GRPNAME -e USRHOME -e ORIGCWD \
            $NETWORK_OPTS -it \
            $DOCKER_IMAGE $DOCKER_PYTHON_SCRIPT --int;
    elif [ "$1" == "--jupyter" ]; then
        docker run \
            -v $HOME:$HOME \
            -e MKL_NUM_THREADS -e OMP_NUM_THREADS \
            -e USERID -e USERNAME -e GRPID -e GRPNAME -e USRHOME -e ORIGCWD \
            $NETWORK_OPTS \
            $DOCKER_IMAGE $DOCKER_PYTHON_SCRIPT --jupyter;
    else
        docker run \
            -v $HOME:$HOME \
            -e MKL_NUM_THREADS -e OMP_NUM_THREADS \
            -e USERID -e USERNAME -e GRPID -e GRPNAME -e USRHOME -e ORIGCWD \
            $NETWORK_OPTS \
            $DOCKER_IMAGE $DOCKER_PYTHON_SCRIPT "$@";
    fi
fi
