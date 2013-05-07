#!/usr/bin/env perl

=pod

=head1 NAME

WTDeployUtil.pm - WEBTOOLS configuration data/utility

=head1 DESCRIPTION

Contains WEBTOOLS server configuration data and utility functions for
determining deployment configuration parameters based on either the
host we are executing on or a given deployment tag.

Can be used either as a perl module or a standalone program.  To use
as a standalone program, do:

 perl WTDeployUtil.pm function [arguments]

Functions which return multiple values will print as a comma separated
list.

=head1 FUNCTIONS

=cut

use warnings;
use strict;

package WTDeployUtil;

use Data::Dumper;
use Sys::Hostname;

use Exporter;
our @EXPORT_OK = qw( dump my_host my_ip ip_of fqdn_of deployment
		     frontend_hosts backend_hosts frontend_ips backend_ips
		     frontend_alias );

our $boxes =
{
# See https://twiki.cern.ch/twiki/bin/viewauth/CMS/CMSVoBoxesServices#WebTools
    'LOCAL' => {
	'FRONTEND_ALIAS' => &my_host(),
	'FRONTEND_HOSTS' => [&my_host(), 'localhost'],
	'BACKEND_HOSTS'  => [&my_host(), 'localhost'] 
	},
    'DEVEL' => { 
	'FRONTEND_ALIAS' => 'cmswttest',
	'FRONTEND_HOSTS' => [qw(vocms109 localhost)],
	'BACKEND_HOSTS'  => [qw(vocms109 localhost)] 
	},
    'PREPROD' => { 
	'FRONTEND_ALIAS' => 'cmsweb-testbed',
	'FRONTEND_HOSTS' => [qw(vocms108)],
	'BACKEND_HOSTS'  => [qw(vocms51)] 
	},
    'PROD' => { 
	'FRONTEND_ALIAS' => 'cmsweb',
	'FRONTEND_HOSTS' => [qw(vocms65 vocms105)],
	'BACKEND_HOSTS'  => [qw(vocms106 vocms107 vocms50 vocms53)] 
	}
};

# turn host names into fully qualified domain names
foreach my $dep (values %$boxes) {
    foreach my $var (qw(FRONTEND_ALIAS FRONTEND_HOSTS BACKEND_HOSTS)) {
	if (! ref $dep->{$var}) { # scalar
	    $dep->{$var} = &fqdn_of($dep->{$var});
	} elsif (ref $dep->{$var} eq 'ARRAY') { # array
	    $dep->{$var} = [ map { &fqdn_of($_) } @{$dep->{$var}} ];
	}
    }
}

=pod

=over

=item dump

Dumps the configuration data defined by this module.

=back

=cut
sub dump 
{
    return Dumper($boxes);
}


=pod

=over

=item my_host

Returns the host name we are on now.

=back

=cut
sub my_host
{
   my $host = hostname();
   chomp $host;
   die "the hostname of this machine could not be found!" unless $host;
   return $host;
}

=pod

=over

=item my_ip

Returns the IP of the host we are on now.

=back

=cut
sub my_ip { return &ip_of(&my_host()); }

=pod

=over

=item ip_of [host]

Returns the IP of the given host name.  Default is my_host.

=back

=cut
sub ip_of
{
    my $host = shift || &my_host();
    my $ip = `host $host`;
    chomp $ip;
    $ip =~ s/\S+ has address ([0-9.]+).*/$1/s;
    return $ip;
}

=pod

=over

=item fqdn_of [host]

Returns the fully qualified domain name of the given local network
host name.  Default is my_host.

=back

=cut
sub fqdn_of
{
    my $host = shift || &my_host();
    $host = `host $host`;
    chomp $host;
    $host =~ s/^(\S+) .*/$1/s;
    return $host;
}

=pod

=over

=item deployment [host]

Attempts to lookup the deployment based on the host we are running on
now, or the given host if one is provided.  If no deployment is found,
defaults to "LOCAL".

=back

=cut
sub deployment
{
    my $host = shift || &my_host();
    foreach my $dep (keys %$boxes) {
	foreach my $end (qw(FRONTEND_HOSTS BACKEND_HOSTS)) {
	    my @hosts = @{$boxes->{$dep}->{$end}};
	    return $dep if grep ( $host =~ /^$_/, @hosts );
	}
    }
    # if we didn't find a deployment specification, use "LOCAL"
    return 'LOCAL';
}

=pod

=over

=item frontend_hosts [deployment]

=item backend_hosts  [deployment]

Returns the hostnames of the front/backends based on a deployment.  If
no deployment is given, defaults to the one looked up by "deployment".

=back

=cut
# define &frontend_hosts and &backend_hosts
foreach my $end (qw(frontend backend)) {
    no strict 'refs';
    my $name = $end.'_hosts';
    *$name = sub {
	my $dep = shift || &deployment();
	return @{$boxes->{uc $dep}->{uc $end.'_HOSTS'}};
    }
}

=pod

=over

=item frontend_ips [deployment]

=item backend_ips  [deployment]

Returns the ip addresses of the front/backends based on a deployment.  If
no deployment is given, defaults to the one looked up by "deployment".

=back

=cut
# define &frontend_ips and &backend_ips
foreach my $end (qw(frontend backend)) {
    no strict 'refs';
    my $name = $end.'_ips';
    *$name = sub
    {
	my $dep = shift || &deployment();
	my @hosts = &{"${end}_hosts"}($dep);
	return  map { &ip_of($_) } @hosts;
    }
}

=pod

=over

=item frontend_alias [deployment]

Returns the frontend alias based on the deployment.  If no deployment
is given, defaults to the one looked up by "deployment".

=back

=cut
sub frontend_alias
{
    my $dep = shift || &deployment();
    return $boxes->{$dep}->{FRONTEND_ALIAS};
}

=pod

=over

=item list

Lists the functions supplied by this module.  (for command-line use)

=back

=over

=item help

Prints help.

=back

=cut

# code to run if called from the command-line
sub runme
{
    my ($func, @args) = @ARGV;
	
    $func ||= 'help';
    if ($func eq 'list') {
	print join("\n  ", "Available functions:", @WTDeployUtil::EXPORT_OK), "\n";
	exit(0);
    } elsif ($func eq 'help') {
	exec("perldoc $0");
    }
	
    no strict 'refs';
    die "$func is not a recognized function" unless exists ${"WTDeployUtil::"}{$func};
    print join(',', &{"WTDeployUtil::$func"}(@args)), "\n";
}

&runme() unless caller;

1;
