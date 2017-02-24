#!/usr/bin/perl -w
# xurl - extract unique, sorted list of links from URL

# UBUNTU: apt-get install libwww-perl libhtml-linkextractor-perl

use HTML::LinkExtor;
use LWP::Simple;

$filename = $ARGV[0];
$baseurl = $ARGV[1] || "http://localhost";

$parser = HTML::LinkExtor->new(undef, $baseurl);
$parser->parse_file($filename);

@links = $parser->links;
foreach $linkarray (@links) {
    my @element  = @$linkarray;
    my $elt_type = shift @element;
    while (@element) {
        my ($attr_name , $attr_value) = splice(@element, 0, 2);
        $seen{$attr_value}++;
    }
}
for (sort keys %seen) { print $_, "\n" }

