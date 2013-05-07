#!/bin/sh

export CONDAPP_VERSION=1.5.1-cmp
export PROJ_NAME=conddb-appserver
export PROJ_DIR=/data/projects/$PROJ_NAME
export SCRAM_ARCH=slc4_ia32_gcc345
export APT_VERSION=0.5.15lorg3.2-cmp
    
export CONDDB_APPSERVER_ROOT=$PROJ_DIR/$SCRAM_ARCH/cms/$PROJ_NAME/$CONDAPP_VERSION
source  $CONDDB_APPSERVER_ROOT/etc/profile.d/init.sh

