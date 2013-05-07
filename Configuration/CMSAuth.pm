package CMSAuth;
use Apache2::Const -compile => ':common', ':http';
use Digest::HMAC_SHA1 'hmac_sha1';
use File::Temp ':mktemp';
use Compress::Zlib;
use MIME::Base64;

my $NULL_COOKIE = "cms-auth=;path=/;secure;httponly;expires=Thu, 01-Jan-1970 00:00:01 GMT\n";
my $initialised = 0;
my %host_exempt = ();
my $secret;
my %secrets;
my %vocms;

# Shorthand for string-to-string base64 encoding.
sub base64 { return &encode_base64($_[0], ''); }

# Shorthand for getting initial request in internal redirects.
sub initialreq
{
  my $prev;
  my $r = shift;
  $r = $prev while ($prev = $r->prev);
  return $r;
}

# Parse cookies from Apache HTTP request.
#
# The input consists of one or more cookie values separated by ';'.
# Each cookie values is of the form NAME=VALUE.  Each NAME may be
# given one or more times; only the first value is kept, on the
# assumption it is the most specific (domain-wise).
#
# FIXME: Parse actual HTTP "Cookie:" header rather than Apache's
# idea of the cookies, and handle $Domain etc. settings manually.
sub parse_cookies
{
  my %cookies = ();
  foreach (map { split(/; ?/) } @_)
  {
    s/^\s+//; s/\s+$//;
    $cookies{$1} = $2 if /([^=]+)=(.*)/ && ! exists $cookies{$1};
  }
  return %cookies;
}

# Build a cookie data value.  The first two values must be the type
# cookie data type ('host' or 'cert'), and the remote address.  The
# remaining arguments are base64-encoded.  All parameters are joined
# together with '|' as the field separator.
sub cookie_pack
{
  my ($kind, $remote_addr, @args) = @_;
  return &base64(&compress(join("|", $kind, $remote_addr, map { &base64($_) } @args)));
}

# Extract data fields from a cookie value created with &cookie_pack().
sub cookie_unpack
{
  my ($kind, $remote_addr, @args) = split(/\|/, &uncompress(&decode_base64(shift)));
  return ($kind, $remote_addr, map { &decode_base64($_) } @args);
}

# Create a cookie response.  The arguments are the cookie type and
# cookie data as created by &cookie_pack().  The type should be 'H'
# (for 'host') or 'C' (for 'cert'), and will be used to decode the
# cookie later on.  Appends SHA1 HMAC to the cookie, and builds a
# cookie response string to be sent back to Apache.
sub make_cookie
{
  my ($type, $data) = @_;
  my $cookie = "1$type|$secret|@{[time()+3600]}|$data|";
  $cookie .= &base64(&hmac_sha1($cookie, $secrets{$secret}));
  return "cms-auth=$cookie;path=/;secure;httponly";
}

# Verify that a certificate belongs to a CMS member.
sub cert_is_cms
{
  my ($r, $newauth, $subject_dn) = @_;
  if (! $subject_dn)
  {
    return (0, $subject_dn);
  }
  elsif (exists $vocms{$subject_dn})
  {
    $r->log->notice("[cookie-auth/$$] accepting full certificate"
		    . " authentication '$subject_dn'")
      if $newauth;
    return (1, $subject_dn);
  }
  elsif (($subject_dn =~ m{(.*?)/CN=\d+$}o && exists $vocms{$1})
	 || ($subject_dn =~ m{(.*?)(?:/CN=proxy)+$}o && exists $vocms{$1}))
  {
    $r->log->notice("[cookie-auth/$$] accepting proxy certificate"
		    . " authentication '$subject_dn'")
      if $newauth;
    return (1, $1);
  }
  else
  {
    $r->log->notice("[cookie-auth/$$] rejecting non-cms certificate"
		    . " authentication '$subject_dn'");
    return (0, $subject_dn);
  }
}

