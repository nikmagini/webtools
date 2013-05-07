#!/bin/sh

FRONTEND="https://cmsweb.cern.ch"
PRODMON_VERSION=0.0.3-cmp3
DEFAULT="/plots/index"
INSTANCE=$1

. /data/projects/prodmon/slc4_ia32_gcc345/cms/prodmon/0.0.3-cmp3/etc/profile.d/init.sh

LOCKFILE="$PRODMON_ROOT/pid.$INSTANCE.txt"

if [ "$INSTANCE" = "prod" ]; then
   PRODMON_PORT=8018
   PRODMON_BASE=prodmon
else
   PRODMON_PORT=8019
   PRODMON_BASE=prodmon_test
fi

PRODMON_CMD="cmsWeb --pid-file ${LOCKFILE} -p ${PRODMON_PORT} --base-url $FRONTEND/${PRODMON_BASE} --default-page ${DEFAULT}"  

# add some needed paths to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$PY2_PIL_ROOT/lib/python2.4/site-packages/PIL:$WEBTOOLS_ROOT/lib/python2.4/site-packages/Tools/GraphTool/src
