################################################################
# SecurityModule::MySQL
#
# Version info: $Id: MySQL.pm,v 1.4 2008/08/07 22:38:46 dfeichti Exp $
################################################################
package CMSWebTools::SecurityModule::MySQL;

use SecurityModule;
use DBI;
use Data::Dumper;
@ISA = ("SecurityModule");
use strict;

sub new {
  my $class = shift;
  my $options = shift;

  my $self  = $class->SUPER::new($options);

  my @settable = qw(DBHOST DBPORT DBNAME DBUSER DBPASS);
  $self->{DBHOST} = "localhost";
  $self->{DBPORT} = 3306;
  $self->{DBNAME} = "secmod";
  $self->{DBUSER} = "somename";
  $self->{DBPASS} = "somepwd";

  $self->{DBHANDLE}=undef;

  while( my ($opt,$val) = each %$options) {
    die "No such option: $opt" if ! grep (/^$opt$/,@settable);
    $self->{$opt} = $val;
  }

  bless ($self, $class);
  return $self;
}

sub init {
  my $self = shift;

  #TODO: get DB params via configuration
  my $connstr = "DBI:mysql:database=" . $self->{DBNAME} . ";host=" . $self->{DBHOST}
    . ";port=" . $self->{DBPORT};

  eval {
    $self->{DBHANDLE} = DBI->connect($connstr,$self->{DBUSER},$self->{DBPASS},
				       {'RaiseError' => 1,
					'AutoCommit' => 1,
				        'PrintError' => 0});
  };
  if($@) {
    $self->_log(1,"Error: Could not connect to DB: $@ (conn str: $connstr)");
    $self->{ERRMSG}= "Could not connect to DB";
    return 0;
  }

  return 0 if (!$self->SUPER::init());

  return 1;
}

############################################
# PRIVATE METHODS

#
# If argument keyid is given, fetches the appropriate key. If
# keyid is omitted, returns the a valid key from the DB (if no
# valid keys are found, a new one will be generated).
# @param: keyid  ID of key to be retrieved
# @return: 0 if ok, 1 if no such key in DB, 2 if key is too old
#
sub _getCipherKey {
  my $self = shift;
  my $keyid = shift;

  $self->{CIPHERKEY} = undef;
  $self->{KEYID} = undef;

  my $time = time();
  my ($stha,$sthb,$row,$keytime);


  if ($keyid) {
    $stha=$self->{DBHANDLE}->prepare("SELECT cryptkey,UNIX_TIMESTAMP(time) FROM crypt_key WHERE id = '$keyid'");
    $stha->execute();
    return 1 if ! ($row = $stha->fetchrow_arrayref());
    $keytime = $row->[1];
    return 2 if $time - $keytime > $self->{KEYVALIDTIME};
    $self->{CIPHERKEY} = $row->[0];
    $self->{KEYID} = $keyid;
    return 0;
  }

  $stha=$self->{DBHANDLE}->prepare("SELECT id,cryptkey,UNIX_TIMESTAMP(time) FROM crypt_key ORDER BY id DESC LIMIT 1");
  $stha->execute();
  $row = $stha->fetchrow_arrayref();
  $keytime = $row->[2];

  if ($time - $keytime > $self->{KEYVALIDTIME}) {
    my $newkey = $self->_createCryptKey();
    $self->_log(5,"_getCipherKey: created new cipher key (length: " . length($newkey) . ")");
    $sthb = $self->{DBHANDLE}->prepare("INSERT INTO crypt_key (cryptkey) VALUES (?)");
    eval {
       $sthb->execute($newkey);
    };
    if($@) {
      $self->_log(1,"Failed to insert key into DB: $@");
      $self->{ERRMSG}= "Failed to insert key into DB";
      return 3;
    }

    $stha->execute();
    $row = $stha->fetchrow_arrayref();
  }

  $self->{KEYID} = $row->[0];
  $self->{CIPHERKEY} = $row->[1];

  return 0;

}

sub _getDNfromUsername {
  my $self = shift;
  my $username = shift;

  my $sth = $self->{DBHANDLE}->prepare("SELECT dn FROM auth_n_user WHERE username = '$username'");
  $sth->execute();
  if(my $row = $sth->fetchrow_arrayref()) {
    $self->_log(5,"_getDNfromUsername: mapped $username to $row->[0]");
    return $row->[0];
  }
  return undef;
}

sub _getRolesFromDN {
  my $self = shift;
  my $dn = shift;

  my ($userid,$row);
  my $roles={};

  my $sth = $self->{DBHANDLE}->prepare("SELECT id FROM auth_n_user WHERE dn = '$dn'");
  $sth->execute();
  if($row = $sth->fetchrow_arrayref()) {
    $userid=$row->[0];
  }
  #print "DEBUG:userid: $userid<br>\n";
  #return {};

  $sth =  $self->{DBHANDLE}->prepare("select role,scope from auth_z_role,auth_z_user_role,auth_z_scope " .
				     "where auth_z_user_role.user_id='$userid' and " .
				     "auth_z_role.id=auth_z_user_role.role_id and " .
				     "auth_z_scope.id=auth_z_user_role.scope_id");
  $sth->execute();
  push @{$roles->{$row->[0]}},$row->[1] while $row = $sth->fetchrow_arrayref();

  $self->_log(5,"_getRolesFromDN: got Roles for $dn: " .Dumper($roles));
  return $roles;
}

sub _getUserPasswd {
  my $self = shift;
  my $username = shift;

  my $sth = $self->{DBHANDLE}->prepare("SELECT passwd FROM user_passwd WHERE username = '$username'");
  $sth->execute();
  my $row;
  return $row->[0] if $row = $sth->fetchrow_arrayref();

  return undef;
}

# import a Hypernews passwords file
sub importHNpasswords {
  my $self = shift;
  my $hnfile = shift;

  if (! open (HNFILE,"<$hnfile")) {
    $self->_log(1,"importHNpasswords: Could not open File: $hnfile");
    return 0;
  }

  my $stha = $self->{DBHANDLE}->prepare("SELECT passwd FROM user_passwd WHERE username = ?");
  my $sthb = $self->{DBHANDLE}->prepare("INSERT INTO user_passwd (username,description,passwd) "
				      . "VALUES (?,?,?)");
  my $sthc = $self->{DBHANDLE}->prepare("UPDATE user_passwd SET passwd = ?, description = ? WHERE username = ?");

  my($uname,$pass,$descr,$row);
  my $num=0;
  while(my $line = <HNFILE>) {
    if( ! (($uname,$pass,undef,undef,$descr,undef,undef) = split(/:/,$line)) ) {
      $self->_log(1,"importHNpasswords: Could not parse line: $line");
      next;
    }

    $stha->execute($uname);
    if($row=$stha->fetchrow_arrayref()) {
      if ($row->[0] ne $pass) {
	$sthc->execute($pass,$descr,$uname);
	$num++;
      }
      next;
    }
    $sthb->execute($uname,$descr,$pass);
    $num++;
  }

  $self->_log(1,"importHNpasswords: inserted/updated $num entries from $hnfile");
  close HNFILE;
  return 1;
}

sub DESTROY {
  ## disconnect is not necessary if mod_perl is used
  #my $self=shift;
  #$self->{DBHANDLE}->disconnect() if defined $self->{DBHANDLE};
}



1;

