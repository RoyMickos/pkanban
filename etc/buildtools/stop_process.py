# stops a given process with pid given as input from command line

import subprocess, sys, os

if len(sys.argv) != 2:
    print "Usage: stop_process pidfile"
else:
    pidfile = open(sys.argv[1],'r')
    pid = pidfile.read()
    # dummy assigment to verify format, will create an exeption if content is corrupted
    pidinteger = int(pid)
    print "Killing process: %d" % pidinteger
    os.remove(sys.argv[1])
    sys.exit(subprocess.call(['kill', pid]))