######################################################################
# Check host authentication cookie.
sub host_validate_cookie
{
  my ($r, $auth_host) = @_;
  my $remote_addr = $r->connection->remote_addr->ip_get;
  my $user_agent = $r->headers_in->get("User-agent") || '';
  my %cookies = &parse_cookies($r->headers_in->get("Cookie"));
  my $data = &cookie_pack('host', $remote_addr, $user_agent, $auth_host);
  my $info = { AUTH_HOST => "$remote_addr $auth_host", AUTH_INFO => $data };
  my $status = "FAIL";

  if (! exists $cookies{'cms-auth'} || $cookies{'cms-auth'} eq '')
  {
    $r->log->notice("[cookie-auth/$$] accepting host authentication"
		    . " '$auth_host'");
    $$info{COOKIE} = &make_cookie('H', $data);
    $status = "OK";
  }
  elsif ($cookies{'cms-auth'} =~ /^(1H\|([A-Z\d]+)\|(\d+)\|([^|]+)\|)([^|]+)$/)
  {
    my $now = time();
    my $refsecret = $2;
    my $refuntil = $3;
    my $refdata = $4;
    my $refhmac = $5;
    my $hmac = &base64(&hmac_sha1($1, $secrets{$refsecret} || $secret));
    if (! exists $secrets{$refsecret})
    {
      $r->log->warn("[cookie-auth/$$] host cookie from $remote_addr/$auth_host"
		    . " uses invalid verification key '$refsecret', forcing"
		    . " reset to a new cookie");
      $r->log->notice("[cookie-auth/$$] accepting host authentication"
		      . " '$auth_host'");
      $$info{COOKIE} = &make_cookie('H', $data);
      $status = "OK";
    }
    elsif ($hmac ne $refhmac)
    {
      $r->log->warn("[cookie-auth/$$] host cookie from $remote_addr/$auth_host"
		    . " was tampered with; hmac was '$refhmac' but should be"
		    . " '$hmac'; cookie was '$cookies{'cms-auth'}'");
      $status = "FAIL";
    }
    elsif ($data ne $refdata)
    {
      $r->log->notice("[cookie-auth/$$] host cookie from $remote_addr/$auth_host"
		      . " does not match current access, forcing reset to a new"
		      . " cookie; data was '$refdata' but should be '$data';"
		      . " cookie was '$cookies{'cms-auth'}'");
      $r->log->notice("[cookie-auth/$$] accepting host authentication '$auth_host'");
      $$info{COOKIE} = &make_cookie('H', $data);
      $status = "OK";
    }
    elsif (int($refuntil) <= $now)
    {
      $r->log->notice("[cookie-auth/$$] host cookie from $remote_addr/$auth_host"
		      . " has expired ($refuntil vs. $now), renewing cookie");
      $r->log->notice("[cookie-auth/$$] accepting host authentication"
		      . " '$auth_host'");
      $$info{COOKIE} = &make_cookie('H', $data);
      $status = "OK";
    }
    else
    {
      $$info{AUTH_INFO} = $refdata;
      $status = "OK";
    }
  }
  else
  {
    $r->log->warn("[cookie-auth/$$] cms-auth cookie from $remote_addr/$auth_host"
		  . " is not a host cookie, forcing cookie reset; cookie was"
		  . " '$cookies{'cms-auth'}'");
    $$info{COOKIE} = $NULL_COOKIE;
    $status = "RETRY";
  }

  return ($status, $info);
}

