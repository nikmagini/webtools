#!/bin/sh
ver=V05_00_04-cmp
frontend=https://cmsweb.cern.ch
#ver=V05_00_03-cmp
#ver=V05_00_02-cmp
#ver=V04_01_27-cmp
#ver=V04_01_23-cmp
proj_dir=/data/projects/dbs
source $proj_dir/slc4_ia32_gcc345/external/apt/0.5.15lorg3.2-cmp/etc/profile.d/init.sh
source $proj_dir/slc4_ia32_gcc345/cms/dbs-web/$ver/etc/profile.d/init.sh
cd $proj_dir/slc4_ia32_gcc345/cms/dbs-web/$ver/lib/python2.4/site-packages/
