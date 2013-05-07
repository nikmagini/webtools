#!/bin/bash

plain=$1

if test z"$plain" = z; then
    plain="Some test string for encryption"
fi

# For this test we specify a fixed init vector
iv="abcdefgh"

encrperl=`./crypttest.pl -e -i $iv "$plain"|sed -e 's/^>\(.*\)<$/\1/'`
echo "  Perl encrypt: >$encrperl<"
decrpython=`./crypttest.py -d "$encrperl"|sed -e 's/^>\(.*\)<$/\1/'`
echo "Python decrypt: >$decrpython<"

encrpython=`./crypttest.py -e -i $iv "$plain"|sed -e 's/^>\(.*\)<$/\1/'`
echo "Python encrypt: >$encrpython<"
decrperl=`./crypttest.pl -d "$encrpython"|sed -e 's/^>\(.*\)<$/\1/'`
echo "  Perl decrypt: >$decrperl<"

if test "$encrperl" != "$encrpython"; then
    echo "ERROR: Encrypted strings do not match"
    exit 1
fi
if test "$decrperl" != "$decrpython"; then
    echo "ERROR: Decrypted strings do not match"
    echo "   Perl  : $decrperl"|cat -v
    echo "   Python: $decrpython"|cat -v
    exit 1
fi

echo;echo "OK"