######################################################################
# Check certificate authentication.
sub cert_validate_cookie
{
  my $r = shift;
  my $remote_addr = $r->connection->remote_addr->ip_get;
  my $user_agent = $r->headers_in->get("User-agent") || '';
  my %cookies = &parse_cookies($r->headers_in->get("Cookie"));
  my $info = { CERT_SUBJ => "", AUTH_INFO => "" };
  my $status = "FAIL";

  if (! exists $cookies{'cms-auth'} || $cookies{'cms-auth'} eq '')
  {
    $status = "VERIFY";
  }
  elsif ($cookies{'cms-auth'} =~ /^(1C\|([A-Z\d]+)\|(\d+)\|([^|]+)\|)([^|]+)$/)
  {
    my $now = time();
    my $refsecret = $2;
    my $refuntil = $3;
    my $refdata = $4;
    my $refhmac = $5;
    my $hmac = &base64(&hmac_sha1($1, $secrets{$refsecret} || $secret));
    if (! exists $secrets{$refsecret})
    {
      $r->log->warn("[cookie-auth/$$] cert cookie from $remote_addr uses"
		    . " invalid verification key '$refsecret', forcing"
		    . " full client verification");
      $status = "VERIFY";
    }
    elsif ($hmac ne $refhmac)
    {
      $r->log->warn("[cookie-auth/$$] cert cookie from $remote_addr was"
		    . " tampered with; hmac was '$refhmac' but should be"
		    . " '$hmac';  cookie was '$cookies{'cms-auth'}'");
      $$info{COOKIE} = $NULL_COOKIE;
      $status = "FAIL";
    }
    elsif (int($refuntil) <= $now)
    {
      $r->log->warn("[cookie-auth/$$] cert cookie from $remote_addr has"
		    . " expired  ($refuntil vs. $now), forcing full client"
		    . " verification");
      $status = "VERIFY";
    }
    else
    {
      my ($iscms, $subject_dn) = &cert_is_cms($r, 0, (&cookie_unpack($refdata))[3]);
      if (! $iscms)
      {
        $r->log->warn("[cookie-auth/$$] valid cookie has subject '$subject_dn'"
                      . " but there is no such CMS VO member, rejecting"
                      . " cookie");
        $status = "VERIFY";
      }
      else
      {
        $$info{CERT_SUBJ} = $subject_dn;
        $$info{AUTH_INFO} = $refdata;
        $status = "OK";
      }
    }
  }
  else
  {
    $r->log->warn("[cookie-auth/$$] cms-auth cookie from $remote_addr is not"
		  . " a cert cookie, forcing cookie reset; cookie was"
		  . " '$cookies{'cms-auth'}'");
    $$info{COOKIE} = $NULL_COOKIE;
    $status = "RETRY";
  }

  return ($status, $info);
}

