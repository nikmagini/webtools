#!/bin/sh

FRONTEND=https://cmsweb.cern.ch
SITEDB_VERSION=1.2.3-cmp2
PROJECT=sitedb
### Pick up the base path from RPM, instead of hardcoding it here..
PROJ_DIR=/data/projects/$PROJECT
PROJ_CONFIG=$PROJ_DIR/config
LOG_DIR=$PROJ_DIR/logs
SEC_MOD_INI=$PROJ_CONFIG/security.ini
SCRAM_ARCH=slc4_ia32_gcc345
APT_VERSION=0.5.15lorg3.2-cmp
. $PROJ_DIR/$SCRAM_ARCH/external/apt/$APT_VERSION/etc/profile.d/init.sh
INSTANCE=$1

mkdir -p $PROJ_DIR/logs
            
if [ "$INSTANCE" = "production" ]; then
   export SITEDB_PORT=8055
   export SITEDB_BASE=sitedb
   export SITEDB_CMD="cmsWeb --base-url $FRONTEND/$SITEDB_BASE -p $SITEDB_PORT --default-page /sitelist/ --my-sitedb-ini=$PROJ_CONFIG/sitedb.ini &> $LOG_DIR/sitedb`date +%y%m%d`.log &"
else
   export SITEDB_PORT=8058
   export SITEDB_BASE=sitedb_wttest
   export SITEDB_CMD="cmsWeb --base-url $FRONTEND/$SITEDB_BASE -p $SITEDB_PORT --default-page /sitelist/ --my-sitedb-ini=$PROJ_CONFIG/sitedb.ini --log-level 10000 &> $LOG_DIR/sitedb`date +%y%m%d`.log &"
fi

cd $PROJ_DIR
. $PROJ_DIR/$SCRAM_ARCH/cms/sitedb/$SITEDB_VERSION/etc/profile.d/init.sh
rm sitedb`date +%m%d%y`.log
