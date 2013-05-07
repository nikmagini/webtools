#!/bin/sh

arch=slc4_ia32_gcc345
aptv=0.5.15lorg3.2-cmp

source $proj_dir/$arch/external/apt/$aptv/etc/profile.d/init.sh
source $prof_dir/$arch/cms/$ws_name/$ws_ver/etc/profile.d/init.sh
cd     $proj_dir/$arch/cms/$ws_name/$ws_ver/lib/python2.4/site-packages/

