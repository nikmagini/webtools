################################################################
# SecurityModule::MySQL
#
# Version info: $Id: SQLite.pm,v 1.7 2008/08/07 22:38:46 dfeichti Exp $
################################################################
package CMSWebTools::SecurityModule::SQLite;

use CMSWebTools::SecurityModule;
use DBI;
use MIME::Base64;
use Data::Dumper;
@ISA = ("CMSWebTools::SecurityModule");
use strict;

sub new {
  my $class = shift;
  my $options = shift;

  my $self  = $class->SUPER::new($options);

  my @settable = qw(DBFILE);
  $self->{DBFILE} = undef;
  $self->{DBHANDLE} = undef;

  while( my ($opt,$val) = each %$options) {
    die "No such option: $opt" if ! grep (/^$opt$/,@settable);
    $self->{$opt} = $val;
  }

  bless ($self, $class);
  return $self;
}

# Note: AutoCommit=1 is extremely important for SQLite, since if it is
# not set (and no commit is issued), the DB will continually lock!
sub init {
  my $self = shift;

  # since SQLite will create a DB if the file is not found, we need to
  # care for this error:
  if (! -r $self->{DBFILE}) {
    $self->_log(1,"Cannot read SQLite DBFILE: $self->{DBFILE}");
    $self->{ERRMSG}= "Could not connect to DB";
    return 0;
  }

  my $connstr = "DBI:SQLite:dbname=" . $self->{DBFILE};

  eval {
    $self->{DBHANDLE} = DBI->connect($connstr,"","",
				       {'RaiseError' => 1,
					'AutoCommit' => 1,
				        'PrintError' => 0});
  };
  if($@) {
    $self->_log(1,"Could not connect to DB: $@ (conn str: $connstr)");
    $self->{ERRMSG}= "Could not connect to DB";
    return 0;
  }

  return 0 if (!$self->SUPER::init());

  return 1;
}

# @params:  a role and a site
# @return:  list of usernames
sub getUsersWithRoleForSite {
    my ($self, $role, $site) = @_;
    my $sql = qq{ select c.id, c.surname, c.forename, c.email,
		         c.username, c.dn, c.phone1, c.phone2
		    from contact c
		    join site_responsibility sr on sr.contact = c.id
		    join role r on r.id = sr.role
		    join site s on s.id = sr.site
		   where r.title = ? and s.name = ? };
    my $sth = $self->{DBHANDLE}->prepare($sql);
    $sth->execute($role, $site);
    my @users;
    while (my $user = $sth->fetchrow_hashref()) {
	push @users, $user;
    }
    return @users;
}

# @params:  a role and a group
# @return:  list of usernames
sub getUsersWithRoleForGroup {
    my ($self, $role, $group) = @_;
    my $sql = qq{ select c.id, c.surname, c.forename, c.email,
		         c.username, c.dn, c.phone1, c.phone2
		    from contact c
		    join group_responsibility gr on gr.contact = c.id
		    join role r on r.id = gr.role
		    join user_group g on g.id = gr.user_group
		   where r.title = ? and g.name = ? };
    my $sth = $self->{DBHANDLE}->prepare($sql);
    $sth->execute($role, $group);
    my @users;
    while (my $user = $sth->fetchrow_hashref()) {
	push @users, $user;
    }
    return @users;
}

