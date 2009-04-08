# This Python file uses the following encoding: utf-8
import getopt, sys
from server import Server
from client import Client

name = "none"
opts, args = getopt.getopt(sys.argv[1:], "hcsn:v",
 ["help","client=","server","name="])
print args
print opts
for o, a in opts:
	if o == "-v":
		print "version: 0.5-git"
	if o in ("-h", "--help"):
		print "help you self"
	if o in ("-n", "--name"):
	 	name = a
	if o in ("-c", "--client"):
		Client(name, a)
	elif o in ("-s", "--server"):	 
		Server(name)