######################################################################
# Per-server initialisation.  Set up cookie verification keys and list
# of hosts exempted from authentication.
sub init
{
  my $r = shift;

  # Read in cookie verification keys.
  foreach my $f (map { @{[<$_/*>]} } $r->dir_config->get("AUTH_COOKIE_KEYS"))
  {
    local $/ = undef;
    my $fname = $f; $fname =~ s|.*/||;
    if (! exists $secrets{$fname})
    {
      open(X, "< $f") or die "$f: $!\n";
      $secrets{$fname} = <X>;
      close(X);
    }
  }

  # Make sure we have keys to work with.  Use the last key.
  if (! keys %secrets)
  {
    $r->log->error("[cookie-auth/$$] no cookie verification keys, please"
		   . " create at least one key with update-cookie-keys,"
		   . " then restart with AUTH_COOKIE_KEYS correctly set");
    die;
  }
  else
  {
    $secret = (sort { $b cmp $a } keys %secrets)[0];
  }

  # Read in host exemption lists.  To generate the host map, use:
  #  : > local-dqm-map.txt
  #  for x in `seq 0 9`; do for y in `seq 0 9`; do
  #    host cmscc$x$y.cern.ch | grep 'has address' | awk '{print $NF, $1}';
  #  done; done >> local-dqm-map.txt
  #  for x in `seq 1 5`; do
  #    host cmsbox$x.desy.de | grep 'has address' | awk '{print $NF, $1}';
  #  done >> local-dqm-map.txt
  foreach my $f ($r->dir_config->get("AUTH_CMS_CENTRE_HOSTS"))
  {
    if (! open(F, "< $f"))
    {
      $r->log->error("[cookie-auth/$$] AUTH_CMS_CENTRE_HOSTS $f: $!");
      die;
    }

    while (<F>)
    {
      chomp; s/\#.*//; s/^\s+//; s/\s+$//;
      next if /^$/;
      @items = split(/\s+/);
      if (scalar @items != 2)
      {
        $r->log->error("[cookie-auth/$$] $f:$.: line not understood");
        die;
      }
      $host_exempt{$items[0]} = $items[1];
    }
    close(F);
  }

  # Read VO member definitions.
  foreach my $f ($r->dir_config->get("AUTH_GRID_MAPS"))
  {
    if (! open(F, "< $f"))
    {
      $r->log->error("[cookie-auth/$$] AUTH_GRID_MAPS $f: $!");
      die;
    }

    while (<F>)
    {
      chomp; s/^\s+//; s/\s+$//;
      if (/"(.*)" ([a-z]+)$/)
      {
        $vocms{$1} = 1 if $2 eq 'cms';
      }
      elsif (! /^$/)
      {
        $r->log->error("[cookie-auth/$$] $f:$.: line not understood");
        die;
      }
    }

    close(F);
  }

  if (! scalar %vocms)
  {
    $r->log->error("[cookie-auth/$$] no CMS VO members found in AUTH_GRID_MAPS");
    die;
  }

  # Mark initialisation complete.
  $initialised = 1;
}

######################################################################
sub handler
{
  my $r = shift;

  # Only permit authentication in HTTPS mode.  This ought to be caught
  # earlier on in server configuration, make last resort check here.
  return &auth_fail($r, "authentication denied without https")
    if ! $r->connection->is_https();

  # Initialise on first request.
  &init($r) if ! $initialised;

  # Force removal of security verification related headers.  Again this
  # prevents the incoming request from setting headers we send to back-
  # end applications and proxies.  Later we only set relevant ones, for
  # example CMS-Auth-Host will only be set if host-based authentication
  # was applied to the request.  The headers are as follows:
  #
  #  CMS-Auth-Status   Presence of this header indicates the request came
  #                    over SSL and was successfully authenticated.  The
  #                    value is always "OK".  The actual authentication
  #                    details are included in other CMS-Auth-* headers.
  #                    This header is purely informative, the front-end
  #                    server never proxies requests unauthenticated.
  #
  #  CMS-Auth-Info     Present with CMS-Auth-Status and contains generic
  #                    authentication information token.  Backends can
  #                    use this as an opaque identifier of the identity
  #                    if they don't need any authorisation.
  #
  #  CMS-Auth-Host     Present with CMS-Auth-Status if the request came
  #                    from an address on the authentication exemption
  #                    list.  No user-based authentication was used.
  #
  #  CMS-Auth-Cert     Present with CMS-Auth-Status if the request was
  #                    authenticated using a verified client certificate.
  #
  #  CMS-Client-CERT   Present with CMS-Auth-Cert, contains certificate.
  #  CMS-Client-S-DN   Present with CMS-Auth-Cert, contains subject DN.
  #
  # The "cmsdaq1.cern.ch" reverse proxy between CERN GPN and P5 network
  # looks for CMS-Auth-Status coming from this server, and will only
  # permit the relay to P5 network if the value is correctly set.
  $r->headers_in->unset("CMS-Auth-Status");
  $r->headers_in->unset("CMS-Auth-Info");
  $r->headers_in->unset("CMS-Auth-Host");
  $r->headers_in->unset("CMS-Auth-Cert");
  $r->headers_in->unset("CMS-Client-CERT");
  $r->headers_in->unset("CMS-Client-S-DN");

  # Make sure authentication-related environment variables are unset.
  #   AUTH_NEXT      Authentication methods left to evaluate.
  #   AUTH_COMPLETE  Used for internal processing to indicate completion.
  $r->subprocess_env->unset("AUTH_NEXT");
  $r->subprocess_env->unset("AUTH_COMPLETE");

  # Process the request.
  if ($r->uri eq '/auth/cert-verify')
  {
    # Do nothing, all the work has already been in done in mod_ssl.
    # This is used internally by &auth_cert_cookie() to get SSL side
    # effects ("SSLClientVerify optional" => environment variables).
    return Apache2::Const::OK;
  }
  else
  {
    return &auth_step($r);
  }
}

# Internal utility function to fail the request.
sub auth_fail 
{
  my ($r, $reason) = @_;
  my $ir = &initialreq($r);
  $r->log->warn("[cookie-auth/$$] $reason; forbidding @{[$ir->unparsed_uri]}");
  $r->uri($ir->unparsed_uri);
  $r->status(Apache2::Const::FORBIDDEN);
  return Apache2::Const::FORBIDDEN;
}

# Internal utility to go to the next stage of authentication.
sub auth_step
{
  my $r = shift;
  my $ir = &initialreq($r);

  # Only allow this authentication to be used during internal rewriting.
  return &auth_fail($r, "auth_step not invoked from internal redirection")
    if ! defined $ir->subprocess_env('AUTH_NEXT');

  # Extract and update next and remaining authentication methods.
  my ($next, @rest) = split(/;/, $ir->subprocess_env('AUTH_NEXT') || 'fail');
  $ir->subprocess_env('AUTH_NEXT' => join(';', @rest));

  # Now process this authentication step.
  if (! $next)
  {
    return &auth_fail($r, "auth_step: no more authentication steps");
  }
  elsif ($next eq 'host')
  {
    return &auth_host($r);
  }
  elsif ($next eq 'cert-cookie')
  {
    return &auth_cert($r);
  }
  elsif ($next eq 'fail')
  {
    return &auth_fail($r, "auth_step: no more authentication methods left");
  }
  else
  {
    return &auth_fail($r, "auth_step: unrecognised next step '$next'");
  }
}

# Authentication routine for host-based authentication.
sub auth_host
{
  my $r = shift;
  my $ir = &initialreq($r);

  # Check if the remote host is in the exemption map.
  my $host = $host_exempt{$r->connection->remote_addr->ip_get};

  # If not in the list of exempted hosts, pass to the next authentication stage.
  # After this we assume the access will succeed, or there was a gross failure.
  return &auth_step($r) if ! $host;

  # Add request headers and cookie for the authentication status.
  my ($status, $data) = &host_validate_cookie($r, $host);

  if ($$data{COOKIE})
  {
    my $oldcookie = $r->headers_in->get("Cookie");
    $r->err_headers_out->add("Set-Cookie" => $$data{COOKIE});
    $r->headers_in->set("Cookie" => $$data{COOKIE} . ($oldcookie ? "; $oldcookie" : ""));
  }

  if ($status eq 'RETRY')
  {
    $r->log->notice("[cookie-auth/$$] retry: redirecting to @{[$ir->unparsed_uri]}");
    $r->uri($ir->unparsed_uri);
    $r->status(Apache2::Const::REDIRECT);
    return Apache2::Const::REDIRECT;
  }
  elsif ($status eq 'OK')
  {
    $r->headers_in->set("CMS-Auth-Status" => "OK");
    $r->headers_in->set("CMS-Auth-Info" => $$data{AUTH_INFO});
    $r->headers_in->set("CMS-Auth-Host" => $$data{AUTH_HOST});
    $r->subprocess_env->set("AUTH_COMPLETE" => "OK");
    $r->internal_redirect($ir->unparsed_uri);
    return Apache2::Const::OK;
  }
  else
  {
    return &auth_fail($r, "auth_host: failing due to status '$status'");
  }
}

# Authentication routine for client certificate.  This one has a fast
# path when there is already a valid cookie recording the certificate
# details.  Otherwise it falls back on full client certificate verify.
sub auth_cert
{
  my $r = shift;
  my $ir = &initialreq($r);

  # Check if we have a valid cookie.  Note that we don't have or use SSL yet.
  my ($status, $data) = &cert_validate_cookie($r);
  if ($status eq 'RETRY')
  {
    $r->log->notice("[cookie-auth/$$] retry: redirecting to @{[$ir->unparsed_uri]}");
    $r->err_headers_out->add("Set-Cookie" => $$data{COOKIE});
    $r->uri($ir->unparsed_uri);
    $r->status(Apache2::Const::REDIRECT);
    return Apache2::Const::REDIRECT;
  }
  elsif ($status eq 'VERIFY')
  {
    my $iscms;
    my $subreq = $r->lookup_uri('/auth/cert-verify');
    my $verify = $subreq->subprocess_env->get('SSL_CLIENT_VERIFY');
    my $cert_data = $subreq->subprocess_env->get('SSL_CLIENT_CERT');
    my $subject_dn = $subreq->subprocess_env->get('SSL_CLIENT_S_DN');
    my $vremain = $subreq->subprocess_env->get('SSL_CLIENT_V_REMAIN');
    my $vstart = $subreq->subprocess_env->get('SSL_CLIENT_V_START');
    my $vend = $subreq->subprocess_env->get('SSL_CLIENT_V_END');
    my $vstatus = $subreq->status();

    # The following is merely to produce better error reports on cert
    # validation, with no change of result. First report gross errors.
    if ($vstatus != Apache2::Const::HTTP_OK || ! $subject_dn)
    {
      $r->log->notice("[cookie-auth/$$] missing required certificate,"
		      ." status $vstatus, verify $verify");
      return &auth_step($r);
    }

    # Report failure if we don't find expected DN structure.
    if ($subject_dn !~ m|/CN=|o)
    {
      $r->log->notice("[cookie-auth/$$] rejecting unexpected certificate"
		      ." $subject_dn, verify $verify, vstart $vstart,"
		      ." vend $vend, vremain $vremain");
      return &auth_step($r);
    }

    # Report failure if the certificate has expired.
    if (! ($vremain > 0))
    {
      $r->log->notice("[cookie-auth/$$] rejecting expired certificate"
		      ." $subject_dn, verify $verify, vstart $vstart,"
		      ." vend $vend, vremain $vremain");
      return &auth_step($r);
    }

    # Report any other failure.
    elsif ($verify ne 'SUCCESS')
    {
      $r->log->notice("[cookie-auth/$$] rejecting invalid certificate"
		      ." $subject_dn, verify $verify, vstart $vstart,"
		      ." vend $vend, vremain $vremain");
      return &auth_step($r);
    }

    # Certificate is valid. Now check it belongs to our VO.
    ($iscms, $subject_dn) = &cert_is_cms($r, 1, $subject_dn);
    return &auth_step($r) if ! $iscms;

    # We accepted it, prepare cookie from the cert data.
    my $remote_addr = $r->connection->remote_addr->ip_get;
    my $user_agent = $r->headers_in->get("User-agent") || '';
    my $cdata = &cookie_pack('cert', $remote_addr, $user_agent, $subject_dn);
    $data = { CERT_DATA => $cert_data, CERT_SUBJ => $subject_dn,
	      AUTH_INFO => $cdata, COOKIE => &make_cookie('C', $cdata) };
    $$data{CERT_DATA} =~ s/\n/ /gs; # FIXME: URL encode?
    $$data{CERT_SUBJ} =~ s/\n/ /gs; # FIXME: URL encode?
    $status = "OK";
  }

  if ($$data{COOKIE})
  {
    my $oldcookie = $r->headers_in->get("Cookie");
    $r->err_headers_out->add("Set-Cookie" => $$data{COOKIE});
    $r->headers_in->set("Cookie" => $$data{COOKIE} . ($oldcookie ? "; $oldcookie" : ""));
  }

  if ($status eq 'OK')
  {
    $r->headers_in->set("CMS-Auth-Status" => "OK");
    $r->headers_in->set("CMS-Auth-Info" => $$data{AUTH_INFO});
    $r->headers_in->set("CMS-Auth-Cert" => $$data{CERT_SUBJ});
    $r->headers_in->set("CMS-Client-S-DN" => $$data{CERT_SUBJ});
    $r->headers_in->set("CMS-Client-CERT" => $$data{CERT_DATA}) if $$data{CERT_DATA};
    $r->subprocess_env->set("AUTH_COMPLETE", "OK");
    $r->internal_redirect($ir->unparsed_uri);
    return Apache2::Const::OK;
  }
  else
  {
    return &auth_fail($r, "auth_cert: failing due to status '$status'");
  }
}

######################################################################
1;