# @params:  none
# @returns:  hash of phedex nodes to site names
sub getPhedexNodeToSiteMap {
    my ($self) = @_;
    my $sql = qq { select n.name, s.name
		     from phedex_node n
		     join site s on s.id = n.site };
    my $sth = $self->{DBHANDLE}->prepare($sql);
    $sth->execute();
    my %map;
    while (my ($node, $site) = $sth->fetchrow()) {
	$map{$node} = $site;
    }
    return %map;
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
# Note: SQLite cannot correctly handle binary fields. Therefore we use
# base 64 encoding for storing the keys
sub _getCipherKey {
  my $self = shift;
  my $keyid = shift;

  $self->{CIPHERKEY} = undef;
  $self->{KEYID} = undef;

  my $time = time();
  my ($stha,$sthb,$row,$keytime);


  if ($keyid) {
    $stha=$self->{DBHANDLE}->prepare("SELECT cryptkey,STRFTIME('%s',time) FROM crypt_key WHERE id = '$keyid'");
    $stha->execute();
    return 1 if ! ($row = $stha->fetchrow_arrayref());
    $keytime = $row->[1];
    return 2 if $time - $keytime > $self->{KEYVALIDTIME};
    $self->{CIPHERKEY} = decode_base64($row->[0]);
    $self->{KEYID} = $keyid;
    return 0;
  }

  $stha=$self->{DBHANDLE}->prepare("SELECT id,cryptkey,STRFTIME('%s',time) FROM crypt_key ORDER BY id DESC LIMIT 1");
  $stha->execute();
  $row = $stha->fetchrow_arrayref();
  $keytime = $row->[2];

  if ($time - $keytime > $self->{KEYVALIDTIME}) {
    my $newkey = $self->_createCryptKey();
    $self->_log(5,"_getCipherKey: created new crypt key (length: " . length($newkey) . ")");
    $sthb = $self->{DBHANDLE}->prepare("INSERT INTO crypt_key (cryptkey,time) VALUES (?,DATETIME('NOW'))");

    eval {
      $sthb->execute(encode_base64($newkey));
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
  $self->{CIPHERKEY} = decode_base64($row->[1]);

  return 0;

}

sub _getIDfromDN {
  my $self = shift;
  my $dn = shift;

  my $sth = $self->{DBHANDLE}->prepare("SELECT id FROM contact WHERE dn = '$dn'");
  $sth->execute();
  if(my $row = $sth->fetchrow_arrayref()) {
    $self->_log(5,"_getUserIDfromDN: mapped $dn to ID $row->[0]");
    return $row->[0];
  }
  return undef;
}

sub _getIDfromUsername {
  my $self = shift;
  my $username = shift;

  my $sth = $self->{DBHANDLE}->prepare("SELECT id FROM contact WHERE username = '$username'");
  $sth->execute();
  if(my $row = $sth->fetchrow_arrayref()) {
    $self->_log(5,"_getUserIdfromUsername: mapped $username to $row->[0]");
    return $row->[0];
  }
  return undef;
}

sub _getUsernameFromID {
  my $self = shift;
  my $id = shift;

  return undef if ! defined $id;
  my $sth = $self->{DBHANDLE}->prepare("SELECT username FROM contact WHERE id = $id");
  $sth->execute();
  if(my $row = $sth->fetchrow_arrayref()) {
    $self->_log(5,"_getUsernamefromID: mapped ID to username $row->[0]");
    return $row->[0];
  }
  return undef;
}

sub _getUserInfoFromID {
  my $self = shift;
  my $id = shift;

  return 0 if ! defined $id;
  my $sth = $self->{DBHANDLE}->prepare("SELECT surname,forename,email FROM contact WHERE id = $id");
  $sth->execute();
  if(my $row = $sth->fetchrow_arrayref()) {
    $self->{USERSURNAME} = $row->[0];
    $self->{USERFORENAME} = $row->[1];
    $self->{USEREMAIL} = $row->[2];
    return 1;
  }
  $self->_log(1,"_getUserInfoFromID: Failed to get user info for ID $id");

  return 0;
}

sub _getRolesFromID {
  my $self = shift;
  my $id = shift;

  return {} if ! defined $id;

  my ($userid,$row);
  my $roles={};

  my $sth =  $self->{DBHANDLE}->prepare("SELECT role.title,site.name FROM site_responsibility,role,site " .
					"WHERE site_responsibility.contact = $id " .
					" AND role.id = site_responsibility.role AND site.id = site_responsibility.site " .
				       "UNION SELECT role.title,user_group.name FROM group_responsibility,role,user_group " .
					"WHERE group_responsibility.contact = $id " .
					" AND role.id = group_responsibility.role AND user_group.id = group_responsibility.user_group");
  $sth->execute();
  push @{$roles->{$row->[0]}},$row->[1] while $row = $sth->fetchrow_arrayref();

  $self->_log(5,"_getRolesFromDN: got Roles for $id: " .Dumper($roles));
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
  my $self=shift;
  $self->{DBHANDLE}->disconnect() if defined $self->{DBHANDLE};
}



1;
