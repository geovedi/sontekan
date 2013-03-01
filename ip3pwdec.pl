#!/usr/bin/perl
# $Id: ip3pwdec.pl,v 1.1 2005/03/24 21:07:46 negative Exp $
#
# IP3 NetAccess password decoder
# by negative@segfault.net
#
# Example config file:
#  ...
#  controlpanel 1 username admin password 420%448%204%388%396%396%404%460%460%
#  controlpanel 2 username shannon password 476%444%456%436%192%224%192%224%
#  controlpanel 3 username patrick password 480%448%388%464%456%420%396%428%
#  ...
#
# Run:
#  $ ip3pwdec.pl < file
#
# Credits: skyper, fygrave, gaius
#

while (<>) {
    if (/password\s([\d\d\d%]+)/) {
        $ep = $1; 
        $dp = "";
        @ch = split(/%/, $ep);
        foreach (@ch) {
            $dp .= sprintf "%s", map{chr} $_ / 4;
        }
        s/$ep/$dp/;
    }
    print;
}
