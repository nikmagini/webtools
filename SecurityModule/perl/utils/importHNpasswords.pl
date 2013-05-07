#!/usr/bin/env perl
##############################################################
#
# Importing of a HyperNews password file into a
# SecurityModule data base
#
# NOTE: Currently the importHNpasswords does not delete users
#       that have disappeared from the password file. New isers
#       are added and password changes are taken into account
#
#
# Version info: $Id: importHNpasswords.pl,v 1.4 2007/06/27 09:37:58 eulisse Exp $
##############################################################

use strict;

sub usage {
  print <<"EOF";
usage: importHNpasswords db-backend secmod-config  hn_password_file
EOF
}

my $dbbackend = $ARGV[0];
my $config = $ARGV[1];
my $hnfile = $ARGV[2];
usage && die "Error: Specify a DB backend\n" if ! $dbbackend;
usage && die "Error: Specify a SecurityModule configuration file\n" if ! $config;
usage && die "Error: Specify a HyperNews password file\n" if ! $hnfile;
usage && die "Error: Cannot read file $hnfile\n" if ! -r $hnfile;

my $sec;
if ($dbbackend eq 'sqlite') {
    require CMSWebTools::SecurityModule::SQLite;
    $sec = new CMSWebTools::SecurityModule::SQLite({CALLER_URL => "",
						    CONFIG => $config,
						    LOGLEVEL => 5,
						    REVPROXY => undef
						    });
} else {
    require CMSWebTools::SecurityModule::Oracle;
    $sec = new CMSWebTools::SecurityModule::Oracle({CALLER_URL => "",
						    CONFIG => $config,
						    LOGLEVEL => 5,
						    REVPROXY => undef
						    });
}

$sec->init() or die "Error: Failed to init SecMod: " . $sec->getErrMsg() . "\n";
$sec->importHNpasswords($hnfile) or die "Error: Failed to import HN passwords\n";

print "OK\n";
exit 0;
