#!/usr/bin/env perl

################################################################
# crypttest.pl
#
# Version info: $Id: crypttest.pl,v 1.2 2007/06/27 09:37:55 eulisse Exp $
################################################################

use Crypt::CBC;
use Carp;
use Getopt::Std;
use MIME::Base64;
use strict;


#####################################################
# PARAMETERS
#
# we use a 56 byte key
my $key = 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabde';
#####################################################


sub usage {
  print <<"EOF";
usage: crypttest.pl -d/-e [-i iv-vector] "message"
   options:
    -e              :  encrypt
    -d              :  decrypt
    -i iv-vector    :  provide a 8 byte init vector for encryption
EOF

}

my $iv;
my $mode='e';

# OPTION PARSING
my %option=();
getopts("edhi:",\%option);

if (defined $option{h}) {
  usage();
  exit(0);
}

if (defined $option{e}) {
  $mode='e';
}

if (defined $option{d}) {
  $mode='d';
}

if (defined $option{i}) {
  $iv = $option{i};
} else {
  $iv     = Crypt::CBC->random_bytes(8);
}

my $text = shift;

die "Error: No text given" if ! $text;
die "Error: IV needs to have length = 8 " if length($iv) != 8;


my $cipher = Crypt::CBC->new( -cipher => 'Blowfish',
			      -literal_key => 1,
			      -key => $key,
			      -iv => $iv,
			      -header      => 'none',
			      -blocksize => 8,
			      -keysize => 56
			      -padding => 'standard'
			    );


if ($mode eq 'e') {
  my $encr = encrypt($text);
  print ">$encr<\n";
  #print "Control check: Decrypted: " . decrypt($encr) . "\n";
} else {
  print ">" . decrypt($text) . "<\n";
}

exit 0;

# we prepend the iv to the encryption
sub encrypt {
  my $plain = shift;

  my $encr = $iv . $cipher->encrypt($plain);
  my $encr64 = encode_base64($encr);

  chomp($encr64);
  return $encr64
}

sub decrypt {
  my $encr64 = shift;

  my $encr = decode_base64($encr64);
  my $iv = substr($encr,0,8,"");
  $cipher->set_initialization_vector($iv);
  my $decr = $cipher->decrypt($encr);

  return $decr;
}
