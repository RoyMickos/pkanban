# simple utility that starts a process and records pid so that another
# utility can kill that process later. 

usage = """
start_process recordfile command
  recordfile: this is used to create recordfile.pid to store process id
  command:    the command that is used to start the process
see documentation for subprocess module in python docs
"""

#TODO: add stdout redirection to a file

import subprocess, sys

if len(sys.argv) < 3:
    print usage
else:
    pidfile = open(sys.argv[1] + ".pid", 'w')
    process = subprocess.Popen(sys.argv[2:])
    # process.pid holds the pid of the started process, but terminating the program
    # leaves python runninf with a pid+1. Killing that will kill the started program as well
    pidfile.write(str(process.pid + 1))
sys.exit(0)
