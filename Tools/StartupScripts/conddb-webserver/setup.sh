#!/bin/sh

export WEBCONDDB_VERSION=1.5.1b-cmp
export PROJ_NAME=webconddb
export PROJECT=condDB
export PROJ_DIR=/data/projects/$PROJECT
export SCRAM_ARCH=slc4_ia32_gcc345
export APT_VERSION=0.5.15lorg3.2-cmp
    
export WEBCONDDB_ROOT=$PROJ_DIR/$SCRAM_ARCH/cms/$PROJ_NAME/$WEBCONDDB_VERSION

. $WEBCONDDB_ROOT/etc/profile.d/init.sh
