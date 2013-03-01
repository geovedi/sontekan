#!/usr/bin/perl

# HINTS:
# - Clue: "Songs for the disgruntled postman" -> SMTP (25/tcp)
# - extract tcp payload on port 4312->23 ...find the secret key in md5
# - extract tcp payload on port 4313->25 ...encryped stored here!
# - http://ezine.echo.or.id/ezine11/echo11-009.txt

use strict;
use warnings;
use MIME::Base64;

printf "[+] ctf.echo.or.id -- level 6" . "\n";

# generating username & password
my $range = 10;
my $username = crypt(int(rand($range)),"ctf"); 
my $password = crypt(int(rand($range)),"level6");

# generating secret key
my $secret_key = `/bin/date | /usr/bin/openssl md5`;
printf "Secret key:\t" . $secret_key;

# generating access message
my $message = "u: $username p: $password";
printf "Message:\t" . $message . "\n";

# encrypting message -> ascii 
my $encrypted_message = `/bin/echo '$message' | /usr/bin/openssl enc -bf-cbc -a -in /dev/stdin -pass pass:$secret_key`;

# generating garbage
my $half = 4096 / 2;
my @chars = (qw(% $ ! @ ^ & * ( ) - = + [ ] { } : < > ? / . ~ | ));
my $garbage = join("", @chars[ map { rand @chars } ( 1 .. 4096 ) ]);
$garbage =~ s/(.{$half})(.{$half})/$1 $secret_key $2/;
$garbage = encode_base64($garbage);

# let's do it!
my $clue = "Songs for the disgruntled postman";
open(STREAM_PT1, '>stream_pt1.txt');
printf STREAM_PT1 $clue . "\n";
printf STREAM_PT1 $garbage . "\n";
close(STREAM_PT1);

open(STREAM_PT2, '>stream_pt2.txt');
printf STREAM_PT2 $encrypted_message;
close(STREAM_PT2);

system('/usr/bin/od -Ax -tx1 stream_pt1.txt | /usr/bin/text2pcap -T4312,23 - stream_pt1.pcap 2>/dev/null');
system('/usr/bin/od -Ax -tx1 stream_pt2.txt | /usr/bin/text2pcap -T4313,25 - stream_pt2.pcap 2>/dev/null');
system('/usr/bin/mergecap -w stream_pt1,2.pcap stream_pt1.pcap stream_pt2.pcap 2>/dev/null');

# XXX: regression test

# analysing the payload (emulate manual actions)
# [1] key
system('/usr/sbin/tcpdump -n -w key.pcap -r stream_pt1,2.pcap "dst port 23" 2>/dev/null');
system('/usr/bin/strings key.pcap | /usr/bin/tail -73 | /usr/bin/openssl base64 -d -out key_temp.txt 2>/dev/null');
system('/usr/bin/awk "{print \$2}" < key_temp.txt > key.txt 2>/dev/null');

# [2] message
system('/usr/sbin/tcpdump -n -w message.pcap -r stream_pt1,2.pcap "dst port 25" 2>/dev/null');
my $test_message = `/usr/bin/strings message.pcap`;
open(TEST_MESSAGE, '>message.txt');
printf TEST_MESSAGE $test_message;
close(TEST_MESSAGE);

# decrypting message
my $test_decrypt = `/usr/bin/openssl enc -bf-cbc -d -a -in message.txt -kfile key.txt`;
printf "\nDecrypted:\t" . $test_decrypt . "\n";

# clean up
system('/bin/rm stream_pt1.txt stream_pt2.txt stream_pt1.pcap stream_pt2.pcap 2>/dev/null');
system('/bin/rm key.pcap message.pcap key.txt 2>/dev/null');
