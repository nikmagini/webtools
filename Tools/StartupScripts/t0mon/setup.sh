#!/bin/sh

FRONTEND=https://cmsweb.cern.ch
T0MON_VERSION=0.5.2-cmp
PROJECT=T0Mon
### Pick up the base path from RPM, instead of hardcoding it here..
PROJ_DIR=/data/projects/$PROJECT

LOG_DIR=$PROJ_DIR/logs

SCRAM_ARCH=slc4_ia32_gcc345
APT_VERSION=0.5.15lorg3.2-cmp
. $PROJ_DIR/$SCRAM_ARCH/external/apt/$APT_VERSION/etc/profile.d/init.sh
INSTANCE=$1

mkdir -p $PROJ_DIR/logs
            
if [ "$INSTANCE" = "production" ]; then
   T0MON_PORT=8300
   T0MON_BASE=T0Mon
else
   T0MON_PORT=8301
   T0MON_BASE=T0Mon_test
fi
T0MON_CMD="cmsWeb --base-url $FRONTEND/$T0MON_BASE -p $T0MON_PORT --default-page /$T0MON_BASE &> T0Mon`date +%m%d%y`.log &"

cd $PROJ_DIR
. $PROJ_DIR/$SCRAM_ARCH/cms/T0Mon/$T0MON_VERSION/etc/profile.d/init.sh
