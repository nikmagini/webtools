#!/bin/sh

##H Reapply reader/writer account privileges to all PhEDEx tables.
##H
##H Usage: OraclePrivs.sh MASTER/PASS@DB READER WRITER
##H
##H MASTER should be the master account name,
##H and PASS it's password.  The first argument will be passed
##H to "sqlplus" as such.
##H
##H READER and WRITER should be the reader
##H and writer accounts, respectively.
##H
##H Issues "grant" statements for all tables as appropriate.  Run
##H this script after defining new tables to update privileges.

if [ $# -ne 3 ]; then
   grep "^##H" < $0 | sed 's/^\#\#\H\( \|$\)//'
   exit 1
fi

connect="$1" reader="$2" writer="$3"

echo_sets() {
  echo "set lines 1000 pages 0;"; 
  echo "set feedback off;";
  echo "set head off;";
}

# Update privileges for all roles and tables.

#for role in \
#  $((echo "select granted_role from user_role_privs;") |
#    sqlplus -S "$connect" | awk '/SITEDB/ { print $1 } {}'); do
#  echo; echo; echo "-- role $role"
#  echo "set feedback off;"
#  echo "grant $role to $writer;"
 
for role in \
  $(echo "dummy_role"); do
  echo; echo; echo "-- role $role"
  echo "set feedback off;"

  for table in \
    $((echo_sets
       echo "select table_name from user_tables;"
      ) |
      sqlplus -S "$connect" | awk '/^[A-Z0-9_]+$/ { print $1 } {}'); do

    echo "revoke all on $table from $reader;"
    echo "revoke all on $table from $writer;"
#    echo "revoke all on $table from $role;"

    case $table:$role in
      *:* )
        # Select only
        echo; echo "grant select on $table to $reader;"
        echo "grant select, insert, update, delete on $table to $writer;" ;;
    esac
  done

  for seq in \
    $((echo_sets
       echo "select sequence_name from user_sequences;") |
       sqlplus -S "$connect" | awk '/^[A-Z0-9_]+$/ { print $1 } {}'); do

    echo "revoke all on $seq from $reader;"
    echo "revoke all on $seq from $writer;"
#    echo "revoke all on $seq from $role;"

    case $seq:$role in
      *:* )
        # Everybody can change all sequences
        echo; echo "grant select on $seq to $reader;"
        echo "grant select on $seq to $writer;" ;;
#        echo "grant select, alter on $seq to $role;" ;;
    esac
  done
done | sqlplus -S "$connect"
