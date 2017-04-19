#!/usr/bin/env perl

use warnings;
use strict;

while(<STDIN>) {
  chop;

  # avoid general madness
  s/[\000-\037]//g;
  s/\s+/ /g;
  s/(£|$|Rp)(\d+)/$1 $2/g;
  s/, "(kata|ujar|ungkap|tutur)/," $1/g;
  s/, "(\w+) (me\w+|said|told)/," $1 $2/g;
  s/ +\.$/./g;
  s/ +\.\.\./.../g;
  s/ +([,:;\.]|'[,s]) +/$1 /g;
  s/ +([\/]) +/\//g;
  s/^ //g;
  s/ $//g;

  print $_."\n";
}
