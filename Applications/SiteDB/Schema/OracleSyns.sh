#!/bin/sh

##H Recreate synonyms from tables in master account.
##H
##H Usage: OracleSyns.sh MASTER MASTER/MPASS@DB ACCOUNT/APASS@DB
##H
##H MASTER should be the master account name,
##H and MPASS it's password.  ACCOUNT/APASS should be similar
##H pair for the account into which synonyms should be created
##H (_reader, _writer).  Both arguments will be
##H passed to "sqlplus" as such.
##H
##H Issues "drop synonym"/"create synonym" statements for all
##H tables as appropriate.  All previous synonyms are removed
##H and fresh ones are created from master table list.

if [ $# -ne 3 ]; then
   grep "^##H" < $0 | sed 's/^\#\#\H\( \|$\)//'
   exit 1
fi

master="$1" master_connect="$2" target_connect="$3"

create_syn() {
  (echo "set lines 1000 pages 0;"; 
   echo "set feedback off;";
   echo ${1+"$@"}) |
  sqlplus -S "$master_connect" |
  grep -v "SP2-0310"
}

(# First drop all existing synonyms
 (echo "set lines 1000 pages 0";
  echo "set feedback off;";
  echo "select synonym_name from user_synonyms;") |
  sqlplus -S "$target_connect" |
  grep -v "SP2-0310" |
  while read t; do
     echo "drop synonym $t;"
  done

 # Now recreate synonyms from master tables
 create_syn "select table_name from user_tables;" |
   while read t; do echo "create synonym $t for $master.$t;"; done

 create_syn "select sequence_name from user_sequences;" |
   while read t; do echo "create synonym $t for $master.$t;"; done
) | sqlplus -S "$target_connect"
