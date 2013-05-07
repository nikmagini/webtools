################################################################
# SecurityModule::MySQL
#
# Version info: $Id: Oracle.pm,v 1.7 2009/04/07 17:13:15 egeland Exp $
################################################################
package CMSWebTools::SecurityModule::Oracle;

use CMSWebTools::SecurityModule;
use DBI;
use MIME::Base64;
use Data::Dumper;
use POSIX qw(mktime);
@ISA = ("CMSWebTools::SecurityModule");
use strict;

sub new {
  my $class = shift;
  my $options = shift;

  my $self  = $class->SUPER::new($options);

  my @settable = qw(DBNAME DBUSER DBPASS);
  $self->{DBNAME} = undef;
  $self->{DBUSER} = undef;
  $self->{DBPASS} = undef;
  $self->{DBHANDLE} = undef;

  while( my ($opt,$val) = each %$options) {
    die "No such option: $opt" if ! grep (/^$opt$/,@settable);
    $self->{$opt} = $val;
  }

  bless ($self, $class);
  return $self;
}

sub init {
  my $self = shift;

  my $connstr = "DBI:Oracle:" . $self->{DBNAME};

  eval {
      $self->{DBHANDLE} = DBI->connect($connstr, $self->{DBUSER}, $self->{DBPASS},
				       {'AutoCommit' => 0,
					'RaiseError' => 1,
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
    $stha=$self->{DBHANDLE}->prepare("SELECT cryptkey,to_char(sys_extract_utc(time), 'YYYY-MM-DD HH24:MI:SS') FROM crypt_key WHERE id = ?");
    $stha->execute($keyid);
    return 1 if ! ($row = $stha->fetchrow_arrayref());
    $keytime = &_strtimeToSeconds($row->[1]);
    $self->_log(5,sprintf("_getCipherKey: key expiration: time=%i keytime=%i diff=%i keyvalidtime=%i", $time, $keytime, $time - $keytime, $self->{KEYVALIDTIME}));
    return 2 if $time - $keytime > $self->{KEYVALIDTIME};
    $self->{CIPHERKEY} = decode_base64($row->[0]);
    $self->{KEYID} = $keyid;
    return 0;
  }

  $stha=$self->{DBHANDLE}->prepare("SELECT id,cryptkey,to_char(sys_extract_utc(time), 'YYYY-MM-DD HH24:MI:SS') FROM crypt_key ORDER BY time DESC");
  $stha->execute();
  $row = $stha->fetchrow_arrayref();
  $keytime = &_strtimeToSeconds($row->[2]);

  if (!defined $keytime || $time - $keytime > $self->{KEYVALIDTIME}) {
    my $newkey = $self->_createCryptKey();
    $self->_log(5,"_getCipherKey: created new crypt key (length: " . length($newkey) . ")");
    # ensure that the next key read is the key that we make here
    $self->{DBHANDLE}->do("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE");
    $sthb = $self->{DBHANDLE}->prepare("INSERT INTO crypt_key (id,cryptkey,time) VALUES (crypt_key_sq.nextval,?,SYSTIMESTAMP)");

    eval {
      $sthb->execute(encode_base64($newkey));
    };
    if($@) {
      $self->_log(1,"Failed to insert key into DB: $@");
      $self->{ERRMSG}= "Failed to insert key into DB";
      return 3;
    }

    $stha->execute();
    $row = $stha->fetchrow_arrayref(); # read the key we just made
    $self->{DBHANDLE}->commit();       # end of transaction
  }

  $self->{KEYID} = $row->[0];
  $self->{CIPHERKEY} = decode_base64($row->[1]);

  return 0;

}

sub _getIDfromDN {
  my $self = shift;
  my $dn = shift;

  my $sth = $self->{DBHANDLE}->prepare("SELECT id FROM contact WHERE dn = ?");
  $sth->execute($dn);
  if(my $row = $sth->fetchrow_arrayref()) {
    $self->_log(5,"_getUserIDfromDN: mapped $dn to ID $row->[0]");
    return $row->[0];
  }
  return undef;
}

sub _getIDfromUsername {
  my $self = shift;
  my $username = shift;

  my $sth = $self->{DBHANDLE}->prepare("SELECT id FROM contact WHERE username = ?");
  $sth->execute($username);
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
  my $sth = $self->{DBHANDLE}->prepare("SELECT username FROM contact WHERE id = ?");
  $sth->execute($id);
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
  my $sth = $self->{DBHANDLE}->prepare("SELECT surname,forename,email FROM contact WHERE id = ?");
  $sth->execute($id);
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
					"WHERE site_responsibility.contact = ? " .
					" AND role.id = site_responsibility.role AND site.id = site_responsibility.site " .
				       "UNION SELECT role.title,user_group.name FROM group_responsibility,role,user_group " .
					"WHERE group_responsibility.contact = ? " .
					" AND role.id = group_responsibility.role AND user_group.id = group_responsibility.user_group");
  $sth->execute($id, $id);
  push @{$roles->{$row->[0]}},$row->[1] while $row = $sth->fetchrow_arrayref();

  $self->_log(5,"_getRolesFromDN: got Roles for $id: " .Dumper($roles));
  return $roles;
}

sub _getUserPasswd {
  my $self = shift;
  my $username = shift;

  my $sth = $self->{DBHANDLE}->prepare("SELECT passwd FROM user_passwd WHERE username = ?");
  $sth->execute($username);
  my $row;
  return $row->[0] if $row = $sth->fetchrow_arrayref();

  return undef;
}

# converts time of the form 'YYYY-MM-DD hh:mm:ss' to seconds since the UNIX epoch
sub _strtimeToSeconds {
    my $strtime = shift @_;
    return undef unless $strtime;
    my @args = reverse ($strtime =~ /(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)/);
    $args[5] -= 1900;
    $args[4] -= 1;
    my $t1 = mktime (@args);
    my @gmt = gmtime ($t1);
    my $t2 = mktime (@gmt);
    return $t1 + ($t1 - $t2);
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
  my $sthb = $self->{DBHANDLE}->prepare("INSERT INTO user_passwd (username,passwd) "
				      . "VALUES (?,?)");
  my $sthc = $self->{DBHANDLE}->prepare("UPDATE user_passwd SET passwd = ?, WHERE username = ?");

  my $num_ins=0;
  my $num_upd=0;
  while(my $line = <HNFILE>) {
      my @line = split(/:/,$line);
      my ($uname, $pass, $desc) = @line[(0, 1, 4)];
      if( ! $uname || ! $pass) {
	  $self->_log(1,"importHNpasswords: Could not parse line: $line");
	  next;
      }

      $stha->execute($uname);
      if(my $row=$stha->fetchrow_arrayref()) {
	  if ($row->[0] ne $pass) {
	      $sthc->execute($pass,$uname);
	      $num_upd++;
	  }
	  next;
      }
      $sthb->execute($uname,$pass);
      $num_ins++;
  }

  $self->_log(1,"importHNpasswords: inserted $num_ins and updated $num_upd entries from $hnfile");
  close HNFILE;
  return 1;
}

sub DESTROY {
  ## disconnect is not necessary if mod_perl is used
  my $self=shift;
  $self->{DBHANDLE}->disconnect() if defined $self->{DBHANDLE};
}



1;
